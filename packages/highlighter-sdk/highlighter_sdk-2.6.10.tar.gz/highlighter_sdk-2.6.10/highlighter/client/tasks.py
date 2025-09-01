from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from highlighter.client.base_models import SubmissionType
from highlighter.client.gql_client import HLClient
from highlighter.core.gql_base_model import GQLBaseModel

__all__ = [
    "update_task_status",
    "update_task",
    "lease_task",
    "lease_tasks_from_steps",
    "update_task_result",
]


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

    @staticmethod
    def validate_str(s) -> bool:
        return s in [s.value for s in TaskStatus]


class UpdateTaskResultPayload(GQLBaseModel):
    submission: SubmissionType
    errors: List[Any]


class Case(GQLBaseModel):
    class CaseSubmission(GQLBaseModel):
        class DataFile(GQLBaseModel):
            uuid: str
            original_source_url: str
            file_url_original: str
            content_type: str

        id: str
        uuid: UUID
        data_files: List[DataFile]

    id: str
    latest_submission: CaseSubmission
    entity_id: Optional[str] = None


class Task(GQLBaseModel):
    id: str
    status: Optional[TaskStatus] = None
    case: Optional[Case] = None
    leased_until: Optional[datetime] = None
    parameters: Optional[Dict[str, Any]] = None


def update_task_result(
    client: HLClient,
    task_id: str,
    status: str,
    observations: List[Dict] = [],
    background_info_layer_file_data: Optional[Dict] = None,
):
    assert isinstance(status, TaskStatus) or TaskStatus.validate_str(status), f"Got: {status}"

    kwargs = {
        "id": task_id,
        "status": status,
        "eavtAttributes": observations,
    }
    if background_info_layer_file_data is not None:
        kwargs["backgroundInfoLayerFileData"] = background_info_layer_file_data

    result = client.updateTaskResultV2(return_type=UpdateTaskResultPayload, **kwargs)
    return result


def update_task_status(
    client: HLClient,
    task_id: str,
    status: Union[str, TaskStatus],
    message: Optional[str] = None,
):

    assert isinstance(status, TaskStatus) or TaskStatus.validate_str(status), f"Got: {status}"

    class UpdateTaskStatusResponse(GQLBaseModel):
        errors: List[Any]

    kwargs = {
        "id": task_id,
        "status": status,
    }
    if message is not None:
        kwargs["message"] = message

    response = client.update_task_status(return_type=UpdateTaskStatusResponse, **kwargs)
    if response.errors:
        raise ValueError(f"{response.errors}")

    return response


def update_task(
    client: HLClient,
    task_id: Union[UUID, str],
    status: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[int] = None,
    **kwargs,
) -> Task:

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        task: Task
        errors: Any

    kwargs = dict(
        id=str(task_id),
        status=status,
        leasedUntil=leased_until,
        **kwargs,
    )

    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    response = client.updateTask(return_type=TaskResponse, **kwargs)

    if response.errors:
        raise ValueError(f"Errors: {response.errors}")

    return response.task


def lease_task(
    client: HLClient,
    task_id: Union[UUID, str],
    set_status_to: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[int] = None,
) -> Task:

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        task: Task
        errors: Any

    update_task_args = {"id": str(task_id), "leasedUntil": leased_until}
    if set_status_to is not None:
        update_task_args["status"] = set_status_to
    response = client.updateTask(return_type=TaskResponse, **update_task_args)
    if response.errors:
        raise ValueError(f"Errors: {response.errors}")
    return response.task


def lease_tasks_from_steps(
    client: HLClient,
    step_ids: List[Union[UUID, str]],
    count: int = 1,
    filter_by_status: Optional[Union[str, TaskStatus]] = None,
    set_status_to: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[float] = None,
    filter_by_task_id: Optional[List[UUID]] = None,
) -> List[Task]:

    if filter_by_status:
        assert isinstance(filter_by_status, TaskStatus) or TaskStatus.validate_str(filter_by_status)

    if set_status_to:
        assert isinstance(set_status_to, TaskStatus) or TaskStatus.validate_str(set_status_to)

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        errors: List[Any]
        tasks: List[Task]

    response = client.leaseTasksFromSteps(
        return_type=TaskResponse,
        stepIds=[str(s) for s in step_ids],
        count=count,
        leasedUntil=leased_until,
    )

    if len(response.errors) > 0:
        raise ValueError(response.errors)

    if filter_by_status:
        tasks = [t for t in response.tasks if t.status == filter_by_status]
    else:
        tasks = response.tasks

    if filter_by_task_id:
        task_ids = []

        for i in filter_by_task_id:
            if isinstance(i, str):
                task_ids.append(i)
            elif isinstance(i, UUID):
                task_ids.append(str(i))
            else:
                raise ValueError()

        tasks = [t for t in tasks if t.id in task_ids]

    if set_status_to:
        for task in tasks:
            _ = update_task_status(client, task.id, set_status_to)
    return tasks


if __name__ == "__main__":
    x = lease_tasks_from_steps(
        HLClient.from_profile("haplomic"),
        ["87f57909-c8e0-412b-b117-59a170920460"],
        # leased_until="2024-09-24T05:05:55+0000",
        lease_sec=10,
        filter_by_status="PENDING",
        count=5,
    )

    print(x)
