# Add neuflow stuff
import logging
import os
import time

import cv2
import numpy as np
import onnxruntime
import requests
import tqdm

__all__ = ["NeuFlowV2", "flow_to_image"]

available_models = ["neuflow_mixed", "neuflow_sintel", "neuflow_things"]


def download_model(url: str, path: str):
    print(f"Downloading model from {url} to {path}")
    r = requests.get(url, stream=True, timeout=30)
    with open(path, "wb") as f:
        total_length = int(r.headers.get("content-length"))
        for chunk in tqdm.tqdm(
            r.iter_content(chunk_size=1024 * 1024),
            total=total_length // (1024 * 1024),
            bar_format="{l_bar}{bar:10}",
        ):
            if chunk:
                f.write(chunk)
                f.flush()


def check_model(model_path: str):
    if os.path.exists(model_path):
        return

    model_name = os.path.basename(model_path).split(".")[0]
    if model_name not in available_models:
        raise ValueError(f"Invalid model name: {model_name}")
    url = f"https://github.com/ibaiGorordo/ONNX-NeuFlowV2-Optical-Flow/releases/download/0.1.0/{model_name}.onnx"
    download_model(url, model_path)


class NeuFlowV2:

    def __init__(self, path: str):
        self.logger = logging.getLogger(__name__)
        check_model(path)

        # Initialize model
        self.session = onnxruntime.InferenceSession(path, providers=onnxruntime.get_available_providers())

        # Get model info
        self.get_input_details()
        self.get_output_details()

    def __call__(self, img_prev: np.ndarray, img_now: np.ndarray) -> np.ndarray:
        return self.estimate_flow(img_prev, img_now)

    def estimate_flow(self, img_prev: np.ndarray, img_now: np.ndarray) -> np.ndarray:
        input_tensors = self.prepare_inputs(img_prev, img_now)

        # Perform inference on the image
        outputs = self.inference(input_tensors)

        return self.process_output(outputs[0])

    def prepare_inputs(self, img_prev: np.ndarray, img_now: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self.img_height, self.img_width = img_now.shape[:2]

        input_prev = self.prepare_input(img_prev)
        input_now = self.prepare_input(img_now)

        return input_prev, input_now

    def prepare_input(self, img: np.ndarray) -> np.ndarray:
        # Resize input image
        input_img = cv2.resize(img, (self.input_width, self.input_height))

        # Scale input pixel values to 0 to 1
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)
        return input_tensor

    def inference(self, input_tensors: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        start = time.perf_counter()
        outputs = self.session.run(
            self.output_names, {self.input_names[0]: input_tensors[0], self.input_names[1]: input_tensors[1]}
        )

        self.logger.debug(f"Inference time: {(time.perf_counter() - start) * 1000:.2f} ms")
        return outputs

    def process_output(self, output) -> np.ndarray:
        flow = output.squeeze().transpose(1, 2, 0)

        return cv2.resize(flow, (self.img_width, self.img_height))

    def get_input_details(self):
        model_inputs = self.session.get_inputs()
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]

        input_shape = model_inputs[0].shape
        self.input_height = input_shape[2]
        self.input_width = input_shape[3]

    def get_output_details(self):
        model_outputs = self.session.get_outputs()
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]


# Ref: https://github.com/liruoteng/OpticalFlowToolkit/blob/5cf87b947a0032f58c922bbc22c0afb30b90c418/lib/flowlib.py#L249
import cv2
import numpy as np


def make_color_wheel():
    """
    Generate color wheel according Middlebury color code
    :return: Color wheel
    """
    RY = 15
    YG = 6
    GC = 4
    CB = 11
    BM = 13
    MR = 6

    ncols = RY + YG + GC + CB + BM + MR

    colorwheel = np.zeros([ncols, 3])

    col = 0

    # RY
    colorwheel[0:RY, 0] = 255
    colorwheel[0:RY, 1] = np.transpose(np.floor(255 * np.arange(0, RY) / RY))
    col += RY

    # YG
    colorwheel[col : col + YG, 0] = 255 - np.transpose(np.floor(255 * np.arange(0, YG) / YG))
    colorwheel[col : col + YG, 1] = 255
    col += YG

    # GC
    colorwheel[col : col + GC, 1] = 255
    colorwheel[col : col + GC, 2] = np.transpose(np.floor(255 * np.arange(0, GC) / GC))
    col += GC

    # CB
    colorwheel[col : col + CB, 1] = 255 - np.transpose(np.floor(255 * np.arange(0, CB) / CB))
    colorwheel[col : col + CB, 2] = 255
    col += CB

    # BM
    colorwheel[col : col + BM, 2] = 255
    colorwheel[col : col + BM, 0] = np.transpose(np.floor(255 * np.arange(0, BM) / BM))
    col += +BM

    # MR
    colorwheel[col : col + MR, 2] = 255 - np.transpose(np.floor(255 * np.arange(0, MR) / MR))
    colorwheel[col : col + MR, 0] = 255

    return colorwheel


colorwheel = make_color_wheel()


def compute_color(u, v):
    """
    compute optical flow color map
    :param u: optical flow horizontal map
    :param v: optical flow vertical map
    :return: optical flow in color code
    """
    [h, w] = u.shape
    img = np.zeros([h, w, 3])
    nanIdx = np.isnan(u) | np.isnan(v)
    u[nanIdx] = 0
    v[nanIdx] = 0

    ncols = np.size(colorwheel, 0)

    rad = np.sqrt(u**2 + v**2)

    a = np.arctan2(-v, -u) / np.pi

    fk = (a + 1) / 2 * (ncols - 1) + 1

    k0 = np.floor(fk).astype(int)

    k1 = k0 + 1
    k1[k1 == ncols + 1] = 1
    f = fk - k0

    for i in range(0, np.size(colorwheel, 1)):
        tmp = colorwheel[:, i]
        col0 = tmp[k0 - 1] / 255
        col1 = tmp[k1 - 1] / 255
        col = (1 - f) * col0 + f * col1

        idx = rad <= 1
        col[idx] = 1 - rad[idx] * (1 - col[idx])
        notidx = np.logical_not(idx)

        col[notidx] *= 0.75
        img[:, :, i] = np.uint8(np.floor(255 * col * (1 - nanIdx)))

    return img


def flow_to_image(flow, maxrad=None):
    """
    Convert flow into middlebury color code image
    :param flow: optical flow map
    :return: optical flow image in middlebury color
    """
    u = flow[:, :, 0]
    v = flow[:, :, 1]

    rad = np.sqrt(u**2 + v**2)
    if maxrad is None:
        maxrad = max(-1, np.max(rad))

    eps = np.finfo(float).eps
    u = np.clip(u, -maxrad + 5, maxrad - 5)
    v = np.clip(v, -maxrad + 5, maxrad - 5)

    u = u / (maxrad + eps)
    v = v / (maxrad + eps)

    img = compute_color(u, v)

    return np.uint8(img)
