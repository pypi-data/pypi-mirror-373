import json
import logging
import os
import sys
from pathlib import Path

import click
import yaml

from highlighter.cli.logging import ColourStr
from highlighter.client import TrainingConfigType, json_tools
from highlighter.client.gql_client import HLClient
from highlighter.client.training_runs import TrainingRunArtefactType
from highlighter.trainers import _scaffold

logger = logging.getLogger(__name__)


def _get_trainer(training_run_dir: Path, hl_training_config: TrainingConfigType):
    with (training_run_dir / ".hl" / "trainer-type").open("r") as f:
        trainer_type = _scaffold.TrainerType(f.readline().strip())

    if (training_run_dir / "trainer.py").exists():
        Trainer = _scaffold.load_trainer_module(training_run_dir).Trainer
    elif "yolo" in trainer_type:
        from highlighter.trainers.yolov11.trainer import YoloV11Trainer as Trainer
    else:
        logger.error(f"Unable to determine trainer from '{trainer_type}'")
        sys.exit(1)
    return Trainer(training_run_dir, hl_training_config, trainer_type)


@click.group("train")
@click.pass_context
def train_group(ctx):
    pass


def _validate_training_run_dir(training_run_dir: Path):
    if not training_run_dir.exists():
        logger.error(f"training_run_dir {training_run_dir} does not exist.")
        sys.exit(1)

    try:
        int(training_run_dir.stem)
        return training_run_dir
    except ValueError:
        logger.error(
            f"Invalid training_run_dir {training_run_dir}. Should be 'ml_training/<TRAINING_RUN_ID>'"
        )
        sys.exit(1)


@train_group.command("start")
@click.argument("training-run-dir", required=False, default=".")
@click.pass_context
def train_start(ctx, training_run_dir):
    """Start model training and generate evaluation metrics.

    Executes the full training pipeline including data preparation, model training,
    and evaluation metric generation. Outputs structured evaluation metrics in JSON
    format for further processing.

    \b
    Args:
        training_run_dir: Directory containing training configuration (default: current directory)

    \b
    Returns:
        Prints training completion message and evaluation metrics in JSON format.
        Also provides command for manual artefact upload if needed.
    """

    client: HLClient = ctx.obj["client"]

    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    combined_ds = trainer.get_datasets(client)

    if trainer.training_data_dir.exists():
        _scaffold.ask_to_remove(trainer.training_data_dir)

    os.chdir(training_run_dir)
    _, artefact_path, _, eval_metric_results = trainer._train(combined_ds)
    click.echo(f"Training {training_run_id} complete")
    click.echo(
        f"{json.dumps({k: e.model_dump() for k,e in eval_metric_results.items()}, cls=json_tools.HLJSONEncoder)}"
    )
    cmd = ColourStr.green(
        f"hl training-run artefact create -i {training_run_id} -a {artefact_path.relative_to(Path.cwd())}"
    )
    click.echo(f"Next run: `{cmd}` to upload to Highlighter")


def _get_object_classes(config):
    with open(config, "r") as f:
        data_yaml_path = yaml.safe_load(f)["data"]
        with open(data_yaml_path, "r") as g:
            classes = yaml.safe_load(g)["names"]

    object_classes = [v for k, v in sorted(classes.items())]
    return object_classes


@train_group.command("evaluate")
@click.argument("training-run-dir", required=False, default=".")
@click.argument("checkpoint", required=True, type=click.Path(dir_okay=False))
@click.argument("config", required=True, type=click.Path(dir_okay=False))
@click.option("--create/--no-create", required=False, type=bool, default=False)
@click.pass_context
def train_evaluate(ctx, training_run_dir, checkpoint, config, create):
    """Evaluate a trained model checkpoint and output structured metrics.

    Evaluates a model checkpoint against validation data and generates evaluation
    metrics in JSON format. Does not upload results to Highlighter - use 'export'
    command for automated upload.

    \b
    Args:
        training_run_dir: Directory containing training configuration (default: current directory)
        checkpoint: Path to model checkpoint file for evaluation
        config: Path to YOLO configuration file
        create: If set will create the metrics results in the Highlighter Research Plan (default: --no-create)

    \b
    Returns:
        Prints evaluation metrics in JSON format
    """
    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    object_classes = _get_object_classes(config)

    eval_metric_results = trainer.evaluate(Path(checkpoint), object_classes, cfg_path=Path(config))
    click.echo(
        f"{json.dumps({k: e.model_dump() for k,e in eval_metric_results.items()}, cls=json_tools.HLJSONEncoder)}"
    )
    if create:
        for m in eval_metric_results.values():
            m.create(client)


@train_group.command("export")
@click.argument("training-run-dir", required=False, default=".")
@click.argument("checkpoint", required=True, type=click.Path(dir_okay=False))
@click.argument("config", required=True, type=click.Path(dir_okay=False))
@click.pass_context
def train_export(ctx, training_run_dir, checkpoint, config):
    """Export model and automatically upload artefact with evaluation metrics.

    This is the main command for finalizing a training run. It exports the model
    to the appropriate format, creates and uploads the training artefact to
    Highlighter, evaluates the model, and automatically uploads all evaluation
    metrics. This streamlined approach eliminates the need for separate manual
    artefact upload steps.

    \b
    Args:
        training_run_dir: Directory containing training configuration (default: current directory)
        checkpoint: Path to model checkpoint file to export
        config: Path to YOLO configuration file

    \b
    Returns:
        Prints artefact upload confirmation with URLs to view results in Highlighter
    """
    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    artefact_path = trainer._export(checkpoint)
    artefact: TrainingRunArtefactType = TrainingRunArtefactType.from_yaml(artefact_path)
    create_artefact_result = artefact.create(client, highlighter_training_config.training_run_id)

    object_classes = _get_object_classes(config)
    eval_metric_results = trainer.evaluate(checkpoint, object_classes, cfg_path=config)

    # create the metric results in Highlighter
    for e in eval_metric_results:
        e.create(client)

    training_run_url = client.endpoint_url.replace(
        "graphql", f"training_runs/{highlighter_training_config.training_run_id}"
    )
    research_plan_url = client.endpoint_url.replace(
        "graphql", f"research_plans/{highlighter_training_config.research_plan_id}"
    )
    msg = ColourStr.green(
        f"Artefact {create_artefact_result.id} uploaded to {training_run_url}.\nSee metric results at {research_plan_url}"
    )
    click.echo(f"{msg}")
