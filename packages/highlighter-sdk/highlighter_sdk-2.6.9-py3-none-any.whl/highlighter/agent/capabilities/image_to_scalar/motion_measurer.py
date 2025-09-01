import logging
from collections import deque
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union
from uuid import UUID

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms as T
from pydantic import BaseModel, model_validator

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.agent.capabilities.image_to_scalar._neuflowv2 import NeuFlowV2
from highlighter.client.base_models.annotation import Annotation
from highlighter.client.base_models.entity import Entity
from highlighter.client.base_models.observation import Observation
from highlighter.client.io import download_bytes
from highlighter.core import LabeledUUID
from highlighter.core.data_models import DataSample

__all__ = ["MotionMeasurer", "OpticalFlow", "MotionMeasurerCapability"]


DEFAULT_MODEL_PATH = Path(__file__).parent.parent / "models" / "neuflow_sintel.onnx"
DEFAULT_MODEL_URL = (
    "https://github.com/ibaiGorordo/ONNX-NeuFlowV2-Optical-Flow/releases/download/0.1.0/neuflow_sintel.onnx"
)


class OpticalFlow(BaseModel):
    """
    A standalone optical flow class that calculates a motion score
    based on optical flow between consecutive frames.

    Args:
        model_path (str): Path to the optical flow model file.
        use_gpu (bool): Whether to use GPU for preprocessing.
        blur_kernel (tuple): Size of Gaussian blur kernel for preprocessing.
    """

    model_path: Union[str, Path] = DEFAULT_MODEL_PATH
    use_gpu: bool = True
    blur_kernel: tuple = (3, 3)

    @model_validator(mode="after")
    def init(self):
        self._logger = logging.getLogger(__name__)
        self._device = "cuda" if torch.cuda.is_available() and self.use_gpu else "cpu"
        self._estimator = self._load_model()  # load the model from the model_path
        self._prev_frame = None

        # Image preprocessing transform pipeline
        self._preprocess_frame = T.Compose(
            [
                T.ToTensor(),  # Convert image to tensor
                T.ConvertImageDtype(torch.float32),  # Convert image to float32
                T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # Normalize image
            ]
        )

        self._logger.info(f"Initialized OpticalFlow on device: {self._device}")
        return self

    def _load_model(self) -> NeuFlowV2:
        """
        Load the NeuFlowV2 optical flow model.

        Returns:
            The loaded NeuFlowV2 model instance.
        """
        self.model_path = Path(self.model_path)
        default_path = Path(DEFAULT_MODEL_PATH)

        # Check if file exists and compare names safely
        if not self.model_path.exists():
            # Create directory
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            # Safe comparison using Path objects
            if self.model_path.name == default_path.name:
                self._logger.info(f"Downloading model from {DEFAULT_MODEL_URL}...")
                download_bytes(DEFAULT_MODEL_URL, save_path=self.model_path)
                self._logger.info(f"Downloaded to: {self.model_path}")
            else:
                raise FileNotFoundError(f"Model not found: {self.model_path}")

        return NeuFlowV2(self.model_path)

    def update(self, image) -> np.ndarray:
        """
        Update the algorithm with a new image and return the latest motion score.

        The motion score is calculated as the sum of the magnitudes of all optical
        flow vectors between the current image and the previous image.

        Args:
            image (numpy.ndarray): Input image (BGR format from OpenCV).

        Returns:
            np.ndarray: Flow vectors indicating the amount of motion between frames.
        """

        # Apply Gaussian blur to reduce noise
        filtered_frame = cv2.GaussianBlur(image, self.blur_kernel, 0)

        # frame_tensor is CHW
        frame_tensor = self._preprocess_frame(filtered_frame).to(self._device)

        # If this is the first frame, store it and return 0
        if self._prev_frame is None:
            self._prev_frame = frame_tensor
            h, w = frame_tensor.shape[1:]
            return np.zeros((h, w, 2), dtype=np.float32)

        # Convert tensors back to numpy for OpticalFlow estimation
        # convert from CHW back to HWC
        prev_frame_np = (self._prev_frame.cpu().permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)

        curr_frame_np = (frame_tensor.cpu().permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)

        # Calculate optical flow
        flow_vectors = self._estimator(prev_frame_np, curr_frame_np)

        # Store current frame for next comparison
        self._prev_frame = frame_tensor

        return flow_vectors

    def reset(self):
        """
        Reset the optical flow state.
        """
        self._prev_frame = None

    @staticmethod
    def draw_flow(curr_frame, flow, step=10) -> np.ndarray:
        # Create a copy of the frame for overlay
        frame_with_flow = curr_frame.copy()

        # Sample flow vectors on a grid
        h, w = flow.shape[:2]
        y, x = np.mgrid[step // 2 : h : step, step // 2 : w : step].reshape(2, -1).astype(int)
        fx, fy = flow[y, x].T

        # Create lines for visualization (start and end points)
        lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
        lines = lines.astype(np.int32)

        # Compute magnitude and angle for color coding
        mag, ang = cv2.cartToPolar(fx, fy)
        mag = np.clip(mag, 0, 20)  # Cap magnitude for visualization
        ang = ang * 180 / np.pi  # Convert to degrees

        # Draw flow vectors as colored lines
        for (x1, y1), (x2, y2), m, a in zip(lines[:, 0], lines[:, 1], mag, ang):
            # Color based on angle (hue) and magnitude (brightness)
            hsv = np.zeros((1, 1, 3), dtype=np.uint8)
            hsv[0, 0, 0] = (a / 2)[0]  # Hue from angle
            hsv[0, 0, 1] = 255  # Full saturation
            hsv[0, 0, 2] = int((255 * m / 20)[0])  # Value from magnitude
            color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
            cv2.line(frame_with_flow, (x1, y1), (x2, y2), color.tolist(), 4)
            cv2.circle(frame_with_flow, (x2, y2), 1, color.tolist(), -1)

        return frame_with_flow


class MotionMeasurer(BaseModel):
    """
    Compute motion measurement from video frames via an underlying OpticalFlow model.

    On instantiation, sets up:
      • an OpticalFlow instance to compute per-frame flow vectors
      • a set of MovingAverage buffers for each requested score type
      • internal history buffers and frame-index tracking

    Usage:
        mm = MotionMeasurer(score_type=["mean","median"], window_size=10)
        for idx, frame in enumerate(frame_generator):
            scores = mm.update(frame, idx)
            # {'mean': 0.23, 'median': 0.19}
    """

    score_type: List[Literal["sum", "mean", "median"]] = ["mean"]
    window_size: int = 20
    history_size: int = 40

    # OpticalFlow Args
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH
    use_gpu: bool = True
    blur_kernel: tuple = (3, 3)

    @model_validator(mode="after")
    def init(self):
        self._optical_flow_model = OpticalFlow(
            model_path=self.model_path,
            use_gpu=self.use_gpu,
            blur_kernel=self.blur_kernel,
        )

        self._score_names = ["sum", "mean", "median"]
        self._score_idxs = [self._score_names.index(a) for a in self.score_type]
        self._motion_averages = {
            self._score_names[i]: MovingAverage(self.window_size) for i in self._score_idxs
        }
        self._frame_idxs = deque(maxlen=self.history_size)
        self._motion_averages_history = {
            self._score_names[i]: deque(maxlen=self.history_size) for i in self._score_idxs
        }
        self._flow_vectors = None
        return self

    def _update_motion_scores(self, flow_vectors: np.ndarray):
        u, v = flow_vectors[..., 0], flow_vectors[..., 1]
        magnitude = np.sqrt(u**2 + v**2)
        motion_scores = (
            float(np.sum(magnitude)),
            float(np.mean(magnitude)),
            float(np.median(magnitude)),
        )

        for i in self._score_idxs:
            self._motion_averages[self._score_names[i]].update(motion_scores[i])

        for k, v in self._motion_averages.items():
            self._motion_averages_history[k].append(v.get_average())

    def get_latest_flow_vectors(self):
        return self._flow_vectors

    def update(self, image: np.ndarray, frame_idx: int) -> Dict[str, float]:
        """
        Process a new video frame and update the running motion statistics.

        This method will:
          1. Append the provided frame index to the internal list of seen frames.
          2. Compute the optical flow between the last frame and the current one.
          3. Update the configured moving averages (sum, mean, median) over the specified window.
          4. Record the latest averaged values in history and return the most recent values.

        Parameters
        ----------
        image : np.ndarray
            The current video frame as a H×W×C NumPy array (in BGR or RGB format
            matching what your OpticalFlow implementation expects).
        frame_idx : int
            The absolute index of this frame in the input sequence (used for x-axis
            labeling in a visualisation and any index-based calculations).

        Returns
        -------
        Dict[str, float]
            A mapping from each requested score name (e.g. `"mean"`, `"median"`) to
            its most recent moving‐average value after processing this frame.

        Example
        -------
        >>> mm = MotionMeasurer(score_type=["mean", "sum"], window_size=5)
        >>> for idx, frame in enumerate(video_frames):
        ...     scores = mm.update(frame, idx)
        ...     # scores might be {"mean": 0.12, "sum": 3456.0}
        """
        self._frame_idxs.append(frame_idx)
        flow_vectors = self._optical_flow_model.update(image)
        self._flow_vectors = flow_vectors

        self._update_motion_scores(flow_vectors)

        return {k: v[-1] for k, v in self._motion_averages_history.items()}

    def get_motion_score_fig(self, select: Optional[List[str]] = None, width: int = 600, height: int = 550):
        plt.style.use("dark_background")

        if select is None:
            select = list(self._motion_averages.keys())

        assert all([s in self._motion_averages for s in select])

        # Create 3 subplots
        fig, axies = plt.subplots(len(select), 1, figsize=(width / 100, height / 100), dpi=100)
        if not isinstance(axies, np.ndarray):
            axies = [axies]

        plot_colors = {
            "sum": "#00BFFF",
            "mean": "#00FF7F",
            "median": "#FFD700",
        }
        plot_colors = {k: v for k, v in plot_colors.items() if k in select}

        for i, (key, color) in enumerate(plot_colors.items()):
            ax = axies[i]
            scores = self._motion_averages_history[key]

            ax.plot(self._frame_idxs, scores, color=color, linewidth=2, alpha=0.9)
            ax.fill_between(self._frame_idxs, scores, alpha=0.3, color=color)

            ax.set_title(
                f"Movement Score ({key.title()})",
                fontsize=20,
                color="white",
                fontweight="bold",
            )
            ax.set_ylabel(key.title(), fontsize=20, color="white")
            ax.grid(True, alpha=0.4, color="gray", linestyle="-", linewidth=0.8)
            ax.set_facecolor("black")
            ax.tick_params(colors="white", labelsize=20)

        axies[-1].set_xlabel("Frame", fontsize=7, color="white")

        fig.patch.set_facecolor("black")
        fig.patch.set_alpha(0.9)
        plt.tight_layout()
        return fig


class MovingAverage:
    def __init__(self, window_size):
        if window_size <= 0:
            raise ValueError("Window size must be positive")
        self.window_size = window_size
        self.values = []
        self.sum = 0.0

    def update(self, value):
        self.values.append(value)
        self.sum += value

        # If window is exceeded, remove oldest value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)

        return self.get_average()

    def get_average(self):
        if not self.values:
            return 0.0
        return self.sum / len(self.values)


class MotionMeasurerCapability(Capability):
    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        attribute_id: UUID
        entity_id: UUID
        object_class_id: UUID
        score_type: Literal["mean", "sum", "median"] = "mean"
        crop: Optional[Tuple[float, float, float, float]] = None
        window_size: int = 10

    def __init__(self, context):
        context.get_implementation("PipelineElement").__init__(self, context)

        # FIXME: make sure DefaultStreamParameters are set at __init__ time, not
        # just at start_stream time
        self.score_type, _ = self.get_parameter("score_type")
        attribute_id, _ = self.get_parameter("attribute_id")
        self.attribute_id = LabeledUUID.from_str(f"{attribute_id}|motion_score_{self.score_type}")
        self.entity_id = UUID(self.get_parameter("entity_id")[0])
        self.entity = Entity(id=self.entity_id)
        object_class_id, _ = self.get_parameter("object_class_id")
        if "|" in object_class_id:
            self.object_class_id = LabeledUUID.from_str(object_class_id)
        else:
            self.object_class_id = LabeledUUID.from_str(f"{object_class_id}|-")

        kwargs = {"score_type": [self.score_type]}
        model_path, _ = self.get_parameter("model_path", use_pipeline=True)
        kwargs["model_path"] = model_path
        use_gpu, _ = self.get_parameter("use_gpu", use_pipeline=True)
        kwargs["use_gpu"] = use_gpu
        blur_kernel, _ = self.get_parameter("blur_kernel", use_pipeline=True)
        kwargs["blur_kernel"] = blur_kernel
        window_size, _ = self.get_parameter("window_size", default=20)
        kwargs["window_size"] = window_size
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self._motion_score_model = MotionMeasurer(**kwargs)

    @property
    def crop(self):
        return self._get_parameter("crop")[0]

    def process_frame(
        self, stream, data_samples: List[DataSample], **kwargs
    ) -> Tuple[StreamEvent, Union[Dict, str]]:
        if len(data_samples) > 1:
            self.logger.warning(
                f"Expected only a single DataFile, got {len(data_samples)}. Processing data_samples[0] only."
            )

        ds = data_samples[0]
        w, h = ds.wh

        if self.crop is not None:
            if isinstance(self.crop[0], float):
                x0 = int(self.crop[0] * w)
                y0 = int(self.crop[1] * h)
                x1 = int(self.crop[2] * w)
                y1 = int(self.crop[3] * h)
                anno_tuple = (x0, y0, x1, y1)
            else:
                anno_tuple = self.crop
            img = ds.crop_content([self.crop])[0]
        else:
            anno_tuple = (0, 0, w, h)
            img = ds.content

        score = self._motion_score_model.update(img, ds.media_frame_index)[self.score_type]
        score_obs = Observation.make_scalar_observation(
            score,
            self.attribute_id,
            occurred_at=ds.recorded_at,
            pipeline_element_name=self.__class__.__name__,
            frame_id=ds.media_frame_index,
        )

        a = Annotation.from_left_top_right_bottom_box(
            anno_tuple, 1.0, frame_id=ds.media_frame_index, data_file_id=ds.data_file_id
        )
        a.observations.add(score_obs)
        score_obs.entity_id = self.entity_id
        score_obs.annotation_id = a.id

        # FIXME - fix memory leak, need to make entity not global
        # JONO: Not sure what this means entirely, I remove the entity
        # from the IdentityMap at the end of record_observations, and 'reset'
        # self.Entity by creating a new instance with the same id. Will that
        # be enough?
        self.entity.annotations.add(a)

        obj_obs = Observation.make_object_class_observation(
            object_class_uuid=self.object_class_id,
            object_class_value=self.object_class_id.label,
            confidence=1.0,
            occurred_at=ds.recorded_at,
            pipeline_element_name=self.__class__.__name__,
            frame_id=ds.media_frame_index,
        )
        a.observations.add(obj_obs)
        obj_obs.entity_id = self.entity_id
        obj_obs.annotation_id = a.id
        self.entity.annotations.add(a)

        self.record_observations([score_obs, obj_obs])
        self.entity = Entity(id=self.entity_id)

        return StreamEvent.OKAY, {"motion_score": score_obs}
