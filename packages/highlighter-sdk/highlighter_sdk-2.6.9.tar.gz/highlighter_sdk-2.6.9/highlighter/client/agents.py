from datetime import datetime
from typing import List, Optional

from ..core import GQLBaseModel
from . import HLClient
from .base_models import MachineAgent, MachineAgentVersion, PipelineInstanceType


def create_machine_agent_version(
    machine_agent_name: str, machine_agent_version_name: str
) -> MachineAgentVersion:
    class CreateMachineAgentPayload(GQLBaseModel):
        errors: List[str]
        machine_agent: MachineAgent

    result = HLClient.get_client().createMachineAgent(
        return_type=CreateMachineAgentPayload,
        name=machine_agent_name,
        machineAgentTypeId="9efdcbce-3434-4b6c-b15b-1f3565899116",  # std_element_pipeline
    )
    if len(result.errors) > 0:
        raise ValueError(f"Error creating machine agent '{machine_agent_name}': {result.errors}")
    machine_agent_id = result.machineAgent.id

    class CreateMachineAgentVersionPayload(GQLBaseModel):
        errors: List[str]
        machine_agent_version: MachineAgentVersion

    result = HLClient.get_client().createMachineAgentVersion(
        return_type=CreateMachineAgentVersionPayload,
        title=machine_agent_version_name,
        code="",
        codeVersion="",
        machineAgentId=machine_agent_id,
        machineAgentTypeId="9efdcbce-3434-4b6c-b15b-1f3565899116",  # std_element_pipeline
    )
    if len(result.errors) > 0:
        raise ValueError(
            f"Error creating machine agent version '{machine_agent_version_name}': {result.errors}"
        )
    return result.machine_agent_version


def create_pipeline_instance(machine_agent_version_id: str, step_id: str) -> str:
    now = datetime.now().isoformat()

    class CreatePipelineInstance(GQLBaseModel):
        errors: List[str]
        pipeline_instance: PipelineInstanceType

    result = HLClient.get_client().createPipelineInstance(
        return_type=CreatePipelineInstance,
        stepId=step_id,
        machineAgentVersionId=machine_agent_version_id,
        reportedStatus="RUNNING",
        startedAt=now,
        lastReportedAt=now,
    )
    if len(result.errors) > 0:
        raise ValueError(f"Could not create pipeline instance in Highlighter: {result.errors}")
    return result.pipeline_instance.id


def update_pipeline_instance(pipeline_instance_id: str, status: str, message: Optional[str] = None):
    class UpdatePipelineInstance(GQLBaseModel):
        errors: List[str]

    result = HLClient.get_client().updatePipelineInstance(
        return_type=UpdatePipelineInstance,
        id=pipeline_instance_id,
        reportedStatus=status,
        lastReportedAt=datetime.now().isoformat(),
        message=message,
    )
    if len(result.errors) > 0:
        raise ValueError(f"Could not update pipeline instance in Highlighter: {result.errors}")


def create_agent_token(machine_agent_version_id: str) -> str:
    class CreateAccessTokenPayload(GQLBaseModel):
        class AccessTokenPayload(GQLBaseModel):
            token: str

        errors: List[str]
        access_token: AccessTokenPayload

    result = HLClient.get_client().createAccessToken(
        return_type=CreateAccessTokenPayload,
        machineAgentVersionId=str(machine_agent_version_id),
    )
    if len(result.errors) > 0:
        raise ValueError(f"Error creating access token for agent: {result.errors}")
    return result.access_token.token
