import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import numpy as np
from PIL import Image

from highlighter.client import HLJSONEncoder
from highlighter.client.base_models.entity import Entity
from highlighter.core import LabeledUUID
from highlighter.core.data_models import DataSample

from .base_capability import (
    Capability,
    ContextPipelineElement,
    DataSourceType,
    StreamEvent,
)

__all__ = [
    "EntityWriteFile",
    "WriteStdOut",
    "ImageWriteStdOut",
    "ImageWrite",
    "TextToStdout",
]

# ToDo: The attribute(s) returned by an llm or any model
#       will need to be configured at run time. The the exception
#       of a hand-full of attributes (pixel-location, object-class, ...)
#       we can't know ahead of time what attribute the output of
#       the model will represent.
TEXT_ATTRIBUTE_UUID = LabeledUUID(int=2, label="response")


class BaseEntityWrite(Capability):

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        task_id: str = ""

    def __init__(self, context: ContextPipelineElement):
        super().__init__(context)
        self.frame_entities = dict()

    def get_task_id(self, stream) -> str:
        return stream.variables.get("task_id", None)

    def _get_source_file_location(self, stream):
        # ToDo: Find a better palce to put/get this from
        #       see also, ImageDataSource.process_frame
        source_info = stream.variables.get("source_info", {})
        source_file_location = source_info.get("source_file_location", None)
        if source_file_location is not None:
            return Path(source_file_location)
        return None

    def on_per_frame(self, stream, entities, data_sample):
        pass

    def process_frame(
        self, stream, data_samples: List[DataSample], entities: List[Dict[UUID, Entity]]
    ) -> Tuple[StreamEvent, dict]:
        for frame_entities, data_sample in zip(entities, data_samples):
            self.on_per_frame(stream, frame_entities, data_sample)
        self.frame_entities[stream.frame_id] = entities
        return StreamEvent.OKAY, {}

    def on_stop_stream(self, stream, stream_id, entities):
        """Note this will not be called if you're calling `pipeline.process_frame`
        directly. Because this is called when a stream is stopped
        """
        pass

    def stop_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[Dict]]:
        self.on_stop_stream(stream, stream_id, self.frame_entities)
        return StreamEvent.OKAY, {}


class EntityWriteFile(BaseEntityWrite):

    class DefaultStreamParameters(BaseEntityWrite.DefaultStreamParameters):
        """Can contain the following placeholders:

            {frame_id}
            {task_id}
            {timestamp}

        for example:
            per_frame_output_file = 'output_{frame_id}_{timestamp}.json'
        """

        per_frame_output_file: Optional[str] = None

        """Can contain the following placeholders:

            {task_id}
            {timestamp}
        """
        stop_stream_output_file: Optional[str] = None

    @property
    def per_frame_output_file(self) -> Optional[str]:
        value, _ = self._get_parameter("per_frame_output_file", None)
        return value

    @property
    def stop_stream_output_file(self) -> Optional[str]:
        value, _ = self._get_parameter("stop_stream_output_file", None)
        return value

    def _timestamp(self):
        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    def get_per_frame_output_file_path(self, stream, data_sample):
        task_id = stream.stream_id
        frame_id = data_sample.media_frame_index

        return self.per_frame_output_file.format(
            frame_id=frame_id,
            task_id=task_id,
            timestamp=self._timestamp(),
        )

    def on_per_frame(self, stream, entities, data_sample):
        if self.per_frame_output_file:
            output_file_path = self.get_per_frame_output_file_path(stream, data_sample)
            Path(output_file_path).parent.mkdir(exist_ok=True, parents=True)
            output_str = json.dumps(entities, indent=2, sort_keys=True, cls=HLJSONEncoder)
            with open(output_file_path, "w") as f:
                f.write(output_str)
                self.logger.debug(f"{self.my_id()}: wrote {len(entities)} entities to {output_file_path} ")

    def get_on_stop_stream_output_file_path(self, stream):
        task_id = stream.variables.get("task_id", None)
        return self.stop_stream_output_file.format(
            stream_id=stream.stream_id,
            task_id=task_id,
        )

    def on_stop_stream(self, stream, stream_id, all_entities):
        if self.stop_stream_output_file:
            self.logger.debug(f"Writing stop_stream_output_file: {self.stop_stream_output_file}")
            output_file_path = self.get_on_stop_stream_output_file_path(stream)
            Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file_path, "w") as f:
                f.write(json.dumps(all_entities, indent=2, sort_keys=True, cls=HLJSONEncoder))


class WriteStdOut(BaseEntityWrite):

    def on_per_frame(self, stream, entities, data_samples):

        for entity in entities:
            output = {"frame_data": entity, "frame_id": stream.frame_id}
            print(json.dumps(output), file=sys.stdout, cls=HLJSONEncoder)


class ImageWriteStdOut(Capability):

    def process_frame(self, stream, data_samples: List[DataSourceType]) -> Tuple[StreamEvent, Optional[Dict]]:
        image = data_samples[0].content
        output_buffer = io.BytesIO()
        if isinstance(image, np.ndarray):
            Image.fromarray(image).save(output_buffer, format="PNG")
        elif isinstance(image, Image.Image):
            image.save(output_buffer, format="PNG")

        sys.stdout.buffer.write(output_buffer.getvalue())

        return StreamEvent.OKAY, {}


class ImageWrite(Capability):

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        output_dir: str

        # Can use placeholders, {file_id}, {media_frame_index}, {original_source_url}
        output_pattern: str

    @property
    def output_dir(self) -> str:
        value, _ = self._get_parameter("output_dir")
        return value

    @property
    def output_pattern(self) -> str:
        value, _ = self._get_parameter("output_pattern")
        return value

    def process_frame(self, stream, data_samples: List[DataSample]) -> Tuple[StreamEvent, dict]:
        output_dir = Path(self.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)

        for ds in data_samples:
            filename = self.output_pattern.format(
                file_id=ds.data_file_id,
                media_frame_index=ds.media_frame_index,
                original_source_url=ds.original_source_url,
            )
            dest = output_dir / filename
            image = ds.content
            if isinstance(image, np.ndarray):
                Image.fromarray(image).save(dest)
            elif isinstance(image, Image.Image):
                image.save(dest)

        return StreamEvent.OKAY, {}


class TextToStdout(Capability):
    def process_frame(self, stream, text: str) -> Tuple[StreamEvent, Union[Dict, str]]:
        sys.stdout.write(text)
        # sys.stdout.write(chr(28))  # ASCII 28 (Record Separator)
        sys.stdout.flush()
        return StreamEvent.OKAY, {}
