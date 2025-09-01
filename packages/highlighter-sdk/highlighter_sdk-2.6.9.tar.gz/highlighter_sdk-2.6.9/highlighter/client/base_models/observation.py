from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from uuid import UUID, uuid4

import numpy as np
import shapely.geometry as geom
from pydantic import ConfigDict, Field

from highlighter.client.base_models.base_models import Polygon
from highlighter.core.hl_base_model import BelongsTo

from ...core import (
    DATA_FILE_ATTRIBUTE_UUID,
    EMBEDDING_ATTRIBUTE_UUID,
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    TRACK_ATTRIBUTE_UUID,
    HLDataModel,
    LabeledUUID,
)
from .datum_source import DatumSource

__all__ = ["Observation"]


@BelongsTo(
    "entity",
    target_cls="highlighter.client.Entity",
    back_populates="global_observations",
)
@BelongsTo(
    "annotation",
    target_cls="highlighter.client.Annotation",
    back_populates="observations",
)
class Observation(HLDataModel):
    """
    entity_id and attribute_id are global
    value is tied to the attribute, and we have unit for it, so it doesn't appear here
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(..., default_factory=uuid4)
    entity_id: Optional[UUID] = None
    annotation_id: Optional[UUID] = None
    attribute_id: LabeledUUID
    value: Any  # <-- ToDo: Add specific types
    occurred_at: datetime = Field(..., default_factory=lambda: datetime.now(timezone.utc))
    datum_source: DatumSource
    unit: Optional[str] = None
    file_id: Optional[UUID] = None

    @classmethod
    def from_deprecated_eavt(cls, eavt, id: UUID, annotation_id: Optional[UUID] = None):
        return cls(
            id=id,
            entity_id=eavt.entity_id,
            annotation_id=annotation_id,
            attribute_id=eavt.attribute_id,
            value=eavt.value,
            occurred_at=eavt.time,
            datum_source=eavt.datum_source,
            unit=eavt.unit,
            file_id=eavt.file_id,
        )

    def to_json(self):
        data = self.model_dump()
        data["id"] = str(self.id)
        data["value"] = self.value.to_json() if hasattr(self.value, "to_json") else self.value
        data["file_id"] = str(self.file_id)
        return data

    def model_dump(self, *args, **kwargs):
        value = self.value
        if isinstance(value, Polygon):
            value = value.dict()

        if isinstance(value, UUID):
            value = str(value)

        return dict(
            entity_id=str(self.entity_id),
            attribute_id=str(self.attribute_id),
            value=value,
            occurred_at=self.occurred_at.isoformat(),
            datum_source=self.datum_source.model_dump(),
        )

    def gql_dict(self):
        d = super().gql_dict()
        d["time"] = d.pop("occurredAt")
        return d

    def serialize(self):
        return self.to_json()

    def is_pixel_location(self):
        return str(self.attribute_id) == PIXEL_LOCATION_ATTRIBUTE_UUID

    def is_object_class(self):
        return str(self.attribute_id) == OBJECT_CLASS_ATTRIBUTE_UUID

    def is_track(self):
        return str(self.attribute_id) == TRACK_ATTRIBUTE_UUID

    def is_embedding(self):
        return str(self.attribute_id) == EMBEDDING_ATTRIBUTE_UUID

    def get_confidence(self):
        return self.datum_source.confidence

    @classmethod
    def make_scalar_observation(
        cls,
        value: Union[int, float, tuple, list],
        attribute_id: LabeledUUID,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
        unit: Optional[str] = None,
    ):
        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        if isinstance(value, tuple):
            value = list(value)

        return cls(
            attribute_id=attribute_id,
            value=value,
            datum_source=datum_source,
            occurred_at=occurred_at,
            unit=unit,
        )

    @classmethod
    def make_image_observation(
        cls,
        image: np.ndarray,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        return cls(
            attribute_id=DATA_FILE_ATTRIBUTE_UUID,
            value=image,
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_embedding_observation(
        cls,
        embedding: List[float],
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        if not isinstance(embedding, list):
            t = type(embedding)
            raise ValueError(f"embedding must be list of float not {t}")

        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        return cls(
            attribute_id=EMBEDDING_ATTRIBUTE_UUID,
            value=embedding,
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_pixel_location_observation(
        cls,
        value: Union[
            geom.Polygon,
            geom.MultiPolygon,
            geom.LineString,
            geom.Point,
        ],
        confidence: float,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Create a new pixel_location attribute"""

        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            attribute_id=PIXEL_LOCATION_ATTRIBUTE_UUID,
            value=value,
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_enum_observation(
        cls,
        attribute_uuid: UUID,
        attribute_label: str,
        enum_value: str,
        enum_id: UUID,
        confidence: float,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Make an Observation with an enum attribute"""
        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            attribute_id=LabeledUUID(
                attribute_uuid,
                label=attribute_label,
            ),
            value=LabeledUUID(
                enum_id,
                label=enum_value,
            ),
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_object_class_observation(
        cls,
        object_class_uuid: UUID,
        object_class_value: str,
        confidence: float,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make an Observation with an object_class"""
        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
            value=LabeledUUID(
                object_class_uuid,
                label=object_class_value,
            ),
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_boolean_observation(
        cls,
        attribute_uuid: UUID,
        attribute_label: str,
        value: bool,
        confidence: float,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make an Observation with an object_class"""
        if not isinstance(value, bool):
            raise ValueError(
                "make_boolean_observation expects value arg to be of type bool "
                f"got: {value} of type: {type(value)}"
            )

        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            attribute_id=LabeledUUID(
                attribute_uuid,
                label=attribute_label,
            ),
            value=value,
            datum_source=datum_source,
            occurred_at=occurred_at,
        )

    @classmethod
    def make_detection_observation_pair(
        cls,
        location_value: Union[geom.Polygon, geom.MultiPolygon],
        object_class_value: str,
        object_class_uuid: UUID,
        confidence: float,
        occurred_at: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make both a pixel_location and
        object_class attribute, returning them both in a list
        """
        pixel_location_observation = Observation.make_pixel_location_observation(
            location_value,
            confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
            occurred_at=occurred_at,
        )

        object_class_observation = Observation.make_object_class_observation(
            object_class_uuid,
            object_class_value,
            confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
            occurred_at=occurred_at,
        )
        return [pixel_location_observation, object_class_observation]
