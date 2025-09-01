import json
from typing import List, Optional

import click
import yaml
from pydantic import NonNegativeFloat

from ..client import CaseType, HLJSONEncoder, TaskStatusEnum, TaskType, TrainingRunType
from ..core import GQLBaseModel


class UpdateTaskPayload(GQLBaseModel):
    errors: List[str]
    task: Optional[TaskType] = None


@click.group("task")
@click.pass_context
def task_group(ctx):
    pass


@task_group.command("read")
@click.option(
    "-i",
    "--ids",
    type=str,
    required=False,
    multiple=True,
)
@click.option(
    "-t",
    "--task-type",
    type=click.Choice(["TrainModel", "EvaluateAgent"], case_sensitive=True),
    required=False,
)
@click.option(
    "-r",
    "--training-run-id",
    type=int,
    required=False,
)
@click.pass_context
def read(ctx, ids, task_type, training_run_id):
    """Read task(s) by ID"""
    client = ctx.obj["client"]
    result = None

    if not ids and training_run_id is None:
        print("Error: Provide ids or training-run-id")
        return

    if task_type is None:
        result = []
        if len(ids) > 0:
            for id in ids:
                result.append(
                    client.task(
                        return_type=TaskType,
                        id=id,
                    ).gql_dict()
                )
    else:
        # TODO: Refactor once tasks are linked to training runs
        training_run = client.trainingRun(
            return_type=TrainingRunType,
            id=training_run_id,
        ).gql_dict()

        if "trainingConfig" in training_run:
            result = training_run["trainingConfig"]
        else:
            print("Error: no training config found in training run")

    if result is not None:
        click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("create")
