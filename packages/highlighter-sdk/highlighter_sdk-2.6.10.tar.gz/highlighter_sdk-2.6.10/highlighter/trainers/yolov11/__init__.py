try:
    import ultralytics
except ModuleNotFoundError as _:
    raise ModuleNotFoundError(
        "The ultralytics package is not installed, use " "`pip install highlighter-sdk[yolo]`"
    )

__all__ = ["generate", "train", "prepare_datasets"]
from .trainer import YoloV11Trainer
