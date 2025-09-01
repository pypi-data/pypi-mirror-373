from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.core.data_models.data_sample import DataSample
from highlighter.client.base_models.entity import Entity

__all__ = ["{{cookiecutter.capability_class_name}}"]

class {{cookiecutter.capability_class_name}}(Capability):
    """{{cookiecutter.capability_description}}
    """

    def __init__(self, context):
        context.get_implementation("PipelineElement").__init__(self, context)

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        return StreamEvent.OKAY, None

    def process_frame(self, stream, data_samples: List[DataSample], entities: List[Dict[UUID, Entity]]) -> Tuple[StreamEvent, Union[Dict, str]]:
        return StreamEvent.OKAY, {}
