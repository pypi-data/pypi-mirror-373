import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from highlighter.agent.capabilities.base_capability import Capability, StreamEvent
from highlighter.client.base_models.entity import Entity
from highlighter.client.gql_client import HLClient
from highlighter.client.training_runs import (
    TrainingRunArtefactType,
)
from highlighter.core.data_models import DataSample
from highlighter.predictors.onnx_yolov8 import OnnxYoloV8 as Predictor

__all__ = ["OnnxYoloV8"]

logger = logging.getLogger(__name__)


class OnnxYoloV8(Capability):

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        onnx_file: Optional[str] = None
        training_run_artefact_id: Optional[UUID] = None
        num_classes: int = 80
        class_lookup: Optional[Dict[int | str, Tuple[UUID, str]]] = None
        conf_thresh: float = 0.1
        nms_iou_thresh: float = 0.5
        is_absolute: bool = True

    def __init__(self, context):
        super().__init__(context)
        self._predictor: Optional[Predictor] = None

        onnx_file, found = self._get_parameter("onnx_file")
        if not found:
            training_run_artefact_id, tra_found = self._get_parameter("training_run_artefact_id")
            if not tra_found:
                raise ValueError("Must provide `onnx_file` or `training_run_artefact_id`")
            training_run_artefact = HLClient.get_client().trainingRunArtefact(
                return_type=TrainingRunArtefactType, id=training_run_artefact_id
            )
            onnx_file = training_run_artefact.file_url

        num_classes, found = self._get_parameter("num_classes")
        class_lookup, _ = self._get_parameter("class_lookup", default=None)
        conf_thresh, _ = self._get_parameter("conf_thresh")
        nms_iou_thresh, _ = self._get_parameter("nms_iou_thresh")
        is_absolute, _ = self._get_parameter("is_absolute")

        artefact_cache_dir = Path.home() / ".cache" / "artefacts"
        # FIXME: kwargs {"device_id", "artefact_cache_dir", "onnx_file_download_timeout"}
        # should be optionally configured by the runtime context.
        self._predictor = Predictor(
            onnx_file,
            num_classes,
            class_lookup=class_lookup,
            conf_thresh=conf_thresh,
            nms_iou_thresh=nms_iou_thresh,
            is_absolute=is_absolute,
            artefact_cache_dir=artefact_cache_dir,
        )

    def process_frame(self, stream, data_samples: List[DataSample]) -> Tuple[StreamEvent, Dict]:
        annotations_per_data_sample = self._predictor.predict(data_samples)
        logger.debug(f"annotations_per_data_sample: {annotations_per_data_sample}")
        entities = {}
        for annotations in annotations_per_data_sample:
            for annotation in annotations:
                entity = Entity.from_annotation(annotation)
                entities[entity.id] = entity
        return StreamEvent.OKAY, {"entities": entities}
