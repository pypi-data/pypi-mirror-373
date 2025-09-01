import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import numpy as np

from highlighter.client.gql_client import HLClient
from highlighter.client.training_config import TrainingConfigType, get_training_config
from highlighter.client.training_runs import get_training_run_artefact
from highlighter.core.exceptions import OptionalPackageMissingError

try:
    import cv2
except ModuleNotFoundError as _:
    raise OptionalPackageMissingError("cv2", "opencv")

try:
    import torch
    import torch.nn.functional as F
except ModuleNotFoundError as _:
    raise OptionalPackageMissingError("torch", "torch")


from highlighter.client import TrainingRunArtefactType
from highlighter.client.base_models.annotation import Annotation
from highlighter.client.base_models.observation import Observation
from highlighter.core.data_models import DataSample

from .onnx_predictor import OnnxPredictor

__all__ = ["OnnxYoloV8"]

LOG = logging.getLogger(__name__)


class OnnxYoloV8:

    def __init__(
        self,
        onnx_predictor: Union[OnnxPredictor, str, Path],
        num_classes: int,
        class_lookup: Optional[Dict[int | str, Tuple[UUID, str]]] = None,
        conf_thresh: float = 0.1,
        nms_iou_thresh: float = 0.5,
        is_absolute: bool = True,
        **kwargs,
    ):
        """
        Args:
            num_classes: The number of output classes of the predictor
            class_lookup: Optional. If set then only classes in the dict will be returned. If not set the
            the Annotation's ObjectClass Observation value with be UUID(int=class_id) with no 'human readable' label
            conf_thresh: Only return detections with confidence >= conf_thresh
            nms_iou_thresh: Detections with an IOU >= nms_iou_thresh and the same class_id will be considered the same entity and the
            one with the max confidence will be used
            is_absolute: True if the model returns detections in absolute pixel values, else set to false.
            kwargs: Optional args to pass to OnnxPredictor
        """

        if isinstance(onnx_predictor, OnnxPredictor):
            self._onnx_predictor = onnx_predictor
        else:
            self._onnx_predictor = OnnxPredictor(onnx_predictor, **kwargs)

        # Numpy dtype: support both FP32 and FP16 onnx model
        self.ndtype = (
            np.half if self._onnx_predictor.sess.get_inputs()[0].type == "tensor(float16)" else np.single
        )
        self.nms_box_conf = conf_thresh  # Boxes with conf < this will be filterd out during NMS,
        # keep this low because we filter out low conf preds in the Element

        self.nms_iou_thr = nms_iou_thresh  # Boxes with iou < this will be filterd out during NMS

        self.num_classes = num_classes
        self.class_lookup = None
        if class_lookup is not None:
            # Ensure keys are int so that class lookup works.
            # JSON doesn't allow numbers as keys so we may receive strings.
            self.class_lookup = {int(k): v for k, v in class_lookup.items()}
        self.is_absolute = is_absolute

        # Get model width and height(YOLOv8-seg only has one input)
        self.model_height, self.model_width = [x.shape for x in self._onnx_predictor.sess.get_inputs()][0][
            -2:
        ]
        self.use_high_res_masks = False  # see:

        onnx_model_input_shape = self._onnx_predictor.sess.get_inputs()[0].shape

        if (len(onnx_model_input_shape) != 4) or (onnx_model_input_shape[0] != 1):
            raise NotImplementedError(
                f"{self.__class__.__name__} can only deal with onnx models "
                "with static input shapes [batch=1, chan=3, h, w] "
                f"got: {onnx_model_input_shape}."
            )

    @classmethod
    def load_from_training_run(
        cls, training_run_id: int, artefact_id: Union[UUID, str], cache_dir: Optional[Path] = None, **kwargs
    ) -> "OnnxYoloV8":
        if cache_dir:
            onnx_file = cache_dir / f"{training_run_id}-{artefact_id}.onnx14"
            training_config_path = cache_dir / f"{training_run_id}-{artefact_id}.yaml"

            if not onnx_file.exists():
                get_training_run_artefact(
                    HLClient.get_client(),
                    str(artefact_id),
                    download_file_url=True,
                    file_url_save_path=str(onnx_file),
                )

            if not training_config_path.exists():
                training_config = get_training_config(HLClient.get_client(), training_run_id)
                training_config.dump("yaml", training_config_path)
            else:
                training_config = TrainingConfigType.from_yaml(training_config_path)
        else:
            onnx_file = get_training_run_artefact(
                HLClient.get_client(),
                str(artefact_id),
                download_file_url=True,
            )
            training_config = get_training_config(HLClient.get_client(), training_run_id)

        class_lookup = {
            p.position: [p.taxon[0].entity_attribute_enum_id, p.taxon[0].entity_attribute_enum_value]
            for p in training_config.input_output_schema.get_head_model_outputs(0)
        }

        return cls(OnnxPredictor(str(onnx_file)), len(class_lookup), class_lookup=class_lookup, **kwargs)

    @classmethod
    def load_from_artefact(cls, training_run_artefact: TrainingRunArtefactType) -> "OnnxYoloV8":
        onnx_predictor = OnnxPredictor(training_run_artefact.file_url)
        num_classes = len(training_run_artefact.inference_config["model_schema"]["model_outputs"])
        return cls(onnx_predictor, num_classes=num_classes)

    def predict(self, data_samples: List[DataSample], **_) -> List[Annotation]:
        batch_output: List[Annotation] = []
        for data_sample in data_samples:
            img = data_sample.content
            img_pre = preprocess(img, self.model_height, self.model_width, self.ndtype)
            raw_ort_output = self._onnx_predictor.predict_batch(img_pre)
            if len(raw_ort_output[0].shape) == 2:
                # classification  #TODO, make this work with any attribute
                # not just object class
                class_ids = np.argmax(raw_ort_output[0], axis=1)
                if self.class_lookup is not None:
                    preds = [self.class_lookup[class_id] for class_id in class_ids]
                else:
                    preds = [(UUID(int=class_id), "") for class_id in class_ids]
                confs = np.max(raw_ort_output[0], axis=1)
                image_annotations = [
                    Annotation.from_left_top_right_bottom_box(
                        (0, 0, img.shape[1], img.shape[0]),
                        conf,
                        observations=[
                            Observation.make_object_class_observation(
                                *pred,
                                conf,
                                datetime.now(),
                            )
                        ],
                        data_file_id=data_samples[0].data_file_id,
                        frame_id=data_sample.media_frame_index,
                    )
                    for conf, pred in zip(confs, preds)
                ]
            else:
                # Need to fork here and run _postprocess depending if we're
                # dealing with a classification responce or det/seg
                image_annotations = self._postprocess(
                    raw_ort_output,
                    img_pre.shape[-2:],
                    img.shape[:2],
                    data_samples,
                    self.is_absolute,
                    frame_id=data_sample.media_frame_index,
                )

            batch_output.append(image_annotations)
        return batch_output

    def _postprocess(
        self,
        batch_ort_output,
        preproc_img_hw: Tuple[int, int],
        orig_img_hw: Tuple[int, int],
        data_samples,
        is_absolute: bool,
        frame_id: int,
    ) -> List[Annotation]:

        annotations: List[Annotation] = []
        if len(batch_ort_output) == 1:  # detection output
            if batch_ort_output[0].shape[0] != 1:
                # ToDo: Deal with batches, first need to figure out how to export
                # yolov8 with variable batch size
                raise NotImplementedError("Can only handel a batch size of one for now")

            # ultralytics/models/yolo/detect/predict.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
            preds = non_max_suppression(
                torch.Tensor(batch_ort_output[0]),
                self.nms_box_conf,
                self.nms_iou_thr,
                nc=self.num_classes,
            )[0]

            if not is_absolute:
                LOG.debug(f"{self.__class__.__name__} scaling relative boxes (before): {preds[:, :4]}")
                preds[:, [0, 2]] = preds[:, [0, 2]] * preproc_img_hw[1]
                preds[:, [1, 3]] = preds[:, [1, 3]] * preproc_img_hw[0]

            LOG.debug(f"{self.__class__.__name__} preproc_img_hw: {preproc_img_hw}")
            LOG.debug(f"{self.__class__.__name__} orig_img_hw: {orig_img_hw}")
            LOG.debug(f"{self.__class__.__name__} preds (pre scale_boxes): {preds[:, :4]}")
            preds[:, :4] = scale_boxes(preproc_img_hw, preds[:, :4], orig_img_hw)
            preds = preds.numpy()
            trlb_boxes = preds[:, :4]
            confs = preds[:, 4]
            class_ids = preds[:, 5].astype(int)
            LOG.debug(f"{self.__class__.__name__} confs: {confs}")
            LOG.debug(f"{self.__class__.__name__} class_ids: {class_ids}")

            if self.class_lookup is not None:
                all_object_classes = [
                    (i, self.class_lookup.get(class_id, None)) for i, class_id in enumerate(class_ids)
                ]
                valid_idxs = [i for i, object_class in all_object_classes if object_class is not None]
                object_classes = [all_object_classes[i][1] for i in valid_idxs]
                invalid_idxs = [i for i, object_class in all_object_classes if object_class is None]
                LOG.debug(f"Dropping {len(invalid_idxs)} detections with object class not in class_lookup")
                trlb_boxes = trlb_boxes[valid_idxs]
                confs = confs[valid_idxs]
            else:
                object_classes = [(UUID(int=class_id), "") for class_id in class_ids]

            LOG.debug(f"{self.__class__.__name__} preds (post scale_boxes): {preds[:, :4]}")
            LOG.debug(f"{self.__class__.__name__} trlb_boxes: {trlb_boxes}")
            LOG.debug(f"{self.__class__.__name__} confs: {confs}")
            LOG.debug(f"{self.__class__.__name__} object_classes: {object_classes}")

            # FIXME: DataSample, how do we associate Annotations to a data files
            # when they may not exist yet.
            annotations = [
                Annotation.from_left_top_right_bottom_box(
                    box,
                    conf,
                    observations=[
                        Observation.make_object_class_observation(
                            *object_class,
                            conf,
                            datetime.now(),
                        )
                    ],
                    data_file_id=data_samples[0].data_file_id,
                    frame_id=frame_id,
                )
                for box, object_class, conf in zip(trlb_boxes, object_classes, confs)
            ]

            LOG.debug(f"{self.__class__.__name__} annotations: {annotations}")

        elif len(batch_ort_output) == 2:  # segmentation output
            # Rename to make it easier to follow the reference implementation
            # ultralytics/models/yolo/segment/predict.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
            preds = batch_ort_output
            p = non_max_suppression(
                torch.Tensor(preds[0]),
                self.nms_box_conf,
                self.nms_iou_thr,
                nc=self.num_classes,
            )

            proto = (
                preds[1][-1] if isinstance(preds[1], tuple) else preds[1]
            )  # tuple if PyTorch model or array if exported

            if len(p) != 1:
                # ToDo: Deal with batches, first need to figure out how to export
                # yolov8 with variable batch size
                raise NotImplementedError("Can only handel a batch size of one for now")

            pred = p[0]
            proto = proto[0]

            if len(pred):
                masks = process_mask(
                    torch.Tensor(proto), pred[:, 6:], pred[:, :4], preproc_img_hw, upsample=True
                )  # HWC
                masks = scale_masks(masks[None], orig_img_hw)[0].numpy()
                pred[:, :4] = scale_boxes(preproc_img_hw, pred[:, :4], orig_img_hw)

                confs = pred[:, 4].numpy()
                class_ids = pred[:, 5].numpy()

                annotations = [
                    Annotation.from_mask(
                        mask,
                        conf,
                        observations=[
                            Observation.make_object_class_observation(
                                UUID(int=class_id),
                                "",
                                conf,
                                datetime.now(),
                            )
                        ],
                        data_file_id=data_samples[0].data_file_id,
                    )
                    for mask, class_id, conf in zip(masks, class_ids.astype(int), confs)
                ]
        else:
            raise ValueError("Invalid batch_ort_output")

        return annotations


