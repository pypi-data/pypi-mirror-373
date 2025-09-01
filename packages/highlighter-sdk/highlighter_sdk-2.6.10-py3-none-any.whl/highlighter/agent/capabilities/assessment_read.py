import re
from typing import Literal, Optional, Tuple

import aiko_services as aiko
import pooch
from pydantic import BaseModel, Field

from highlighter import Entity
from highlighter.agent.capabilities import ActorTopic, DataSourceCapability, StreamEvent
from highlighter.agent.capabilities.base_capability import IMAGE, TEXT, VIDEO
from highlighter.agent.capabilities.sources import OutputType, VideoDataSource
from highlighter.client import (
    HLClient,
    SubmissionType,
    read_image_from_url,
    read_text_file_from_url,
)
from highlighter.core.data_models import DataSample

ASSESSMENT_URL_REGEX = (
    r"https://[a-zA-Z0-9_-]+.(?:staging-|sandbox-)?highlighter.ai/oid/assessment/([a-z0-9-]*)"
)


class AssessmentRead(DataSourceCapability):

    class DefaultStreamParameters(DataSourceCapability.DefaultStreamParameters):
        class DataSources(BaseModel):
            class AssessmentDataSource(BaseModel):
                media_type: Literal["highlighter-assessment"] = "highlighter-assessment"
                url: str = Field(pattern=ASSESSMENT_URL_REGEX)

            AssessmentRead: AssessmentDataSource

        data_sources: Optional[DataSources] = None
        output_type: OutputType = OutputType.numpy

    def __init__(self, context):
        super().__init__(context)
        self.client = HLClient.get_client()
        # ToDo: Shold we be calling compose_instance here? Is this someething we could
        # do in highlighter.agent.capabilities:PipelineElement?
        self.video_data_source = aiko.compose_instance(VideoDataSource, {"context": context})
        self.stream_media_types = {}

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, dict]:
        data_sources, _ = self.get_parameter("data_sources")
        assessment_id = re.search(ASSESSMENT_URL_REGEX, data_sources["assessment_read"]["url"])
        if assessment_id is None:
            raise ValueError(
                f"assessment data_source must have the form 'https://<subdomain>.highlighter.ai/oid/assessment/<id>', got: {data_sources['AssessmentRead']['url']}"
            )
        assessment_id = assessment_id.group(1)
        assessment = self.client.submission(return_type=SubmissionType, uuid=str(assessment_id))
        if assessment.background_info_layer_file_cacheable_url is not None:
            # avro_data = hl.io.read_avro_file_from_url(assessment.backgroundInfoLayerFileCacheableUrl)
            # frame_indexed_entities = Entity.frame_indexed_entities_from_avro(assessment)
            self.logger.warning("Not propagating previous assessment for video file")
            entities = {}
        else:
            entities = Entity.entities_from_assessment(assessment)

        data_file_ids = [f.uuid for f in assessment.data_files]

        content_types = [f.mime_type for f in assessment.data_files]
        if len(set(content_types)) > 1:
            raise NotImplementedError("Cannot handle case-files with different content-types")
        content_type = content_types[0]

        if content_type.startswith("image"):
            stream.variables["stream_media_type"] = IMAGE
            data_samples = [
                DataSample(
                    content=read_image_from_url(file_info.file_url_original),
                    content_type="image",
                    data_file_id=file_info.uuid,
                )
                for file_info in assessment.data_files
            ]
            self.pipeline.create_frame(stream, {"data_samples": data_samples, "entities": entities})
            self.pipeline._post_message(ActorTopic.IN, "destroy_stream", [stream_id, True])

        elif content_type.startswith("video"):
            stream.variables["stream_media_type"] = VIDEO
            stream.variables["video_data_file_ids"] = data_file_ids
            video_paths = [
                pooch.retrieve(file_info.file_url_original, None) for file_info in assessment.data_files
            ]
            if len(video_paths) > 1:
                raise NotImplementedError(
                    f"Cannot handle more than 1 video in a case, got {len(video_paths)} videos"
                )
            stream.parameters["data_file_id"] = data_file_ids[0]

            stream.parameters["data_sources"] = aiko.utilities.parser.generate_s_expression(video_paths)

            self.video_data_source.start_stream(stream, stream_id)

        elif content_type.startswith("text"):
            stream.variables["stream_media_type"] = TEXT
            text_data_samples = [
                DataSample(
                    content=read_text_file_from_url(file_info.file_url_original),
                    content_type="text",
                    data_file_id=file_info.uuid,
                )
                for file_info in assessment.data_files
            ]
            self.pipeline.create_frame(stream, {"data_samples": text_data_samples, "entities": entities})
            self.pipeline._post_message(ActorTopic.IN, "destroy_stream", [stream_id, True])

        else:
            raise ValueError(f"Unsupported MIME type: {content_type}")

        return StreamEvent.OKAY, {}

    def process_frame(self, stream, data_samples, entities) -> Tuple[StreamEvent, dict]:
        return StreamEvent.OKAY, {"data_samples": data_samples, "entities": entities}

    def stop_stream(self, stream, stream_id):
        if stream_id in self.stream_media_types:
            if self.stream_media_types[stream_id] == VIDEO:
                self.video_read_file.stop_stream(stream, stream_id)
            del self.stream_media_types[stream_id]
        return StreamEvent.OKAY, {}
