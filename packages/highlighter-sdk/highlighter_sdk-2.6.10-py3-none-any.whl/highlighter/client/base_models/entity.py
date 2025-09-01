from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import numpy as np
from pydantic import Field
from shapely.wkt import loads as wkt_loads

from highlighter.client.base_models.base_models import SubmissionType
from highlighter.core import GQLBaseModel
from highlighter.core.data_models.data_sample import DataSample
from highlighter.core.geometry import polygon_from_tlbr

from ...core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
)
from .annotation import Annotation
from .base_models import EAVT
from .datum_source import DatumSource
from .observation import Observation
from .validated_set import ValidatedSet


class Entity(GQLBaseModel):
    id: UUID = Field(..., default_factory=uuid4)
    annotations: ValidatedSet[Annotation]
    global_observations: ValidatedSet[Observation]

    def __init__(self, **kwargs):
        annotations = ValidatedSet()
        if "annotations" in kwargs and kwargs["annotations"] is not None:
            for obs in kwargs["annotations"]:
                annotations.append(obs)
        kwargs["annotations"] = annotations
        global_observations = ValidatedSet()
        if "global_observations" in kwargs and kwargs["global_observations"] is not None:
            for obs in kwargs["global_observations"]:
                global_observations.append(obs)
        kwargs["global_observations"] = global_observations
        super().__init__(**kwargs)
        self.annotations.validator = self.validate_add_annotation
        for annotation in self.annotations:
            self.validate_add_annotation(annotation)
        self.global_observations.validator = self.validate_add_global_observation
        for observation in self.global_observations:
            self.validate_add_global_observation(observation)

    def validate_add_annotation(self, new_annotation: Annotation):
        if not isinstance(new_annotation, Annotation):
            raise TypeError(f"Expected annotation, got {type(new_annotation).__qualname__}")

        # Check if update is allowed
        if new_annotation.entity is not None and new_annotation.entity != self:
            raise ValueError(
                "Cannot add annotation that references a different entity. "
                f"Dissasociate the annotation from {new_annotation.entity.id} before adding it to {self.id}"
            )

        # Do associated updates
        new_annotation._entity = self

    def validate_add_global_observation(self, new_observation):
        if not isinstance(new_observation, Observation):
            raise TypeError(f"Expected Observation, got {type(new_observation).__qualname__}")

        # Check if update is allowed
        if (
            new_observation._global_observation_entity is not None
            and new_observation._global_observation_entity != self
        ):
            raise ValueError(
                "Cannot add global observation that references a different entity. "
                f"Dissasociate the observation from entity {new_observation._global_observation_entity.id} "
                f"via `observation.entity = None` before adding it to entity {self.id}."
            )
        if new_observation._annotation is not None:
            raise ValueError(
                "Cannot add global observation that references an annotation. "
                f"Dissasociate the observation from annotation {new_observation._annotation.id} "
                f"via `observation.annotation = None` before adding it to entity {self.id}"
            )

        # Do associated updates
        new_observation._global_observation_entity = self

    def to_json(self):
        data = self.model_dump()
        data["id"] = str(data["id"])
        data["annotations"] = [a.to_json() for a in data["annotations"]]
        data["global_observations"] = [o.to_json() for o in data["global_observations"]]
        return data

    def serialize(self):
        # ToDo: Make this more general
        if self.annotations:
            annotations = [a.serialize() for a in self.annotations]
        else:
            annotations = []

        if self.global_observations:
            global_observations = [o.serialize() for o in self.global_observations]
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
        observations.extend(self.global_observations)
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
                    entity=entity,
                    location=wkt_loads(annotation.location),
                    track_id=annotation.track_id,
                    data_file_id=annotation.data_file_id,
                    datum_source=DatumSource(
                        frame_id=annotation.frame_id,
                        confidence=annotation.confidence,
                    ),
                    correlation_id=annotation.correlation_id,
                )

                Observation(
                    annotation=ann,
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

                for eav in entity_data["observations"][annotation.uuid]:
                    Observation(
                        annotation=ann,
                        attribute_id=eav.entity_attribute_id,
                        value=(
                            eav.value
                            if eav.value is not None
                            else eav.related_entity_id or eav.file_uuid or eav.entity_attribute_enum.id
                        ),
                        occurred_at=eav.occurred_at,
                        datum_source=eav.entity_datum_source,
                    )

            for eav in entity_data["global_observations"]:
                entity.global_observations.add(
                    Observation(
                        entity=entity,
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
    def entities_from_deprecated_eavts(eavts: List[EAVT]) -> Dict[UUID, "Entity"]:
        entities = {}
        if len(eavts) > 0:
            grouped = defaultdict(list)
            for eavt in eavts:
                grouped[eavt.entity_id].append(eavt)
            for group in grouped.values():
                entity = Entity(id=group[0].entity_id)
                entities[entity.id] = entity
                location_eavts = [e for e in group if e.attribute_id == PIXEL_LOCATION_ATTRIBUTE_UUID]
                if len(location_eavts) == 0:
                    for eavt in group:
                        obs = Observation.from_deprecated_eavt(eavt)
                        entity.global_observations.add(obs)

                elif len(location_eavts) == 1:
                    location_eavt = location_eavts[0]
                    annotation = Annotation(
                        entity=entity,
                        # The EAVT 'value' is a PixelLocationAttributeValue
                        # which has a shapely geometry as its 'value'
                        location=location_eavt.value.value,
                        datum_source=location_eavt.datum_source,
                    )

                    for eavt in group:
                        if eavt.attribute_id != PIXEL_LOCATION_ATTRIBUTE_UUID:
                            obs = Observation.from_deprecated_eavt(eavt)
                            annotation.observations.add(obs)

                    entity.annotations.add(annotation)
                else:
                    raise ValueError(
                        f"Can't handle {len(location_eavts)} pixel locations for a single entity"
                    )
        return entities

    def crop_annotations(
        self,
        crop_args: "CropArgs",
        data_sample: DataSample,
        crop_annotations_with: Optional[Union[UUID, Tuple[UUID, Any]]] = None,
    ) -> List[np.ndarray]:
        crops = []
        if crop_annotations_with is None:
            for a in self.annotations:
                crops.append(a.crop(crop_args, data_sample=data_sample))
        else:

            if isinstance(crop_annotations_with, UUID):
                query_args = {"attribute_id": crop_annotations_with}
            else:
                attribute_id, value = crop_annotations_with
                query_args = {"attribute_id": attribute_id, "value": value}

            for a in self.annotations:
                if len(a.observations_where(**query_args)) > 0:
                    crops.append(a.crop(crop_args, data_sample=data_sample))

        return crops

    @staticmethod
    def crop_entity_annotations(
        entities: List["Entity"],
        crop_args: "CropArgs",
        data_sample: DataSample,
        crop_annotations_with: Optional[Union[UUID, Tuple[UUID, Any]]] = None,
    ) -> List[np.ndarray]:
        crops = []
        for e in entities:
            crops.extend(
                e.crop_annotations(
                    crop_args, data_sample=data_sample, crop_annotations_with=crop_annotations_with
                )
            )
        return crops