# Adapted from: ultralytics/data/augment.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def preprocess(img, new_height, new_width, ndtype):
    """
    Pre-processes the input image.

    Args:
        img (Numpy.ndarray): image about to be processed.

    Returns:
        img_process (Numpy.ndarray): image preprocessed for inference.
    """

    # Resize and pad input image using letterbox() (Borrowed from Ultralytics)
    shape = img.shape[:2]  # original image shape
    new_shape = (new_height, new_width)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    ratio = r, r
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    pad_w, pad_h = (new_shape[1] - new_unpad[0]) / 2, (new_shape[0] - new_unpad[1]) / 2  # wh padding
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(pad_h - 0.1)), int(round(pad_h + 0.1))
    left, right = int(round(pad_w - 0.1)), int(round(pad_w + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))

    # Transforms: HWC to CHW -> BGR to RGB -> div(255) -> contiguous -> add axis(optional)
    # img = np.ascontiguousarray(np.einsum("HWC->CHW", img)[::-1], dtype=ndtype) / 255.0
    img = np.ascontiguousarray(np.einsum("HWC->CHW", img), dtype=ndtype) / 255.0

    img_process = img[None] if len(img.shape) == 3 else img
    return img_process


# Taken from: ultralytics/utils/metrics.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def _get_covariance_matrix(boxes):
    """
    Generating covariance matrix from obbs.

    Args:
        boxes (torch.Tensor): A tensor of shape (N, 5) representing rotated bounding boxes, with xywhr format.

    Returns:
        (torch.Tensor): Covariance metrixs corresponding to original rotated bounding boxes.
    """
    # Gaussian bounding boxes, ignore the center points (the first two columns) because they are not needed here.
    gbbs = torch.cat((boxes[:, 2:4].pow(2) / 12, boxes[:, 4:]), dim=-1)
    a, b, c = gbbs.split(1, dim=-1)
    cos = c.cos()
    sin = c.sin()
    cos2 = cos.pow(2)
    sin2 = sin.pow(2)
    return a * cos2 + b * sin2, a * sin2 + b * cos2, (a - b) * cos * sin


