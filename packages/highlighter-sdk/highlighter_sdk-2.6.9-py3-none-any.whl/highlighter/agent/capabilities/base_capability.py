import threading
from datetime import datetime, timezone
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from uuid import UUID

import aiko_services as aiko
from aiko_services import (
    PROTOCOL_PIPELINE,
    ActorTopic,
)
from aiko_services import DataSource as AikoDataSource
from aiko_services import (
    PipelineImpl,
    StreamEvent,
    StreamState,
    compose_instance,
    pipeline_args,
    pipeline_element_args,
)
from pydantic import BaseModel
from sqlmodel import Session

from highlighter.agent.capabilities.data_sample_processor import (
    DataSampleProcessor,
    RecordMode,
)
from highlighter.client.base_models.annotation import Annotation
from highlighter.client.base_models.entity import Entity
from highlighter.client.base_models.observation import Observation
from highlighter.core.data_models.data_sample import DataSample
from highlighter.core.enums import ContentTypeEnum

__all__ = [
    "ActorTopic",
    "Capability",
    "DataSourceCapability",
    "ContextPipelineElement",
    "EntityUUID",
    "PROTOCOL_PIPELINE",
    "PipelineElement",
    "PipelineImpl",
    "StreamEvent",
    "StreamState",
    "compose_instance",
    "compose_instance",
    "pipeline_args",
    "pipeline_element_args",
]

VIDEO = "VIDEO"
TEXT = "TEXT"
IMAGE = "IMAGE"

EntityUUID = UUID

"""Decouple the rest of the code from aiko.PipelineElement"""
ContextPipelineElement = aiko.ContextPipelineElement
PipelineElement = aiko.PipelineElement

# SEPARATOR = b"\x1c"  # ASCII 28 (File Separator)
SEPARATOR = 28  # ASCII 28 (File Separator)


class _BaseCapability:
    class DefaultStreamParameters(BaseModel):
        """Populate with default stream param key fields"""

        pass

    @classmethod
    def default_stream_parameters(cls) -> BaseModel:
        return {
            k: v.default for k, v in cls.DefaultStreamParameters.model_fields.items() if not v.is_required()
        }

    def _get_parameter(
        self, name, default=None, required=False, use_pipeline=True, self_share_priority=True
    ) -> Tuple[Any, bool]:
        """Adds the correct output type to get_parameter type checking
        does not complain
        """
        if default is None:
            default = self.default_stream_parameters().get(name)
        return self.get_parameter(
            name,
            default=default,
            required=required,
            use_pipeline=use_pipeline,
            self_share_priority=self_share_priority,
        )


class _AppendableIterator:
    def __init__(self):
        """Initialize the iterator with an optional list of initial items."""
        self._items = Queue(maxsize=10)

    def __iter__(self):
        """Make the class iterable."""
        return self

    def __next__(self):
        """Return the next item in the sequence or raise StopIteration."""
        try:
            item = self._items.get(timeout=10)
        except Empty:
            raise StopIteration
        return item

    def append(self, item):
        """Append an item to the underlying list."""
        self._items.put(item)


class Capability(PipelineElement, _BaseCapability):

    _observation_data_samples = _AppendableIterator()
    _dsp = None

    class DefaultStreamParameters(_BaseCapability.DefaultStreamParameters):
        # recorder_args: Must be set at the agent level
        #     data_source_uuid: UUID   # associate DataFiles with a source
        #     account_uuid: UUID       # (replace with real IDs in prod)
        #     samples_per_file: int    # batch size
        #     record: RecordMode       # local, cloud, off, both
        pass

    @property
    def recorder_args(self) -> dict:
        class RecorderArgs(BaseModel):
            account_uuid: UUID
            data_source_uuid: UUID
            samples_per_file: int
            record: RecordMode

        recorder_args_names = [
            "account_uuid",
            "data_source_uuid",
            "samples_per_file",
            "record",
        ]
        _recorder_args = {}
        for k, v in self.pipeline.definition.parameters.items():
            if k in recorder_args_names:
                _recorder_args[k] = v

        if len(_recorder_args) == 0:
            # Not set
            self.logger.debug("Recorder args are not set, recording disabled")
            result = None
        elif len(_recorder_args) < len(recorder_args_names):
            # Partially set
            self.logger.warning(
                f"Recorder args are partially set, expected all '{recorder_args_names}'. recording disabled"
            )
            result = None
        else:
            result = RecorderArgs(**_recorder_args).model_dump()
        return result

    def __init__(self, context: aiko.ContextPipelineElement):
        context.get_implementation("PipelineElement").__init__(self, context)

    def process_frame(self, stream, *args) -> Tuple[StreamEvent, dict]:
        raise NotImplementedError()

    def start_stream(self, stream, stream_id, use_create_frame=True):
        validated_parameters = self.DefaultStreamParameters(**self.parameters)
        for param_name in self.DefaultStreamParameters.model_fields:
            self.parameters[f"{self.definition.name}.{param_name}"] = getattr(
                validated_parameters, param_name
            )
            # FIXME: Solve parameter handling properly
        stream.parameters.update(self.parameters)

        recorder_args = self.recorder_args
        if recorder_args is not None:
            database = stream.parameters.get("database", None)
            record = recorder_args.get("record", RecordMode.OFF)
            if record != RecordMode.OFF and database is None:
                raise ValueError("Missing 'database', required when recording")

            if (record is not RecordMode.OFF) and (Capability._dsp is None):
                self.logger.info(f"Recording to {record}")
                Capability._dsp = DataSampleProcessor(
                    iterator=Capability._observation_data_samples,
                    session_factory=lambda: Session(database.engine),
                    content_type=ContentTypeEnum.OBSERVATION,
                    **self.recorder_args,
                )
        return StreamEvent.OKAY, {}

    def stop_stream(self, stream, stream_id):
        if Capability._dsp is not None:
            Capability._dsp.flush()  # Blocks until dsp worker thread exits
        return StreamEvent.OKAY, None

    def record_observations(self, observations: List[Observation]):
        assert isinstance(observations, list), f"Observation must be list got: {observations}"
        if self.recorder_args and self.recorder_args.get("record", RecordMode.OFF) is not RecordMode.OFF:
            # self.logger.info(f"Recording: {len(observations)}, {observations[0].datum_source.frame_id}")
            for o in observations:
                Capability._observation_data_samples.append(
                    DataSample(
                        content=o,
                        content_type=ContentTypeEnum.OBSERVATION,
                        recorded_at=o.occurred_at,
                        stream_frame_index=o.datum_source.frame_id,
                        media_frame_index=o.datum_source.frame_id,
                    )
                )
                next(Capability._dsp)
                # Remove from identity map. This will not delete the object. It
                # will simply remove the reference from the IdentityMap so it
                # does not hold onto it indefinately.
                # FIXME: Remove the old data layer work entirely
                # FIXME: Have to think about how to properly clean up IdentityMap
                # if we remove the Entity and/or Annotation the Observation.annotation
                # or Observation.entity will not work, because it needs to lookup
                # the given instance by id from the IdentityMap
                # Entity.remove_by_id(o.entity_id)
                # Annotation.remove_by_id(o.annotation_id)
                Observation.remove_by_id(o.get_id())


