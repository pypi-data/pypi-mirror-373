import click
import yaml

from .common import _to_pathlib


@click.group("step")
@click.pass_context
def step_group(ctx):
    pass


@step_group.command("create")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--workflow-id",
    type=str,
    required=True,
)
@click.option(
    "-b",
    "--batch-size",
    type=int,
    required=False,
    default=10,
)
@click.option(
    "--consumable",
    is_flag=True,
)
@click.option(
    "--lockable",
    is_flag=True,
)
@click.option(
    "--capacity",
    type=int,
    required=False,
    default=None,
)
@click.option(
    "--user-ids",
    type=int,
    multiple=True,
)
@click.option(
    "-i",
    "--ids-txt",
    type=click.Path(file_okay=True, writable=False),
    required=True,
    callback=_to_pathlib,
)
@click.pass_context
def create(ctx, name, workflow_id, batch_size, consumable, lockable, capacity, user_ids, ids_txt):
    client = ctx.obj["client"]

    result = client.createImageQueue(return_type=TrainingRunType, id=id)

    result_str = yaml.dump(result.dict())
    print(f"{result_str}")