# Taken from: ultralytics/utils/metrics.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def batch_probiou(obb1, obb2, eps=1e-7):
    """
    Calculate the prob IoU between oriented bounding boxes, https://arxiv.org/pdf/2106.06072v1.pdf.

    Args:
        obb1 (torch.Tensor | np.ndarray): A tensor of shape (N, 5) representing ground truth obbs, with xywhr format.
        obb2 (torch.Tensor | np.ndarray): A tensor of shape (M, 5) representing predicted obbs, with xywhr format.
        eps (float, optional): A small value to avoid division by zero. Defaults to 1e-7.

    Returns:
        (torch.Tensor): A tensor of shape (N, M) representing obb similarities.
    """
    obb1 = torch.from_numpy(obb1) if isinstance(obb1, np.ndarray) else obb1
    obb2 = torch.from_numpy(obb2) if isinstance(obb2, np.ndarray) else obb2

    x1, y1 = obb1[..., :2].split(1, dim=-1)
    x2, y2 = (x.squeeze(-1)[None] for x in obb2[..., :2].split(1, dim=-1))
    a1, b1, c1 = _get_covariance_matrix(obb1)
    a2, b2, c2 = (x.squeeze(-1)[None] for x in _get_covariance_matrix(obb2))

    t1 = (
        ((a1 + a2) * (y1 - y2).pow(2) + (b1 + b2) * (x1 - x2).pow(2))
        / ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)
    ) * 0.25
    t2 = (((c1 + c2) * (x2 - x1) * (y1 - y2)) / ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)) * 0.5
    t3 = (
        ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2))
        / (4 * ((a1 * b1 - c1.pow(2)).clamp_(0) * (a2 * b2 - c2.pow(2)).clamp_(0)).sqrt() + eps)
        + eps
    ).log() * 0.5
    bd = (t1 + t2 + t3).clamp(eps, 100.0)
    hd = (1.0 - (-bd).exp() + eps).sqrt()
    return 1 - hd