# ToDO: Remove
class DataSourceType(BaseModel):
    # class MediaType(str, Enum):
    #    IMAGE = "IMAGE"
    #    TEXT = "TEXT"
    #    VIDEO = "VIDEO"

    media_type: str
    url: str
    id: UUID
    content: Optional[Any] = None

    @classmethod
    def image_iter(cls, images: Iterable[Union[str, Path, bytes]]):
        pass

    @classmethod
    def video_iter(cls, videos: Iterable[Union[str, Path, bytes]]):
        pass

    @classmethod
    def text_iter(cls, tests: Iterable[Union[str, Path, bytes]]):
        pass


class DataSourceCapability(AikoDataSource, _BaseCapability):

    stream_media_type = None

    class DefaultStreamParameters(_BaseCapability.DefaultStreamParameters):

        rate: Optional[float] = None
        batch_size: int = 1
        data_sources: Optional[str] = None
        file_ids: Optional[Iterable] = None
        task_id: Optional[UUID] = None

    @property
    def rate(self) -> float:
        return self._get_parameter("rate")[0]

    @property
    def batch_size(self) -> int:
        return self._get_parameter("batch_size")[0]

    def __init__(self, context: aiko.ContextPipelineElement):
        context.get_implementation("PipelineElement").__init__(self, context)

    def frame_generator(self, stream, pipeline_iter_idx):
        """Produce a batch of frames.

        Args:
            stream: The Stream context
            pipeline_iter_idx: An integer counting the number of times the
                               pipeline has been executed, (ie: process_frame
                               has been called)

        """
        if stream.variables["disable_create_frame_event"].is_set():
            return StreamEvent.STOP, {"diagnostic": "Frame generation disabled"}

        batch_size = self.batch_size
        task_id, _ = self._get_parameter("task_id")

        frame_data_batch = {"data_samples": [], "entities": {}}
        for _ in range(batch_size):
            try:
                data_sample, entities = self.get_next_data_sample(stream)
                frame_data_batch["data_samples"].append(data_sample)
                frame_data_batch["entities"].update(entities)
                self.logger.debug(f"data_sample: {data_sample}, entities: {entities}")
            except StopIteration:
                pass
            except Exception as e:
                return StreamEvent.ERROR, {"diagnostic": e}

        if not frame_data_batch["data_samples"]:
            return StreamEvent.STOP, {"diagnostic": "All frames generated"}

        # For each pipeline iteration the is a batch of file_ids and frame_ids
        stream.variables["task_id"] = task_id

        return StreamEvent.OKAY, frame_data_batch

    def start_stream(self, stream, stream_id):
        stream.variables["video_capture"] = None
        stream.variables["video_frame_generator"] = None

        stream.variables["disable_create_frame_event"] = threading.Event()

        return super().start_stream(
            stream, stream_id, frame_generator=self.frame_generator, use_create_frame=False
        )

    def stop_stream(self, stream, stream_id):
        stream.variables["disable_create_frame_event"].set()
        return super().stop_stream(stream, stream_id)

    def get_next_data_sample(self, stream):
        raise NotImplementedError()

    def process_frame(
        self, stream, data_samples, entities: Optional[Dict] = None
    ) -> Tuple[StreamEvent, Dict]:
        return StreamEvent.OKAY, {
            "data_samples": data_samples,
            "entities": entities if entities is not None else {},
        }

    def using_hl_data_scheme(self, stream) -> bool:
        return "hl_source_data" in stream.variables
