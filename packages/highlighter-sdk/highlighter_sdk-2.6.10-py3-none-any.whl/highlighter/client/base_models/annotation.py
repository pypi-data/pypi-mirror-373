from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import numpy as np
import shapely.geometry as geom
from PIL.Image import Image
from pydantic import BaseModel, ConfigDict, Field, field_validator

from highlighter.core import GQLBaseModel
from highlighter.core.data_models.data_sample import DataSample
from highlighter.core.utilities import stringify_if_not_null

from ...core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    polygon_from_mask,
)
from .base_models import EAVT
from .datum_source import DatumSource
from .observation import Observation
from .validated_set import ValidatedSet


class AnnotationCrop(BaseModel):
    content: Any
    annotation_id: UUID
    entity_id: Optional[UUID] = None


_sentinel = object()


class Annotation(GQLBaseModel):
    id: UUID = Field(..., default_factory=uuid4)
    _entity: Optional[Any] = None  # Optional[Entity], not imported to avoid circular imports

    location: Optional[Union[geom.Polygon, geom.MultiPolygon, geom.LineString, geom.Point]] = None
    data_file_id: Optional[UUID] = None
    observations: ValidatedSet
    track_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None

    datum_source: DatumSource = Field(..., default_factory=lambda: DatumSource(confidence=1))

    model_config = ConfigDict(
        arbitrary_types_allowed=True, extra="ignore"
    )  # Required for shapely geometry types

    def __init__(self, **kwargs):
        observations = ValidatedSet()
        if "observations" in kwargs and kwargs["observations"] is not None:
            for obs in kwargs["observations"]:
                observations.append(obs)
        kwargs["observations"] = observations
        super().__init__(**kwargs)
        if "entity" in kwargs:
            self.entity = kwargs["entity"]  # Trigger setter
        # Validate observations passed to constructor
        self.observations.validator = self.validate_add_observation
        for observation in self.observations:
            self.validate_add_observation(observation)

    @property
    def entity(self) -> Optional["Entity"]:
        return self._entity

    @entity.setter
    def entity(self, new_entity: Optional["Entity"]):
        from .entity import Entity  # Import here to avoid circular imports

        if not isinstance(new_entity, Optional[Entity]):
            raise TypeError(f"Expected Entity, got '{type(new_entity).__qualname__}'")

        # Check if update is allowed
        if new_entity is not None and self.entity is not None and new_entity != self.entity:
            raise ValueError(
                f"Annotation is still associated with entity {self.entity.id}. "
                "Dissiaociate via `self.entity = None` before "
                "associating with a different entity."
            )

        # Do the update
        if self.entity is not None:
            self.entity.annotations.remove(self)
        if new_entity is not None and self not in new_entity.annotations:
            new_entity.annotations.add(self)
        self._entity = new_entity

    def validate_add_observation(self, new_observation: Observation):
        if not isinstance(new_observation, Observation):
            raise TypeError(f"Expected Observation, got {type(new_observation).__qualname__}")

        # Check if update is allowed
        if new_observation._global_observation_entity is not None:
            raise ValueError(
                "Cannot add observation that references a different entity. "
                f"Dissasociate the observation from entity {new_observation.entity.id} "
                f"via `observation.entity = None` before adding it to annotation {self.id}"
            )
        if new_observation._annotation is not None and new_observation._annotation != self:
            raise ValueError(
                "Cannot add observation that references a different annotation. "
                f"Dissasociate the observation from annotation {new_observation._annotation.id} "
                f"via `observation.annotation = None` before adding it to annotation {self.id}"
            )

        # Do associated updates
        new_observation._annotation = self

    def get_or_create_entity(self) -> "Entity":
        from .entity import Entity

        if self.entity is not None:
            return self.entity
        entity = Entity()
        entity.annotations.add(self)
        return entity

    @classmethod
    def from_points(
        cls,
        points: List[Tuple[int, int]],
        confidence: float,
        data_file_id: Optional[UUID] = None,
        observations: Optional[List[Observation]] = None,
        track_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
        # Optional DatumSource fields
        frame_id: Optional[int] = None,
        host_id: Optional[str] = None,
        pipeline_element_name: Optional[str] = None,
    ):
        datum_source = DatumSource(
            confidence=confidence,
            frame_id=frame_id,
            host_id=host_id,
            pipeline_element_name=pipeline_element_name,
        )

        anno = cls(
            location=geom.Polygon(points),
            observations=observations,
            track_id=track_id,
            correlation_id=correlation_id,
            data_file_id=data_file_id,
            datum_source=datum_source,
        )
        return anno

    @classmethod
    def from_left_top_right_bottom_box(
        cls,
        box: Tuple[int, int, int, int],
        confidence: float,
        data_file_id: Optional[UUID] = None,
        observations: Optional[List[Observation]] = None,
        track_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
        # Optional DatumSource fields
        frame_id: Optional[int] = None,
        host_id: Optional[str] = None,
        pipeline_element_name: Optional[str] = None,
    ):
        x0, y0, x1, y1 = box
        return cls.from_points(
            [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)],
            confidence,
            data_file_id=data_file_id,
            observations=observations,
            track_id=track_id,
            correlation_id=correlation_id,
            frame_id=frame_id,
            host_id=host_id,
            pipeline_element_name=pipeline_element_name,
        )

    @classmethod
    def from_mask(
        cls,
        mask: np.array,
        confidence: float,
        data_file_id: Optional[UUID] = None,
        observations: Optional[List[Observation]] = None,
        track_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
        # Optional DatumSource fields
        frame_id: Optional[int] = None,
        host_id: Optional[str] = None,
        pipeline_element_name: Optional[str] = None,
        **polygon_from_mask_kwargs,
    ):

        points = polygon_from_mask(mask, **polygon_from_mask_kwargs)
        points = [(x, y) for x, y in zip(points[:-1:2], points[1::2])]
        # Shapely expects a closed
        points.append(points[0])
        # breakpoint()

        return cls.from_points(
            points,
            confidence,
            data_file_id=data_file_id,
            observations=observations,
            track_id=track_id,
            correlation_id=correlation_id,
            frame_id=frame_id,
            host_id=host_id,
            pipeline_element_name=pipeline_element_name,
        )

    def observations_where(
        self, *, attribute_id: UUID | None = None, value: Any = _sentinel
    ) -> List[Observation]:
        obs_where = []
        for o in self.observations:
            if attribute_id is not None and o.attribute_id == attribute_id:
                if value is _sentinel or o.value == value:
                    obs_where.append(o)
        return obs_where

    def crop(self, crop_args: "CropArgs", data_sample: DataSample) -> AnnotationCrop:
        from ...datasets.cropping import crop_rect_from_poly

        if self.data_file_id is None:
            raise ValueError("Cannot crop an Annotation when data_file_id is None")
        if self.location is None:
            raise ValueError("Cannot crop an Annotation when location is None")
        if not isinstance(self.location, geom.Polygon):
            raise ValueError(f"Cannot crop an Annotation when location is {type(self.location)}")

        if "image" not in data_sample.content_type:
            raise ValueError(
                f"Cannot crop data_file with content_type '{data_sample.content_type}', must be 'image'"
            )

        if not isinstance(data_sample.content, (np.ndarray, Image)):
            raise ValueError(
                f"Cannot crop data_file with content '{type(data_sample.content).__qualname__}', must be (PIL.Image|np.array)"
            )

        cropped_image = crop_rect_from_poly(data_sample.content, self.location, crop_args)
        return AnnotationCrop(content=cropped_image, entity_id=self.entity.id, annotation_id=self.id)

    def to_deprecated_pixel_location_eavt(self) -> EAVT:
        if self.entity is None:
            raise ValueError("Entity must exist to convert Annotation to deprecated EAVT")
        return EAVT.make_pixel_location_eavt(
            entity_id=self.entity.id,
            location_points=self.location,
            confidence=self.datum_source.confidence,
            time=datetime.now(timezone.utc),
            frame_id=self.datum_source.frame_id,
        )

    @field_validator("location")
    @classmethod
    def validate_geometry(cls, v):
        if v is not None:
            assert v.is_valid, f"Invalid Geometry: {v}"
        return v

    def serialize(self):
        return {
            "id": str(self.id),
            "entity_id": str(self.entity.id) if self.entity else None,
            "location": self.location.wkt if self.location is not None else None,
            "observations": [o.serialize() for o in self.observations],
            "track_id": str(self.track_id),
            "correlation_id": str(self.correlation_id),
            "data_file_id": str(self.data_file_id),
            "datum_source": self.datum_source.serialize(),
        }

    def to_json(self):
        data = self.model_dump()
        data["id"] = stringify_if_not_null(data["id"])
        data["entity_id"] = stringify_if_not_null(data.get("entity", {}).get("id"))
        data["location"] = data["location"].wkt if data["location"] is not None else None
        data["datum_source"] = data["datum_source"].to_json()
        data["observations"] = [d.to_json() for d in data["observations"]]

        data["track_id"] = stringify_if_not_null(data["track_id"])
        data["data_file_id"] = stringify_if_not_null(data["data_file_id"])
        data["correlation_id"] = stringify_if_not_null(data["correlation_id"])
        return data

    def gql_dict(self) -> Dict:
        try:
            object_class_observation = [
                observation
                for observation in self.observations
                if observation.attribute_id == OBJECT_CLASS_ATTRIBUTE_UUID
            ][-1]
        except IndexError:
            raise ValueError(
                "Annotation must have an object-class observation in order to submit to Highlighter"
            )

        if isinstance(self.location, geom.Polygon):
            data_type = "polygon"
        elif isinstance(self.location, geom.LineString):
            data_type = "line"
        elif isinstance(self.location, geom.Point):
            data_type = "point"
        else:
            data_type = "polygon"
        result = {
            "objectClassUuid": stringify_if_not_null(object_class_observation.value),
            "location": self.location.wkt if self.location is not None else None,
            "confidence": self.datum_source.confidence,
            "dataType": data_type,
            "correlationId": stringify_if_not_null(self.correlation_id),
            "frameId": self.datum_source.frame_id,
            "trackId": stringify_if_not_null(self.track_id),
            "entityId": str(self.entity.id) if self.entity else None,
            "dataFileId": stringify_if_not_null(self.data_file_id),
            "uuid": stringify_if_not_null(self.id),
        }
        return result
