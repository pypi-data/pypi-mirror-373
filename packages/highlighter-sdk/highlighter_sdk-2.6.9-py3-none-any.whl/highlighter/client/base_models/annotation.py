from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import numpy as np
import shapely.geometry as geom
from PIL.Image import Image
from pydantic import BaseModel, ConfigDict, Field, field_validator

from highlighter.client.utilities import stringify_if_not_null
from highlighter.core.hl_base_model import HLModelMap

from ...core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    BelongsTo,
    HasMany,
    HLDataModel,
    polygon_from_mask,
)
from .base_models import EAVT
from .data_file import DataFile
from .datum_source import DatumSource
from .observation import Observation

__all__ = ["Annotation"]


class AnnotationCrop(BaseModel):
    content: Any
    annotation_id: UUID
    entity_id: Optional[UUID] = None


@HasMany("observations", target_cls="highlighter.client.Observation", back_populates="annotation")
@BelongsTo(
    "entity",
    target_cls="highlighter.client.Entity",
    back_populates="annotations",
)
class Annotation(HLDataModel):
    id: UUID = Field(..., default_factory=uuid4)

    location: Optional[Union[geom.Polygon, geom.MultiPolygon, geom.LineString, geom.Point]] = None
    data_file_id: Optional[UUID] = None
    observations: HLModelMap = Field(..., default_factory=lambda: HLModelMap(Observation))
    entity_id: Optional[UUID] = None

    # TODO update HL Web to refer to data-sources (e.g. webrtc streams) as well as files
    track_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None

    datum_source: DatumSource

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Required for shapely geometry types

    @field_validator("observations", mode="before")
    @classmethod
    def validate_c(cls, v: Any) -> HLModelMap:
        if isinstance(v, list):
            _v = HLModelMap(Observation)
        else:
            _v = v
        assert isinstance(_v, HLModelMap)
        return _v

    @classmethod
    def from_points(
        cls,
        points: List[Tuple[int, int]],
        confidence: float,
        data_file_id: Optional[UUID] = None,
        observations: Optional[List[Observation]] = None,
        entity_id: Optional[UUID] = None,
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
            datum_source=datum_source,
            location=geom.Polygon(points),
            data_file_id=data_file_id,
            entity_id=entity_id,
            track_id=track_id,
            correlation_id=correlation_id,
        )
        if observations is not None:
            _ = [anno.observations.add(o) for o in observations]
        return anno

    @classmethod
    def from_left_top_right_bottom_box(
        cls,
        box: Tuple[int, int, int, int],
        confidence: float,
        data_file_id: Optional[UUID] = None,
        observations: Optional[List[Observation]] = None,
        entity_id: Optional[UUID] = None,
        track_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
        # Optional DatumSource fields
        frame_id: Optional[int] = None,
        host_id: Optional[str] = None,
        pipeline_element_name: Optional[str] = None,
    ):
        x0, y0, x1, y1 = box
        return cls.from_points(
            ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)),
            confidence,
            data_file_id=data_file_id,
            observations=observations,
            entity_id=entity_id,
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
        entity_id: Optional[UUID] = None,
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
            entity_id=entity_id,
            track_id=track_id,
            correlation_id=correlation_id,
            frame_id=frame_id,
            host_id=host_id,
            pipeline_element_name=pipeline_element_name,
        )

    def serialize(self):
        return {
            "id": str(self.id),
            "entity_id": str(self.entity_id),
            "location": self.location.wkt if self.location is not None else None,
            "observations": [o.serialize() for o in self.observations.values()],
            "track_id": str(self.track_id),
            "correlation_id": str(self.correlation_id),
            "data_file_id": str(self.data_file_id),
            "datum_source": self.datum_source.serialize(),
        }

    def get_observation(self, attribute_id: UUID) -> Optional[Observation]:
        for o in self.observations:
            if o.attribute_id == attribute_id:
                return o
        return None

    def has_observation(self, attribute_id: UUID, value: Optional[Any] = None) -> bool:
        if value is None:
            return any([o.attribute_id == attribute_id for o in self.observations])
        else:
            return any([((o.attribute_id == attribute_id) and (o.value == value)) for o in self.observations])

    def crop(self, crop_args: "CropArgs") -> AnnotationCrop:
        from ...datasets.cropping import crop_rect_from_poly

        if self.data_file_id is None:
            raise ValueError("Cannot crop an Annotation when data_file_id is None")
        if self.location is None:
            raise ValueError("Cannot crop an Annotation when location is None")
        if not isinstance(self.location, geom.Polygon):
            raise ValueError(f"Cannot crop an Annotation when location is {type(self.location)}")

        data_file = DataFile.find_by_id(self.data_file_id)

        if data_file is None:
            raise ValueError(f"Could not find DataFile with id {self.data_file_id}")

        if "image" not in data_file.content_type:
            raise ValueError(
                f"Cannot crop data_file with content_type '{data_file.content_type}', must be 'image'"
            )

        if not isinstance(data_file.content, (np.ndarray, Image)):
            raise ValueError(
                f"Cannot crop data_file with content '{type(data_file.content)}', must be (PIL.Image|np.array)"
            )

        cropped_image = crop_rect_from_poly(data_file.content, self.location, crop_args)
        return AnnotationCrop(content=cropped_image, entity_id=self.entity_id, annotation_id=self.id)

    def to_deprecated_pixel_location_eavt(self) -> EAVT:
        return EAVT.make_pixel_location_eavt(
            entity_id=self.entity_id,
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

    def to_json(self):
        data = self.model_dump()
        data["id"] = stringify_if_not_null(data["id"])
        data["entity_id"] = stringify_if_not_null(data["entity_id"])
        data["location"] = data["location"].wkt
        data["datum_source"] = data["datum_source"]
        data["observations"] = [d.to_json() for d in data["observations"].values()]

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
            "entityId": stringify_if_not_null(self.entity_id),
            "dataFileId": stringify_if_not_null(self.data_file_id),
            "uuid": stringify_if_not_null(self.id),
        }
        return result
