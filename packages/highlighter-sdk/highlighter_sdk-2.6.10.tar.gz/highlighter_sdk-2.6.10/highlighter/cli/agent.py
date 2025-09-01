import json
import logging
import sys
from typing import List

import click
from aiko_services.main import DEFAULT_STREAM_ID

from highlighter.client import CloudAgent
from highlighter.client.agents import create_agent_token, create_machine_agent_version
from highlighter.client.gql_client import HLClient
from highlighter.client.json_tools import HLJSONEncoder
from highlighter.core.config import HighlighterRuntimeConfigError
from highlighter.core.runtime import DEFAULT_CONTENT_SEPARATOR, Runtime

logger = logging.getLogger(__name__)


@click.group("agent")
@click.pass_context
def agent_group(ctx):
    pass


@agent_group.command("start")
@click.option(
    "--separator",
    "-p",
    type=str,
    default=None,
    help=f"If --expect-filepaths is true the default is '\\n'. Else the the unix file separator '{DEFAULT_CONTENT_SEPARATOR}'. This parameter is only used for piped inputs, if passing paths directly use spaces to separate paths",
)
@click.option("--expect-filepaths", "-f", is_flag=True, default=False)
@click.option("--step-task-ids", "-t", type=str, default=None, help="comma separate for multiple")
@click.option("--step-id", "-i", type=str, default=None)
@click.option("--stream-id", "-s", type=str, default=DEFAULT_STREAM_ID)
@click.option("--dump-definition", type=str, default=None)
@click.option("--allow-non-machine-user", is_flag=True, default=False)
@click.argument("agent_definition", type=click.Path(dir_okay=False, exists=False))
@click.argument("input_data", nargs=-1, type=click.STRING, required=False)
@click.pass_context
def _start(
    ctx,
    separator,
    expect_filepaths,
    step_task_ids,
    step_id,
    stream_id,
    dump_definition,
    allow_non_machine_user,
    agent_definition,
    input_data,
):
    """Start a local Highlighter Agent to process data either from your local machine or from Highlighter tasks.

    When processing local files, a single stream is created to process all files.
    The Agent definition must have its first element as a
    DataSourceCapability, such as ImageDataSource, VideoDataSource,
    TextDataSource, JsonArrayDataSource, etc. The examples below assume
    the use of ImageDataSource.

    When processing Highlighter tasks, a single stream is created for each
    task. The Agent definition should use AssessmentRead as the first element in this case.
    Note: When processing tasks, use a GraphQL API key specific to the agent being run. You can
    create this using 'hl agent create-token'.

    Examples:

      \b
      1. Start an agent against a single image path
      \b
        > hl agent start -f agent-def.json images/123.jpg

      \b
      2. Start an agent against a multiple image paths
      \b
        > find images/ -name *.jpg | hl agent start -f agent-def.json

      \b
      3. Cat the contents of an image to an agent
      \b
        > cat images/123.jpg | hl agent start -f agent-def.json

      \b
      4. Pass data directly to process_frame
      \b
        > hl agent start -f agent-def.json '[{"foo": "bar"},{"foo": "baz"}]'

      \b
      5. Process tasks from a Highlighter machine-step, using a local agent definition
      \b
        > STEP_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        > hl agent start agent-def.json --step-id "$STEP_UUID"

      \b
      6. Process tasks from a Highlighter machine-step, using an agent definition from Highlighter
      \b
        > STEP_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        > AGENT_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        > hl agent start "$AGENT_UUID" --step-id "$STEP_UUID"

    """
    try:
        runtime = Runtime(
            agent_definition=agent_definition,
            input_data=input_data,
            separator=separator,
            expect_filepaths=expect_filepaths,
            step_task_ids=step_task_ids,
            step_id=step_id,
            stream_id=stream_id,
            dump_definition=dump_definition,
            allow_non_machine_user=allow_non_machine_user,
            hl_cfg=ctx.obj.get("hl_cfg"),
            hl_client=ctx.obj.get("client"),
            queue_response=ctx.obj.get("queue_response"),
        )
        runtime.run()
    except HighlighterRuntimeConfigError as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(2)
    except Exception as exc:
        logger.error(exc)
        sys.exit(1)


@agent_group.command("create-token")
@click.option("--machine-agent-version-id", type=str)
@click.option("--machine-agent-name", type=str, required=False)
@click.option("--machine-agent-version-name", type=str, required=False)
def _create_token(
    machine_agent_version_id,
    machine_agent_name,
    machine_agent_version_name,
):
    """Create an access token for an agent

    Once an access token has been created, run an agent with that identity by
    setting `HL_WEB_GRAPHQL_API_TOKEN=<new-token>` before running `hl agent start`

    Either provide the ID of the machine-agent-version in Highlighter, or
    specify a new machine-agent name and version-name to create a new machine-agent-version
    for your agent.
    """
    if machine_agent_version_id is None:
        if machine_agent_name is not None or machine_agent_version_name is not None:
            raise ValueError(
                "Must specify either 'machine_agent_token', give a machine-agent version "
                "ID as the agent definition, or specify both 'machine_agent_name' and "
                "'machine_agent_version'"
            )
        machine_agent_version = create_machine_agent_version(machine_agent_name, machine_agent_version_name)
        machine_agent_version_id = machine_agent_version.id
    machine_agent_token = create_agent_token(machine_agent_version_id)
    # Print to stdout rather than log
    print(machine_agent_token)


@agent_group.command("list")
@click.option("--cloud", is_flag=True)
def _list(cloud):
    """List running agents"""
    if not cloud:
        raise NotImplementedError(
            "Can currently only list agents running in the cloud with the '--cloud' flag"
        )
    try:
        client = HLClient.get_client()
        cloud_agents = client.cloudAgents(return_type=List[CloudAgent])
        print(json.dumps(cloud_agents, indent=4, cls=HLJSONEncoder))
    except Exception as e:
        print(f"Error listing agents. {type(e).__qualname__}: {e}")
