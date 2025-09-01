from datetime import datetime
from typing import List, Tuple
from uuid import UUID, uuid4

from shapely import geometry as geom

from highlighter import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    Annotation,
    DatumSource,
    Entity,
    Observation,
)
from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.core.data_models import DataSample


class MockDetector(Capability):

    def process_frame(self, stream, data_samples: List[DataSample]) -> Tuple[StreamEvent, dict]:
        """Mock detector that creates dummy detections on image or text source data"""

        output_object_class_ids, found = self.get_parameter("output_object_class_ids")
        if not found:
            raise ValueError("'output_object_class_ids' not in element parameters")
        self.output_object_class_ids = [UUID(id) for id in output_object_class_ids]

        if len(data_samples) == 0:
            return StreamEvent.OKAY, {"entities": {}}

        entities = {}
        for data_sample in data_samples:
            if data_sample.content_type.startswith("image"):
                locations = [
                    geom.Polygon([(0, 0), (0, 10), (10, 10), (10, 0)]),
                    geom.Polygon([(100, 100), (100, 110), (110, 110), (110, 100)]),
                ]
            elif data_sample.content_type.startswith("text"):
                locations = [geom.LineString([(0, 0), (10, 0)]), geom.LineString([(100, 100), (110, 100)])]
            else:
                raise ValueError(
                    "MockDetector.process_frame() must be given either 'image' or 'text' data samples"
                )
            for location in locations:
                for object_class_id in self.output_object_class_ids:
                    entity_id = uuid4()
                    entities[entity_id] = Entity(id=entity_id)

                    annotation_datum_source = DatumSource(
                        confidence=1, frame_id=data_sample.media_frame_index
                    )
                    annotation = Annotation(
                        id=uuid4(),
                        location=location,
                        data_file_id=data_sample.data_file_id,
                        datum_source=annotation_datum_source,
                    )
                    entities[entity_id].annotations.add(annotation)

                    observation_datum_source = DatumSource(
                        confidence=1, frame_id=data_sample.media_frame_index
                    )
                    observation = Observation(
                        id=uuid4(),
                        attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                        value=object_class_id,
                        occurred_at=datetime.now(),
                        datum_source=observation_datum_source,
                    )
                    annotation.observations.add(observation)
        return StreamEvent.OKAY, {"entities": entities}
