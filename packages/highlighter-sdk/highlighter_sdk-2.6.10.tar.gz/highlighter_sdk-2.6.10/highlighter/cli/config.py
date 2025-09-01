from pathlib import Path

import click
import yaml

from ..client.gql_client import (
    CONST_DEFAULT_GRAPHQL_PROFILES_YAML,
    KEY_API_TOKEN,
    KEY_ENDPOINT_URL,
)


@click.group("config")
@click.pass_context
def config_group(ctx):
    """Commands associated with configuration of the Highlighter SDK"""
    pass


NAME_OPTION = click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="Name of the profile you're creating",
)

API_TOKEN_OPTION = click.option(
    "-t",
    "--api-token",
    type=str,
    required=True,
    help="API Token of the profile",
)

ENDPOINT_URL_OPTION = click.option(
    "-u",
    "--endpoint-url",
    type=str,
    required=True,
    help=("Endpoint url of the profile, " "https://<client-account>.highlighter.ai/graphql"),
)


@config_group.command("create")
@click.option(
    "-p",
    "--path",
    type=click.Path(file_okay=True, exists=False),
    required=True,
    default=str(CONST_DEFAULT_GRAPHQL_PROFILES_YAML),
    show_default=True,
    help="If not default location provide path yaml to create",
)
@NAME_OPTION
@API_TOKEN_OPTION
@ENDPOINT_URL_OPTION
def create(path, name, api_token, endpoint_url):
    """Create  a .highlighter-profiles.yaml"""
    if Path(path).exists():
        raise ValueError(f"{path} alread exists. Use 'highlighter config update ...'")

    data = {
        name: {
            KEY_API_TOKEN: api_token,
            KEY_ENDPOINT_URL: endpoint_url,
        }
    }
    with open(path, "w") as f:
        yaml.dump(data, f)


@config_group.command("read")
@click.option(
    "-p",
    "--path",
    type=click.Path(file_okay=True, exists=True),
    required=True,
    default=str(CONST_DEFAULT_GRAPHQL_PROFILES_YAML),
    show_default=True,
)
def read(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    GREEN = "\033[92m"
    RED = "\033[91m"
    CLREND = "\033[0m"
    data = [(account_name, creds) for account_name, creds in data.items()]
    data = sorted(data, key=lambda x: x[0])
    for account_name, creds in data:
        url = creds["endpoint_url"]
        token = creds["api_token"][:4]
        print(f"{GREEN}{account_name}: {CLREND}".ljust(30), end="")
        print(url, end=" ")
        print(f"{RED}[{token}...]{CLREND}")


@config_group.command("update")
@click.option(
    "-p",
    "--path",
    type=click.Path(file_okay=True, exists=True),
    required=True,
    default=str(CONST_DEFAULT_GRAPHQL_PROFILES_YAML),
    show_default=True,
    help="If not default location provide path yaml to update",
)
@NAME_OPTION
@API_TOKEN_OPTION
@ENDPOINT_URL_OPTION
def update(path, name, api_token, endpoint_url):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if data is None:
        data = {}

    data.update(
        {
            name: {
                KEY_API_TOKEN: api_token,
                KEY_ENDPOINT_URL: endpoint_url,
            }
        }
    )

    with open(path, "w") as f:
        yaml.dump(data, f)


@config_group.command("delete")
@click.option(
    "-p",
    "--path",
    type=click.Path(file_okay=True, exists=True),
    required=True,
    default=str(CONST_DEFAULT_GRAPHQL_PROFILES_YAML),
    show_default=True,
    help="If not default location provide path yaml to update",
)
@NAME_OPTION
def delete(path, name):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    del data[name]

    with open(path, "w") as f:
        yaml.dump(data, f)
