<div align="center">
    <img width="640" src="https://highlighter-public.s3.ap-southeast-2.amazonaws.com/web/assets/Highlighter_Logo_Primary_Horizontal_RGB.png" alt="Highlighter logo">
</div>

<br />

<a href=“”></a>
<div align="center">
<a href="https://highlighter-docs.netlify.app/">📘 Documentation</a> |
<a href="#installation">🛠️ Installation</a> |
<a href="mailto:support@highlighter.ai"> 🤔 Reporting Issues</a> 
</div>

<h1>Highlighter SDK</h1>


The Highlighter SDK Python library provides convenient access to the [Highlighter](https://highlighter.ai) API from applications written in Python. There is also a CLI to access the Highlighter API in your shell.

The library also provides other features. For example:

* Easy configuration for fast setup and use across multiple Highlighter accounts.
* Functions to help get datasets in and out of Highlighter
* Helpers for pagination.


# Installation

```console
pip install highlighter-sdk
```


# API Tokens, Environment Variables and Profiles

If you have just a single set of Highlighter credentials you can simply set
the appropriate environment variables.

```
export HL_WEB_GRAPHQL_ENDPOINT="https://<client-account>.highlighter.ai/graphql"
export HL_WEB_GRAPHQL_API_TOKEN="###"

# Only required if you have datasets stored outside Highlighter's managed
# aws s3 storage
export AWS_ACCESS_KEY_ID=###
export AWS_SECRET_ACCESS_KEY=###
export AWS_DEFAULT_REGION=###
```

If you have several Highlighter credentials we suggest you use the
**profiles** option. You can create a `~/.highlighter-profiles.yaml` via the
cli.

```console
hl config create --name my-profile --api-token ### --endpoint https://...
```

Other commands for managing your profiles can be seen with the `--help` flag,

If you're a *Maverick Renegade* you can manage the `~/.highlighter-profiles.yaml`
manually. Below is an example,

```yaml
# Example ~/.highlighter-profiles.yaml

my_profile:
  endpoint_url: https://<client-account>.highlighter.ai/graphql
  api_token: ###

  # Only required if you have datasets stored outside Highlighter's managed
  # aws s3 storage
  cloud:
    - type: aws-s3
      aws_access_key_id: ###
      aws_secret_access_key: ###
      aws_default_region: ###
```

To use as a profile in the cli simply use,

```console
hl --profile <profile-name> <command>
```

In a script you can use,

```python
# in a script
from highlighter.client import HLClient

client = HLClient.from_profile("profile-name")
```

Additionally `HLClient` can be initialized using environment variables or
by passing credentials direcly

```python
from highlighter.client import HLClient

client = HLClient.get_client()

# or

api_token = "###"
endpoint_url = "https://...highligher.ai/graphql
client = HLCient.from_credential(api_token, endpoint_url)
```

Finally, if you are in the position where you want to write a specified profile's
credentials to an evnironment file such as `.env` or `.envrc` you can use
the `write` command. This will create or append to the specified file.

```console
hl --profile my-profile write .envrc
```

## Python API

Once you have a `HLClient` object you can use it perform queries or mutations. Here is a simple example.

```python
from highlighter.client import HLClient
from pydantic import BaseModel

client = HLClient.get_client()

# You don't always need to define your own BaseModels
# many common BaseModels are defined in highlighter.base_models
# this is simply for completeness
class ObjectClassType(BaseModel):
  id: int
  name: str

id = 1234  # add an object class id from you account

result = client.ObjectClass(
    return_type=ObjectClassType,
    id=id,
    )

print(result)
```

Some queries may return arbitrarily many results. These queries are
paginated and are called `Connections` and the queries are named accordingly.
We have provided a `paginate` function to help with these `Connections`

```python
from highlighter.core import paginate
from highlighter.client import HLClient
from pydantic import BaseModel

client = HLClient.get_client()
uuids = [
   "abc123-abc123-abc123-abc123",
   "xyz456-xyz456-xyz456-xyz456",
]

# The following BaseModels are all defined in
# highlighter.base_models. They are simply here
# for completeness
class PageInfo(BaseModel):
    hasNextPage: bool
    endCursor: Optional[str]

class ObjectClass(BaseModel):
    id: str
    uuid: str
    name: str

class ObjectClassTypeConnection(BaseModel):
    pageInfo: PageInfo
    nodes: List[ObjectClass]

generator = paginate(
     client..objectClassConnection,
     ObjectClassTypeConnection,
     uuid=uuids,
     )

for object_class in generator:
  print(object_class)
```

## Datasets

Highlighter SDK provides a dataset representation that can populated
from several sources `{HighlighterWeb.Assessments | Local files {.hdf, records.json, coco.json} | S3Bucket}`.
Once populated the `Highlighter.Datasets` object contains 2 `Pandas.DataFrames`
(`data_files_df` and `annotations_df`) that you can manipulate as required. When you're
ready you can write to disk or upload to Highligher using one of the `Writer` classes
to dump your data to disk in a format that can be consumed by your downstream code.
If you need you can also roll-your-own `Writer` by implementing the `highlighter.datasets.interfaces.IWriter` interface.

## CLI Tab Completion

<table>
    <tr>
        <th>Console</th>
        <td>
        </td>
    </tr>
    <tr>
        <th>Shell</th>
        <td>
          Add this to your <code>~/.bashrc</code>:<br>
          <code>eval "$(_HL_COMPLETE=bash_source hl)"</code><br>
        </td>
    </tr>
    <tr>
        <th>ZSH</th>
        <td>
          Add this to your <code>~/.zshrc</code>:<br>
          <code>eval "$(_HL_COMPLETE=zsh_source hl)"</code><br>
        </td>
    </tr>
    <tr>
        <th>Fish</th>
        <td>
          Add this to <code>~/.config/fish/completions/hl.fish</code>:<br>
          <code>_HL_COMPLETE=fish_source hl | source</code>
        </td>
    </tr>
</table>

For more information, see the [Click documentation](https://click.palletsprojects.com/en/8.1.x/shell-completion/#enabling-completion)

## Documentation

See https://highlighter-docs.netlify.app/
