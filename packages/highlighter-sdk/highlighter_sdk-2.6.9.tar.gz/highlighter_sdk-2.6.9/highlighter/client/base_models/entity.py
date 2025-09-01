from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import numpy as np
import shapely.geometry as geom
from pydantic import Field
from shapely.wkt import loads as wkt_loads

from highlighter.client.base_models.base_models import SubmissionType
from highlighter.core.geometry import polygon_from_tlbr
from highlighter.core.hl_base_model import HasMany, HLModelMap

from ...core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    HLDataModel,
)
from .annotation import Annotation
from .datum_source import DatumSource
from .observation import Observation

__all__ = ["Entity"]


@HasMany("annotations", target_cls="highlighter.client.Annotation", back_populates="entity")
@HasMany("global_observations", target_cls="highlighter.client.Observation", back_populates="entity")
class Entity(HLDataModel):
    id: UUID = Field(..., default_factory=uuid4)
    annotations: HLModelMap = Field(..., default_factory=lambda: HLModelMap(Annotation))
    global_observations: HLModelMap = Field(..., default_factory=lambda: HLModelMap(Observation))

    def get_annotations(self) -> List[Annotation]:
        return list(self.annotations.values())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def make_entity(
        cls,
        entity_id: Optional[UUID] = None,
        location: Optional[geom.Polygon] = None,
        observations: List[Observation] = [],
        global_observations: List[Observation] = [],
    ):
        if entity_id is None:
            entity_id = uuid4()

        annotations = []
        if observations:
            annotations = [
                Annotation(
                    id=uuid4(),
                    entity_id=entity_id,
                    location=location,
                    observations=observations,
                    datum_source=observations[0].datum_source,
                )
            ]

        entity = cls(
            id=entity_id,
            annotations=annotations,
            global_observations=global_observations,
        )
        return entity

    @classmethod
    def from_annotation(cls, annotation: Annotation) -> "Entity":
        if annotation.entity_id is not None:
            entity = Entity(id=annotation.entity_id)
        else:
            entity = Entity(id=uuid4())
            annotation.entity_id = entity.id
            for obs in annotation.observations.values():
                obs.entity_id = entity.id
        entity.annotations[annotation.id] = annotation
        return entity

    def reassign_id(self, new_id: UUID):
        self.id = new_id
        for annotation in self.get_annotations():
            annotation.entity_id = new_id
            for observation in annotation.observations.values():
                observation.entity_id = self.id
        for observation in self.global_observations.values():
            observation.entity_id = self.id

    def to_json(self):
        data = self.model_dump()
        data["id"] = str(data["id"])
        data["annotations"] = [a.to_json() for a in data["annotations"].values()]
        data["global_observations"] = [o.to_json() for o in data["global_observations"].values()]
        return data

    def serialize(self):
        # ToDo: Make this more general
        if self.annotations:
            annotations = [a.serialize() for a in self.annotations.values()]
        else:
            annotations = []

        if self.global_observations:
            global_observations = [o.serialize() for o in self.global_observations.values()]
        else:
            global_observations = []

        result = {
            "id": str(self.id),
            "annotations": annotations,
            "global_observations": global_observations,
        }
        return result

    def to_deprecated_observations(self) -> List[Observation]:
        """
        Convert to the deprecated "set of observations" representation
        where pixel locations are represented as observations rather than annotations
        """
        observations = []
        observations.extend(self.global_observations.values())
        for annotation in self.annotations:
            observations.extend(annotation.observations)
            if annotation.location is not None:
                observation = Observation.make_pixel_location_observation(
                    value=annotation.location,
                    confidence=annotation.datum_source.confidence,
                    occurred_at=datetime.now(timezone.utc),
                    frame_id=annotation.datum_source.frame_id,
                )
                observation.entity = annotation.entity
                observations.append(observation)
        return observations

    @staticmethod
    def entities_to_deprecated_observations(entities: Dict[UUID, "Entity"]) -> List[Observation]:
        observations = []
        for entity in entities.values():
            observations.extend(entity.to_deprecated_observations())
        return observations

    @staticmethod
    def entities_from_assessment(assessment: SubmissionType) -> Dict[UUID, "Entity"]:
        # Step 1: Group annotations and observations by entity, and further group observations by annotation
        grouped_entities = defaultdict(
            lambda: {"annotations": [], "observations": defaultdict(list), "global_observations": []}
        )
        for annotation in assessment.annotations:
            grouped_entities[UUID(annotation.entity_id)]["annotations"].append(annotation)
        for observation in assessment.entity_attribute_values:
            if observation.annotation_uuid is not None:
                grouped_entities[UUID(observation.entity_id)]["observations"][
                    observation.annotation_uuid
                ].append(observation)
            else:
                grouped_entities[UUID(observation.entity_id)]["global_observations"].append(observation)
        # Step 2: Convert Hl Web representations into our local representations
        entities = {}
        for entity_id, entity_data in grouped_entities.items():
            entity = Entity(id=entity_id)
            for annotation in entity_data["annotations"]:
                ann = Annotation(
                    entity_id=entity_id,
                    location=wkt_loads(annotation.location),
                    track_id=annotation.track_id,
                    data_file_id=annotation.data_file_id,
                    datum_source=DatumSource(
                        frame_id=annotation.frame_id,
                        confidence=annotation.confidence,
                    ),
                    correlation_id=annotation.correlation_id,
                )

                obs = Observation(
                    entity_id=entity_id,
                    attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                    value=annotation.object_class.uuid,
                    occurred_at=datetime.now(
                        timezone.utc
                    ),  # TODO store with annotation in hl web or infer from source data file
                    datum_source=DatumSource(
                        frame_id=annotation.frame_id,
                        confidence=annotation.confidence,
                    ),
                )
                ann.observations.add(obs)
                entity.annotations.add(ann)

                for eav in entity_data["observations"][annotation.uuid]:
                    obs = Observation(
                        entity_id=entity_id,
                        attribute_id=eav.entity_attribute_id,
                        value=(
                            eav.value
                            if eav.value is not None
                            else eav.related_entity_id or eav.file_uuid or eav.entity_attribute_enum.id
                        ),
                        occurred_at=eav.occurred_at,
                        datum_source=eav.entity_datum_source,
                    )
                    ann.observations.add(obs)

            for eav in entity_data["global_observations"]:
                entity.global_observations.add(
                    Observation(
                        entity_id=entity_id,
                        attribute_id=eav.entity_attribute_id,
                        value=(
                            eav.value
                            if eav.value is not None
                            else eav.related_entity_id or eav.file_uuid or eav.entity_attribute_enum.id
                        ),
                        occurred_at=eav.occurred_at,
                        datum_source=eav.entity_datum_source,
                    )
                )
            entities[entity_id] = entity
        return entities

    @staticmethod
    def frame_indexed_entities_from_avro(
        avro_entities, data_file_id: UUID
    ) -> List[Tuple[int, Dict[UUID, "Entity"]]]:
        """See Avro schema at highlighter.entity_avro_schema"""
        frame_indexed_entities = defaultdict(dict)  # Outer index is frame ID, inner index is entity ID
        for entity in avro_entities:
            # TODO handle embeddings
            # TODO handle eavts
            for track in entity.tracks:
                for detection in track.detections:
                    observations = [
                        Observation(
                            entity_id=entity.id,
                            attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                            value=entity.object_class,
                            occurred_at=datetime.now(timezone.utc),  # TODO change to correct occurred_at
                            datum_source=DatumSource(
                                confidence=1.0,
                                frame_id=detection.frame_id,
                            ),
                        )
                    ]
                    annotations = [
                        Annotation(
                            id=uuid4(),
                            entity_id=entity.id,
                            location=polygon_from_tlbr(detection.bounds),
                            track_id=track.track_id,
                            observations=observations,
                            data_file_id=data_file_id,
                            datum_source=DatumSource(
                                confidence=1.0,
                                frame_id=detection.frame_id,
                            ),
                        )
                    ]
                    global_observations = []
                    frame_indexed_entities[detection.frame_id][entity.id] = Entity(
                        id=entity.id,
                        annotations=annotations,
                        global_observations=global_observations,
                    )
        raise NotImplementedError("This implementation is a sketch, don't use without adding tests")
        return sorted(frame_indexed_entities.items(), key=lambda kv: kv[0])

    @staticmethod
    def entities_from_deprecated_eavts(eavts: List["EAVT"]) -> Dict[UUID, "Entity"]:
        entities = {}
        if len(eavts) > 0:
            grouped = defaultdict(list)
            for eavt in eavts:
                grouped[eavt.entity_id].append(eavt)
            for group in grouped.values():
                entity_id = group[0].entity_id
                location_eavts = [e for e in group if e.attribute_id == PIXEL_LOCATION_ATTRIBUTE_UUID]
                if len(location_eavts) == 0:
                    entities[entity_id] = Entity(id=entity_id)

                    for eavt in group:
                        obs_id = uuid4()
                        obs = Observation.from_deprecated_eavt(
                            eavt,
                            obs_id,
                        )

                        entities[entity_id].global_observations.add(obs)

                elif len(location_eavts) == 1:
                    location_eavt = location_eavts[0]
                    entity = Entity(id=entity_id)
                    annotation = Annotation(
                        id=uuid4(),
                        # The EAVT 'value' is a PixelLocationAttributeValue
                        # which has a shapely geometry as its 'value'
                        location=location_eavt.value.value,
                        datum_source=location_eavt.datum_source,
                    )

                    for eavt in group:
                        if eavt.attribute_id != PIXEL_LOCATION_ATTRIBUTE_UUID:
                            obs_id = uuid4()
                            obs = Observation.from_deprecated_eavt(
                                eavt,
                                obs_id,
                            )
                            annotation.observations.add(obs)

                    entity.annotations.add(annotation)
                    entities[entity_id] = entity
                else:
                    raise ValueError(
                        f"Can't handle {len(location_eavts)} pixel locations for a single entity"
                    )
        return entities

    def crop_annotations(
        self,
        crop_args: "CropArgs",
        crop_annotations_with: Optional[Union[UUID, Tuple[UUID, Any]]] = None,
    ) -> List[np.ndarray]:
        crops = []
        if crop_annotations_with is None:
            for a in self.annotations:
                crops.append(a.crop(crop_args))
        else:

            if isinstance(crop_annotations_with, UUID):
                value = None
                attribute_id = crop_annotations_with
            else:
                attribute_id, value = crop_annotations_with

            for a in self.annotations:
                if a.has_observation(attribute_id, value=value):
                    crops.append(a.crop(crop_args))

        return crops

    @staticmethod
    def crop_entity_annotations(
        entities: List["Entity"],
        crop_args: "CropArgs",
        crop_annotations_with: Optional[Union[UUID, Tuple[UUID, Any]]] = None,
    ) -> List[np.ndarray]:
        crops = []
        for e in entities:
            crops.extend(e.crop_annotations(crop_args, crop_annotations_with=crop_annotations_with))
        return crops
