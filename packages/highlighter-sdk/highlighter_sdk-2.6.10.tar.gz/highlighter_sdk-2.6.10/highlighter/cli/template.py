import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import click
from cookiecutter.generate import generate_context
from cookiecutter.main import cookiecutter
from cookiecutter.prompt import prompt_for_config

from highlighter.cli.logging import ColourStr
from highlighter.client import TrainingConfigType
from highlighter.client.gql_client import HLClient

# register custom filters for cookiecutter
from highlighter.templates.filters import *
from highlighter.trainers import _scaffold


def _do_cookiecutter(tmpdir, template_dir, context_dict):
    dst_dir = Path(tmpdir) / "template"
    shutil.copytree(template_dir, dst_dir)

    cookiecutter_json = dst_dir / "cookiecutter.json"
    with cookiecutter_json.open("w") as f:
        json.dump(context_dict, f)

    # Load the context from the Cookiecutter template
    context = generate_context(context_file=str(cookiecutter_json))
    # Prompt user for inputs
    completed_context = prompt_for_config(context)
    # Render the template
    final_path = cookiecutter(
        str(dst_dir),
        no_input=True,
        extra_context=completed_context,
        output_dir=tmpdir,
    )
    return final_path, completed_context


@click.group("generate")
@click.pass_context
def generate_group(ctx):
    pass


@generate_group.command("agent")
@click.argument(
    "agents_dir", type=click.Path(dir_okay=True, file_okay=False), required=False, default="./agents"
)
@click.pass_context
def agent_generate(ctx, agents_dir):
    """Follow the prompts to create a basic agent definition in the specified
    location.

    \b
    Usage:
        # Generate an agent def json in ./agents/
        hl generate agent

        \b
        # Generate an agent def json in ./foo/bar/
        # if ./foo/bar does not exist it will be created
        hl generate agent ./foo/bar

    \b
    Args:
        agents_dir: Directory to contain your agent definition. Default
        './agents', if it does not exist it will be created.
    """
    template_dir = Path(__file__).parent.parent / "templates" / "agent"

    context_dict = {
        "data_source_type": ["highlighter", "local_text", "local_video", "local_image"],
        "agent_name": "my_agent",
        "_root": "root_dir",
    }

    with TemporaryDirectory() as tmp:
        final_path, completed_context = _do_cookiecutter(tmp, template_dir, context_dict)
        agents_dir = Path(agents_dir)
        agents_dir.mkdir(exist_ok=True, parents=True)
        agent_def_file_name = f'{completed_context["agent_name"]}.json'
        gen_agent_path = Path(final_path) / agent_def_file_name
        new_agent_dest = agents_dir / agent_def_file_name
        _scaffold.safe_move(gen_agent_path, new_agent_dest)
    msg = ColourStr.green(f"Created {completed_context['agent_name']} in {new_agent_dest}")
    click.echo(f"{msg}")


@generate_group.command("capability")
@click.argument("capabilities_dir", type=click.Path(dir_okay=True, file_okay=False), required=True)
@click.pass_context
def capability_generate(ctx, capabilities_dir):
    """Follow the prompts to create the boilerplate for a basic capabilility, and
    optioanlly add it to an existing agent definition

    \b
    Usage:
        # Generate capabilility boilerplate in ./src/PACKAGE_NAME/capabilities/
        hl generate capability

        \b
        # Generate capabilility boilerplate in ./foo/bar/
        # if ./foo/bar does not exist it will be created
        hl generate capabilility ./foo/bar

    \b
    Args:
        capabilities_dir: Directory to put your capabilility. Default
        './src/PACKAGE_NAME/capabilities', if it does not exist it will be created.
    """
    template_dir = Path(__file__).parent.parent / "templates" / "capabilility"

    context_dict = {
        "capability_class_name": "MyCapability",
        "capability_module_name": "{{ cookiecutter.capability_class_name | camel_to_snake }}",
        "capability_description": "Does something cool",
        "_root": "root_dir",
        "_extensions": ["highlighter.templates.filters.camel_to_snake"],
    }

    with TemporaryDirectory() as tmp:
        final_path, completed_context = _do_cookiecutter(tmp, template_dir, context_dict)
        capability_py = f"{completed_context['capability_module_name']}.py"
        gen_capability_path = Path(final_path) / capability_py
        dest_capability_path = Path(capabilities_dir) / capability_py
        _scaffold.safe_move(gen_capability_path, dest_capability_path)
    msg = ColourStr.green(f"Created {completed_context['capability_class_name']} in {dest_capability_path}")
    click.echo(f"{msg}")


@generate_group.command("training-run")
@click.argument("training_run_id", type=int)
@click.argument("trainer", type=click.Choice(list(_scaffold.TrainerType)))
@click.argument(
    "ml_training_dir",
    type=click.Path(dir_okay=True, file_okay=False),
    required=False,
    default="./ml_training",
)
@click.option("--page-size", type=int, default=None)
@click.pass_context
def train_generate(ctx, training_run_id, trainer, ml_training_dir, page_size):
    """Generate the boilerplate for a model training.

    \b
    Usage:
        # Generate training boilerplate for a YOLO Detector in ./ml_training/TRAINING_RUN_ID/
        hl generate training-run TRAINING_RUN_ID yolo-det

        # Generate training boilerplate for a YOLO Detector in ./foo/bar/
        # if ./foo/bar does not exist it will be created
        hl generate training-run TRAINING_RUN_ID yolo-det ./foo/bar

    \b
    Args:
        training_run_id: The id of the Highligher Training Run
        trainer: select from supported trainers
        ml_training_dir: Directory to put your training files. Default
        './ml_training/TRAINING_RUN_ID', if it does not exist it will be created.
    """

    trainer_name = trainer
    ml_training_dir = Path(ml_training_dir)

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, training_run_id)

    training_run_dir = ml_training_dir / str(training_run_id)
    if training_run_dir.exists():
        _scaffold.ask_to_remove(training_run_dir, terminate=True)

    training_run_dir.mkdir(parents=True, exist_ok=False)

    if "yolo" in trainer_name:
        from highlighter.trainers.yolov11 import YoloV11Trainer as Trainer
    else:
        raise ValueError(f"Unable to determine trainer from '{trainer_name}'")

    page_size = page_size if page_size is not None else ctx.obj["hl_cfg"].pagination_page_size
    trainer = Trainer(training_run_dir, highlighter_training_config, trainer_name)
    trainer.generate_boilerplate()
    trainer.get_datasets(client, page_size=page_size)

    click.echo(f"{trainer_name} template generated at {training_run_dir}")
    cmd = ColourStr.green(f"hl train start {training_run_dir}")
    cfg_path = ColourStr.green(f"{trainer.config_path}")
    click.echo(f"OPTIONAL, edit the config at {cfg_path}")
    click.echo(f"Start training with: `{cmd}`")