# Taken from: ultralytics/utils/ops.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def nms_rotated(boxes, scores, threshold=0.45):
    """
    NMS for obbs, powered by probiou and fast-nms.

    Args:
        boxes (torch.Tensor): (N, 5), xywhr.
        scores (torch.Tensor): (N, ).
        threshold (float): IoU threshold.

    Returns:
    """
    if len(boxes) == 0:
        return np.empty((0,), dtype=np.int8)
    sorted_idx = torch.argsort(scores, descending=True)
    boxes = boxes[sorted_idx]
    ious = batch_probiou(boxes, boxes).triu_(diagonal=1)
    pick = torch.nonzero(ious.max(dim=0)[0] < threshold).squeeze_(-1)
    return sorted_idx[pick]


# Taken from: ultralytics/utils/ops.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def xywh2xyxy(x):
    """
    Convert bounding box coordinates from (x, y, width, height) format to (x1, y1, x2, y2) format where (x1, y1) is the
    top-left corner and (x2, y2) is the bottom-right corner.

    Args:
        x (np.ndarray | torch.Tensor): The input bounding box coordinates in (x, y, width, height) format.

    Returns:
        y (np.ndarray | torch.Tensor): The bounding box coordinates in (x1, y1, x2, y2) format.
    """
    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = torch.empty_like(x) if isinstance(x, torch.Tensor) else np.empty_like(x)  # faster than clone/copy
    dw = x[..., 2] / 2  # half-width
    dh = x[..., 3] / 2  # half-height
    y[..., 0] = x[..., 0] - dw  # top left x
    y[..., 1] = x[..., 1] - dh  # top left y
    y[..., 2] = x[..., 0] + dw  # bottom right x
    y[..., 3] = x[..., 1] + dh  # bottom right y
    return y


