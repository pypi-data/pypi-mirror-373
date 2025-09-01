import click

from highlighter.cli.common import _to_pathlib_make_dir

from ..client import ExperimentType, TrainingRunType, download_bytes


@click.group("experiment")
@click.pass_context
def experiment_group(ctx):
    pass


@experiment_group.command("read")
@click.option(
    "-i",
    "--id",
    type=str,
    required=True,
    help="Id of experiment to download",
)
@click.option(
    "-d",
    "--save-dir",
    type=click.Path(file_okay=True, writable=True),
    required=False,
    default=None,
    callback=_to_pathlib_make_dir,
    help="Directory to save experiment files to",
)
@click.option(
    "-t",
    "--training-run-id",
    type=str,
    required=False,
    help="Id of training run to download",
)
@click.pass_context
def read(ctx, id, save_dir, training_run_id):
    client = ctx.obj["client"]

    result = client.experiment(
        return_type=ExperimentType,
        id=id,
    )
    md_path = str(save_dir / f"experiment_{id}.md")
    result.to_markdown(md_path)

    if training_run_id is not None:
        save_path = save_dir / f"{training_run_id}.tar.gz"
        result = client.trainingRun(
            return_type=TrainingRunType,
            id=training_run_id,
        )

        if save_path is not None:
            download_bytes(
                result.model_implementation_file_url,
                save_path=save_path,
            )