@click.option(
    "-p",
    "--workflow-order-id",
    type=str,
    required=True,
    help="Project order ID",
)
@click.option("-f", "--file-ids", type=int, required=True, help="File IDs", multiple=True)
@click.pass_context
def create(ctx, workflow_order_id, file_ids):
    """Create task(s) in a process order"""
    client = ctx.obj["client"]

    class AddFilesToProjectOrderPayload(GQLBaseModel):
        errors: List[str]
        tasks: List[TaskType]

    result = client.addFilesToProjectOrder(
        return_type=AddFilesToProjectOrderPayload,
        projectOrderId=workflow_order_id,
        fileIds=file_ids,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("update")
@click.option(
    "-i",
    "--id",
    type=str,
    required=True,
    help="The IDs of the task to update. Comma separate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    required=False,
    help="The name of this task",
)
@click.option("-d", "--description", type=str, required=False, help="The description of this task")
@click.option(
    "-s",
    "--status",
    type=TaskStatusEnum,
    required=False,
    help="Status of task",
)
@click.option(
    "-t",
    "--tags",
    type=str,
    required=False,
    help="Tags for task",
    multiple=True,
)
@click.option(
    "-p",
    "--parameters",
    type=str,
    required=False,
    help="Aiko task parameters",
)
@click.option(
    "-r",
    "--requested-by-id",
    type=int,
    required=False,
    help="ID of the requester",
)
@click.option(
    "-l",
    "--leased-until",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S%z"]),
    required=False,
    help="When to lease task(s) until",
)
@click.option(
    "-a",
    "--leased-by-agent-id",
    type=str,
    required=False,
    help="ID of the leasing agent",
)
@click.option(
    "-p",
    "--leased-by-pipeline-instance-id",
    type=str,
    required=False,
    help="ID of the leasing pipeline instance",
)
@click.pass_context
def update(
    ctx,
    id,
    name,
    description,
    status,
    tags,
    parameters,
    requested_by_id,
    leased_until,
    leased_by_agent_id,
    leased_by_pipeline_instance_id,
):
    client = ctx.obj["client"]

    if leased_until is not None:
        leased_until = leased_until.isoformat()

    kwargs = {
        k: v
        for k, v in dict(
            name=name,
            description=description,
            status=status,
            tags=tags,
            parameters=parameters,
            leasedUntil=leased_until,
            requestedById=requested_by_id,
            leasedByAgentId=leased_by_agent_id,
            leasedByPipelineInstanceId=leased_by_pipeline_instance_id,
        ).items()
        if v is not None
    }

    for i in id.split(","):
        i = i.strip()

        result = client.updateTask(return_type=UpdateTaskPayload, id=i, **kwargs).gql_dict()

        click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("lease")
@click.option(
    "-i",
    "--id",
    type=str,
    required=False,
    help="The ID of the task to lease",
)
@click.option(
    "-l",
    "--leased-until",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S%z"]),
    required=True,
    help="When to lease task until",
)
@click.option(
    "-a",
    "--leased-by-agent-id",
    type=str,
    required=False,
    help="Agent ID to lease task by",
)
@click.option(
    "-p",
    "--leased-by-pipeline-instance-id",
    type=str,
    required=False,
    help="Pipeline instance ID to lease task by",
)
@click.pass_context
def lease(
    ctx,
    id,
    leased_until,
    leased_by_agent_id,
    leased_by_pipeline_instance_id,
):
    """Lease task"""
    client = ctx.obj["client"]

    if leased_by_agent_id is None and leased_by_pipeline_instance_id is None:
        raise ValueError("Error: One of leased-by-agent-id or leased-by-pipeline-instance-id must be set")

    result = client.updateTask(
        return_type=UpdateTaskPayload,
        id=id,
        leasedUntil=leased_until.isoformat(),
        leasedByAgentId=leased_by_agent_id,
        leasedByPipelineInstanceId=leased_by_pipeline_instance_id,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("re-lease")
@click.option(
    "-i",
    "--id",
    type=str,
    required=False,
    help="The ID of the task to re-lease",
)
@click.option(
    "-l",
    "--leased-until",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S%z"]),
    required=True,
    help="When to lease task until",
)
@click.pass_context
def re_lease(
    ctx,
    id,
    leased_until,
):
    """Re-lease task"""
    client = ctx.obj["client"]

    result = client.updateTask(
        return_type=UpdateTaskPayload,
        id=id,
        leasedUntil=leased_until.isoformat(),
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("mark-with-status")
@click.option(
    "-i",
    "--id",
    type=str,
    required=False,
    help="The ID of the task to re-lease",
)
@click.option(
    "-s",
    "--status",
    type=str,
    required=True,
    help="The status to give the task",
)
@click.pass_context
def mark_with_status(
    ctx,
    id,
    status,
):
    """Mark with status"""
    client = ctx.obj["client"]

    result = client.updateTask(
        return_type=UpdateTaskPayload,
        id=id,
        status=status,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("lease-from-steps")
@click.option(
    "-l",
    "--leased-until",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S%z"]),
    required=True,
    help="When to lease tasks until",
)
@click.option(
    "-a",
    "--leased-by-agent-id",
    type=str,
    required=False,
    help="Agent ID to lease tasks by",
)
@click.option(
    "-p",
    "--leased-by-pipeline-instance-id",
    type=str,
    required=False,
    help="Pipeline instance ID to lease tasks by",
)
@click.option(
    "-s",
    "--step-id",
    type=str,
    required=True,
    help="Lease tasks belonging to step(s)",
    multiple=True,
)
@click.option(
    "-c",
    "--count",
    type=int,
    required=True,
    help="Number of tasks to lease",
)
@click.pass_context
def lease_from_steps(
    ctx,
    leased_until,
    leased_by_agent_id,
    leased_by_pipeline_instance_id,
    step_id,
    count,
):
    """Lease task(s) belonging to step(s)"""
    client = ctx.obj["client"]

    class LeaseTaskPayload(GQLBaseModel):
        errors: List[str]
        tasks: Optional[List[TaskType]] = None

    result = client.leaseTasksFromSteps(
        return_type=LeaseTaskPayload,
        leasedUntil=leased_until.isoformat(),
        leasedByAgentId=leased_by_agent_id,
        leasedByPipelineInstanceId=leased_by_pipeline_instance_id,
        stepIds=step_id,
        count=count,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("unlease")
@click.option(
    "-i",
    "--id",
    type=str,
    required=True,
    help="The ID of the task to unlease",
)
@click.pass_context
def unlease(ctx, id):
    """Unlease task"""
    client = ctx.obj["client"]

    result = client.updateTask(
        return_type=UpdateTaskPayload,
        id=id,
        leasedUntil=None,
        leasedByAgentId=None,
        leasedByPipelineInstanceId=None,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@task_group.command("delete")
@click.option(
    "-i",
    "--id",
    type=str,
    required=True,
    help="The ID of the task to delete",
)
@click.pass_context
def delete(ctx, id):
    """Delete task"""
    client = ctx.obj["client"]

    class DeleteTaskPayload(GQLBaseModel):
        errors: List[str]
        task: Optional[TaskType] = None

    result = client.deleteTask(
        return_type=DeleteTaskPayload,
        id=id,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))
