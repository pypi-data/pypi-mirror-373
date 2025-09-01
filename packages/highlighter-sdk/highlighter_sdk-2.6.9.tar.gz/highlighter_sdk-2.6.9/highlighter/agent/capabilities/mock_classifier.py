from typing import Any, Dict, List, Tuple
from uuid import UUID

from highlighter import DatumSource, Entity, Observation
from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.core.data_models import DataSample


class MockClassifier(Capability):
    """Mock classifier that creates a dummy observation"""

    def process_frame(
        self, stream, entities: Dict[UUID, Entity], data_samples: List[DataSample]
    ) -> Tuple[StreamEvent, dict]:
        # When we specify the output taxonomy of the element in the
        # pipeline element outputs then we can get it from there. For now
        # we add it to the parameters
        output_attribute_id, found = self.get_parameter("output_attribute_id")
        if not found:
            raise ValueError("'output_attribute_id' not in element parameters")
        self.output_attribute_id = UUID(output_attribute_id)
        output_enum_id, found = self.get_parameter("output_enum_id")
        if not found:
            raise ValueError("'output_enum_id' not in element parameters")
        self.output_enum_id = UUID(output_enum_id)

        for entity_id, entity in entities.items():
            for annotation in entity.annotations:
                datum_source = DatumSource(confidence=1, frame_id=annotation.datum_source.frame_id)
                obs = Observation(
                    attribute_id=self.output_attribute_id,
                    value=self.output_enum_id,
                    datum_source=datum_source,
                )
                obs.entity_id = entity_id
                annotation.observations.add(obs)
        return StreamEvent.OKAY, {"entities": entities}
