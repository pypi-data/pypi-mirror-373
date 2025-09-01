from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from uuid import UUID, uuid4

import numpy as np
import shapely.geometry as geom
from pydantic import ConfigDict, Field

from highlighter.client.base_models.base_models import Polygon
from highlighter.core import GQLBaseModel

from ...core import (
    DATA_FILE_ATTRIBUTE_UUID,
    EMBEDDING_ATTRIBUTE_UUID,
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    TRACK_ATTRIBUTE_UUID,
    LabeledUUID,
)
from .datum_source import DatumSource


class Observation(GQLBaseModel):
    """
    entity_id and attribute_id are global
    value is tied to the attribute, and we have unit for it, so it doesn't appear here
    """

    id: UUID = Field(..., default_factory=uuid4)
    _global_observation_entity: Optional[Any] = (
        None  # Optional[Entity] (not imported to avoid circular imports)
    )
    _annotation: Optional[Any] = None  # Optional[Annotation] (not imported to avoid circular imports)

    attribute_id: LabeledUUID
    value: Any  # <-- ToDo: Add specific types
    occurred_at: datetime = Field(..., default_factory=lambda: datetime.now(timezone.utc))
    datum_source: DatumSource = Field(..., default_factory=lambda: DatumSource(confidence=1))
    unit: Optional[str] = None
    file_id: Optional[UUID] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "entity" in kwargs:
            self.entity = kwargs["entity"]  # Trigger setter
        if "annotation" in kwargs:
            self.annotation = kwargs["annotation"]  # Trigger setter

    @property
    def entity(self):
        if self._annotation is not None:
            return self._annotation.entity
        elif self._global_observation_entity is not None:
            return self._global_observation_entity
        else:
            return None

    @entity.setter
    def entity(self, new_entity: Optional["Entity"]):
        from .entity import Entity  # Import here to avoid circular imports

        if not isinstance(new_entity, Optional[Entity]):
            raise TypeError(f"Expected Entity, got '{type(new_entity).__qualname__}'")

        # Check if update is allowed
        if self._annotation is not None:
            raise ValueError(
                "Cannot reassign observation to entity {new_entity.id}: "
                "Observation is already associated with an annotation. "
                "Assign the annotation to the new entity, or dissasociate "
                "the observation from the annotation via `observation.annotation = None` first."
            )
        if (
            new_entity is not None
            and self._global_observation_entity is not None
            and new_entity != self._global_observation_entity
        ):
            raise ValueError(
                f"Observation is still associated with entity {self.entity.id}. "
                "Dissiaociate via `self.entity = None` before "
                "associating with a different entity."
            )

        # Do the update
        if new_entity is None:
            if (
                self._global_observation_entity is not None
                and self in self._global_observation_entity.global_observations
            ):
                self._global_observation_entity.global_observations.remove(self)
        if new_entity is not None and self not in new_entity.global_observations:
            new_entity.global_observations.add(self)
        self._global_observation_entity = new_entity

    @property
    def annotation(self) -> Optional["Annotation"]:
        return self._annotation

    @annotation.setter
    def annotation(self, new_annotation: Optional["Annotation"]):
        from .annotation import Annotation  # Import here to avoid circular imports

        if not isinstance(new_annotation, Optional[Annotation]):
            raise TypeError(f"Expected Annotation, got '{type(new_annotation).__qualname__}'")

        # Check if update is allowed
        if new_annotation is not None and self.annotation is not None and new_annotation != self.annotation:
            raise ValueError(
                f"Observation is still associated with annotation {self.annotation.id}. "
                "Dissiaociate via  `self.annotation = None` before "
                "associating with a different annotation."
            )
        if new_annotation is not None and self._global_observation_entity is not None:
            raise ValueError(
                f"Observation is still associated with entity {self._global_observation_entity.id}. "
                "Dissiaociate via `self.entity = None` before associating with a different entity."
            )

        # Do the update
        if self.annotation is not None:
            self.annotation.observations.remove(self)
        if new_annotation is not None and self not in new_annotation.observations:
            new_annotation.observations.add(self)
        self._annotation = new_annotation

    @classmethod
    def from_deprecated_eavt(cls, eavt, id: Optional[UUID] = None, annotation: Optional["Annotation"] = None):
        kwargs = dict(
            attribute_id=eavt.attribute_id,
            value=eavt.value,
            occurred_at=eavt.time,
            datum_source=eavt.datum_source,
            unit=eavt.unit,
            file_id=eavt.file_id,
        )
        if id:
            kwargs["id"] = id
        if annotation:
            kwargs["annotation"] = annotation
        return cls(**kwargs)

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
            entity_id=str(self.entity.id) if self.entity else None,
            annotation_uuid=str(self.annotation.id) if self.annotation else None,
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