# Taken from: ultralytics/utils/ops.py (commit: b617e131bdf4ba6652a55f71b95e2c4c00e2ee59)
def non_max_suppression(
    prediction,
    conf_thres=0.25,
    iou_thres=0.45,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=300,
    nc=0,  # number of classes (optional)
    max_time_img=0.05,
    max_nms=30000,
    max_wh=7680,
    in_place=True,
    rotated=False,
):
    """
    Perform non-maximum suppression (NMS) on a set of boxes, with support for masks and multiple labels per box.

    Args:
        prediction (torch.Tensor): A tensor of shape (batch_size, num_classes + 4 + num_masks, num_boxes)
            containing the predicted boxes, classes, and masks. The tensor should be in the format
            output by a model, such as YOLO.
        conf_thres (float): The confidence threshold below which boxes will be filtered out.
            Valid values are between 0.0 and 1.0.
        iou_thres (float): The IoU threshold below which boxes will be filtered out during NMS.
            Valid values are between 0.0 and 1.0.
        classes (List[int]): A list of class indices to consider. If None, all classes will be considered.
        agnostic (bool): If True, the model is agnostic to the number of classes, and all
            classes will be considered as one.
        multi_label (bool): If True, each box may have multiple labels.
        labels (List[List[Union[int, float, torch.Tensor]]]): A list of lists, where each inner
            list contains the apriori labels for a given image. The list should be in the format
            output by a dataloader, with each label being a tuple of (class_index, x1, y1, x2, y2).
        max_det (int): The maximum number of boxes to keep after NMS.
        nc (int, optional): The number of classes output by the model. Any indices after this will be considered masks.
        max_time_img (float): The maximum time (seconds) for processing one image.
        max_nms (int): The maximum number of boxes into torchvision.ops.nms().
        max_wh (int): The maximum box width and height in pixels.
        in_place (bool): If True, the input prediction tensor will be modified in place.

    Returns:
        (List[torch.Tensor]): A list of length batch_size, where each element is a tensor of
            shape (num_boxes, 6 + num_masks) containing the kept boxes, with columns
            (x1, y1, x2, y2, confidence, class, mask1, mask2, ...).
    """
    import torchvision  # scope for faster 'import ultralytics'

    # Checks
    assert (
        0 <= conf_thres <= 1
    ), f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(
        prediction, (list, tuple)
    ):  # YOLOv8 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output

    bs = prediction.shape[0]  # batch size
    nc = nc or (prediction.shape[1] - 4)  # number of classes
    nm = prediction.shape[1] - nc - 4
    mi = 4 + nc  # mask start index
    xc = prediction[:, 4:mi].amax(1) > conf_thres  # candidates

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    time_limit = 2.0 + max_time_img * bs  # seconds to quit after
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)

    prediction = prediction.transpose(-1, -2)  # shape(1,84,6300) to shape(1,6300,84)
    if not rotated:
        if in_place:
            prediction[..., :4] = xywh2xyxy(prediction[..., :4])  # xywh to xyxy
        else:
            prediction = torch.cat(
                (xywh2xyxy(prediction[..., :4]), prediction[..., 4:]), dim=-1
            )  # xywh to xyxy

    t = time.time()
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[:, 2:4] < min_wh) | (x[:, 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]) and not rotated:
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 4), device=x.device)
            v[:, :4] = xywh2xyxy(lb[:, 1:5])  # box
            v[range(len(lb)), lb[:, 0].long() + 4] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Detections matrix nx6 (xyxy, conf, cls)
        box, cls, mask = x.split((4, nc, nm), 1)

        if multi_label:
            i, j = torch.where(cls > conf_thres)
            x = torch.cat((box[i], x[i, 4 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = cls.max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        if n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        scores = x[:, 4]  # scores
        if rotated:
            boxes = torch.cat((x[:, :2] + c, x[:, 2:4], x[:, -1:]), dim=-1)  # xywhr
            i = nms_rotated(boxes, scores, iou_thres)
        else:
            boxes = x[:, :4] + c  # boxes (offset by class)
            i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections

        # # Experimental
        # merge = False  # use merge-NMS
        # if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
        #     # Update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
        #     from .metrics import box_iou
        #     iou = box_iou(boxes[i], boxes) > iou_thres  # IoU matrix
        #     weights = iou * scores[None]  # box weights
        #     x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
        #     redundant = True  # require redundant detections
        #     if redundant:
        #         i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            LOG.warning(f"WARNING ⚠️ NMS time limit {time_limit:.3f}s exceeded")
            break  # time limit exceeded

    return output


def scale_boxes(img1_shape, boxes, img0_shape, ratio_pad=None, padding=True, xywh=False):
    """
    Rescales bounding boxes (in the format of xyxy by default) from the shape of the image they were originally
    specified in (img1_shape) to the shape of a different image (img0_shape).

    Args:
        img1_shape (tuple): The shape of the image that the bounding boxes are for, in the format of (height, width).
        boxes (torch.Tensor): the bounding boxes of the objects in the image, in the format of (x1, y1, x2, y2)
        img0_shape (tuple): the shape of the target image, in the format of (height, width).
        ratio_pad (tuple): a tuple of (ratio, pad) for scaling the boxes. If not provided, the ratio and pad will be
            calculated based on the size difference between the two images.
        padding (bool): If True, assuming the boxes is based on image augmented by yolo style. If False then do regular
            rescaling.
        xywh (bool): The box format is xywh or not, default=False.

    Returns:
        boxes (torch.Tensor): The scaled bounding boxes, in the format of (x1, y1, x2, y2)
    """
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (
            round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1),
            round((img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1),
        )  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    if padding:
        boxes[..., 0] -= pad[0]  # x padding
        boxes[..., 1] -= pad[1]  # y padding
        if not xywh:
            boxes[..., 2] -= pad[0]  # x padding
            boxes[..., 3] -= pad[1]  # y padding
    boxes[..., :4] /= gain
    return clip_boxes(boxes, img0_shape)


def clip_boxes(boxes, shape):
    """
    Takes a list of bounding boxes and a shape (height, width) and clips the bounding boxes to the shape.

    Args:
        boxes (torch.Tensor): the bounding boxes to clip
        shape (tuple): the shape of the image

    Returns:
        (torch.Tensor | numpy.ndarray): Clipped boxes
    """
    if isinstance(boxes, torch.Tensor):  # faster individually (WARNING: inplace .clamp_() Apple MPS bug)
        boxes[..., 0] = boxes[..., 0].clamp(0, shape[1])  # x1
        boxes[..., 1] = boxes[..., 1].clamp(0, shape[0])  # y1
        boxes[..., 2] = boxes[..., 2].clamp(0, shape[1])  # x2
        boxes[..., 3] = boxes[..., 3].clamp(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2
    return boxes


def process_mask(protos, masks_in, bboxes, shape, upsample=False):
    """
    Apply masks to bounding boxes using the output of the mask head.

    Args:
        protos (torch.Tensor): A tensor of shape [mask_dim, mask_h, mask_w].
        masks_in (torch.Tensor): A tensor of shape [n, mask_dim], where n is the number of masks after NMS.
        bboxes (torch.Tensor): A tensor of shape [n, 4], where n is the number of masks after NMS.
        shape (tuple): A tuple of integers representing the size of the input image in the format (h, w).
        upsample (bool): A flag to indicate whether to upsample the mask to the original image size. Default is False.

    Returns:
        (torch.Tensor): A binary mask tensor of shape [n, h, w], where n is the number of masks after NMS, and h and w
            are the height and width of the input image. The mask is applied to the bounding boxes.
    """

    c, mh, mw = protos.shape  # CHW
    ih, iw = shape

    masks = (masks_in @ protos.float().view(c, -1)).sigmoid().view(-1, mh, mw)  # CHW
    width_ratio = mw / iw
    height_ratio = mh / ih

    downsampled_bboxes = bboxes.clone()
    downsampled_bboxes[:, 0] *= width_ratio
    downsampled_bboxes[:, 2] *= width_ratio
    downsampled_bboxes[:, 3] *= height_ratio
    downsampled_bboxes[:, 1] *= height_ratio

    masks = crop_mask(masks, downsampled_bboxes)  # CHW
    if upsample:
        masks = F.interpolate(masks[None], shape, mode="bilinear", align_corners=False)[0]  # CHW
    return masks.gt_(0.5)


def crop_mask(masks, boxes):
    """
    It takes a mask and a bounding box, and returns a mask that is cropped to the bounding box.

    Args:
        masks (torch.Tensor): [n, h, w] tensor of masks
        boxes (torch.Tensor): [n, 4] tensor of bbox coordinates in relative point form

    Returns:
        (torch.Tensor): The masks are being cropped to the bounding box.
    """
    _, h, w = masks.shape
    x1, y1, x2, y2 = torch.chunk(boxes[:, :, None], 4, 1)  # x1 shape(n,1,1)
    r = torch.arange(w, device=masks.device, dtype=x1.dtype)[None, None, :]  # rows shape(1,1,w)
    c = torch.arange(h, device=masks.device, dtype=x1.dtype)[None, :, None]  # cols shape(1,h,1)

    return masks * ((r >= x1) * (r < x2) * (c >= y1) * (c < y2))


def scale_masks(masks, shape, padding=True):
    """
    Rescale segment masks to shape.

    Args:
        masks (torch.Tensor): (N, C, H, W).
        shape (tuple): Height and width.
        padding (bool): If True, assuming the boxes is based on image augmented by yolo style. If False then do regular
            rescaling.
    """
    mh, mw = masks.shape[2:]
    gain = min(mh / shape[0], mw / shape[1])  # gain  = old / new
    pad = [mw - shape[1] * gain, mh - shape[0] * gain]  # wh padding
    if padding:
        pad[0] /= 2
        pad[1] /= 2
    top, left = (int(pad[1]), int(pad[0])) if padding else (0, 0)  # y, x
    bottom, right = (int(mh - pad[1]), int(mw - pad[0]))
    masks = masks[..., top:bottom, left:right]

    masks = F.interpolate(masks, shape, mode="bilinear", align_corners=False)  # NCHW
    return masks
