from datetime import datetime
from re import sub
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel

from highlighter.client.base_models.base_models import SubmissionType
from highlighter.client.base_models.image import Image
from highlighter.core.hl_base_model import GQLBaseModel, snake_to_camel

from ..core import paginate
from .base_models import SubmissionTypeConnection as SubmissionConnection
from .gql_client import HLClient

__all__ = [
    "get_latest_assessments_gen",
    "get_assessments_gen",
    "create_assessment_with_avro_file",
    "append_data_files_to_not_finalised_assessment",
    "create_assessment_not_finalised",
]


def get_latest_assessments_gen(
    client: HLClient,
    **kwargs,
):
    query_args = {k: v for k, v in kwargs.items() if v is not None}
    assessments_gen = paginate(
        client.latestSubmissionConnection,
        SubmissionConnection,
        **query_args,
    )
    return assessments_gen


def get_assessments_gen(
    client: HLClient,
    **kwargs,
):
    query_args = {k: v for k, v in kwargs.items() if v is not None}
    assessments_gen = paginate(
        client.assessmentConnection,
        SubmissionConnection,
        **query_args,
    )
    return assessments_gen


def create_assessment_with_avro_file(client: HLClient, workflow_id: int, file_id: int, avro_file_info: dict):
    class CreateAssessmentPayload(BaseModel):
        errors: List[str]

    result = client.createAssessment(
        return_type=CreateAssessmentPayload,
        projectId=workflow_id,
        imageId=file_id,
        backgroundInfoLayerFileData=avro_file_info,
        status="completed",
    )
    if len(result.errors) > 0:
        raise RuntimeError(f"Error creating assessment: {result.errors}")


def create_assessment_not_finalised(
    client: HLClient,
    task_id=UUID,
    image_id=int,
    user_id: Optional[int] = None,
    model_id: Optional[int] = None,
    training_run_id: Optional[int] = None,
    data_source_id: Optional[int] = None,
    flag_reason: Optional[str] = None,
    started_at: Optional[str] = None,
) -> SubmissionType:
    kwargs = locals()
    kwargs.pop("client")
    kwargs = {snake_to_camel(k): v for k, v in kwargs.items() if v is not None}

    class CreateSubmissionNotFinalisedPayload(GQLBaseModel):
        errors: Optional[Any]
        submission: SubmissionType

    payload = client.createSubmissionNotFinalised(return_type=CreateSubmissionNotFinalisedPayload, **kwargs)
    if payload.errors:
        raise ValueError(payload.errors)
    return payload.submission


def append_data_files_to_not_finalised_assessment(
    client: HLClient,
    not_finalised_assessment: SubmissionType,
    data_files: List[Image],
) -> SubmissionType:
    kwargs = {
        "submissionId": not_finalised_assessment.id,
        "dataFileIds": [str(d.uuid) for d in data_files],
    }

    class Payload(BaseModel):
        errors: Optional[Any]
        submission: SubmissionType

    payload = client.appendDataFilesToNotFinalisedSubmission(return_type=Payload, **kwargs)
    if payload.errors:
        raise ValueError(payload.errors)

    return payload.submission


def finalise(
    client: HLClient,
    not_finalised_assessment: SubmissionType,
) -> SubmissionType:
    kwargs = {"submissionId": not_finalised_assessment.id}

    class Payload(BaseModel):
        errors: Optional[Any]
        submission: SubmissionType

    payload = client.finaliseSubmissionNotFinalised(return_type=Payload, **kwargs)
    if payload.errors:
        raise ValueError(payload.errors)

    return payload.submission
