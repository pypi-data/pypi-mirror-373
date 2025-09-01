import asyncio
import concurrent.futures
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Union

import boto3
import yaml
from aiohttp.client_exceptions import ClientConnectorError
from gql import Client as GQLClient
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import BaseModel

import highlighter.core.decorators as decorators
from highlighter.client._colors import ColoredString

from ..core import snake_to_camel
from .gql_base import (
    Line,
    get_all_mutations,
    get_all_queries,
    get_gql_obj,
    get_gql_return_type,
    get_gql_schema,
    return_type_formatting,
    to_gql_type,
    to_python_type,
)

LOGGER = logging.getLogger(".".join([__name__, "HLClient"]))

cs = ColoredString()


KEY_API_TOKEN = "api_token"  # nosec hardcoded_password_string
KEY_ENDPOINT_URL = "endpoint_url"
KEY_CLOUD = "cloud"

KEY_AWS_ACCESS_KEY_ID = "aws_access_key_id"
KEY_AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"  # nosec hardcoded_password_string
KEY_AWS_REGION = "aws_default_region"

ENV_HL_WEB_GRAPHQL_API_TOKEN = "HL_WEB_GRAPHQL_API_TOKEN"  # nosec hardcoded_password_string
ENV_HL_WEB_GRAPHQL_ENDPOINT = "HL_WEB_GRAPHQL_ENDPOINT"
ENV_AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
ENV_AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"  # nosec hardcoded_password_string
ENV_AWS_DEFAULT_REGION = "AWS_DEFAULT_REGION"

ENV_HL_DEFAULT_PROFILE = "HL_DEFAULT_PROFILE"
ENV_HL_PROFILES_YAML = "HL_PROFILES_YAML"
ENV_HL_GQL_TIMEOUT_SEC = "HL_GQL_TIMEOUT_SEC"

CONST_HLCLIENT_GQL_TIMEOUT_SEC = os.environ.get(ENV_HL_GQL_TIMEOUT_SEC, 60)
CONST_GRAPHQL_DEFAULT_PROFILE = os.environ.get(ENV_HL_DEFAULT_PROFILE, None)
CONST_DEFAULT_GRAPHQL_PROFILES_YAML = Path.home() / ".highlighter-profiles.yaml"

CONST_GRAPHQL_PROFILES_YAML = os.environ.get(ENV_HL_PROFILES_YAML, CONST_DEFAULT_GRAPHQL_PROFILES_YAML)

EXAMPLE_PROFILE = {
    "my-first-profile": {
        KEY_ENDPOINT_URL: "https://<client-account>.highlighter.ai/graphql",
        KEY_API_TOKEN: "123...abc",
    }
}


class S3Creds(BaseModel):
    __type__: str = "aws-s3"
    type: Literal[__type__] = __type__
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str

    def as_environment_variables(self) -> Dict[str, str]:
        return {
            ENV_AWS_ACCESS_KEY_ID: self.aws_access_key_id,
            ENV_AWS_SECRET_ACCESS_KEY: self.aws_secret_access_key,
            ENV_AWS_DEFAULT_REGION: self.aws_default_region,
        }


def validate_cloud_creds(cloud_creds_dict):
    valid_cloud_cred_types = [S3Creds]
    for t in valid_cloud_cred_types:
        try:
            creds = t(**cloud_creds_dict)
            return creds
        except:
            continue  # nosec try_except_continue
    raise ValueError(f"Not a valid cloud credential: {cloud_creds_dict}")


def get_credentials_from_profiles_yaml(
    profile,
    profiles_path=CONST_GRAPHQL_PROFILES_YAML,
):
    if not Path(profiles_path).exists():
        raise FileNotFoundError()

    with open(profiles_path, "r") as f:
        creds = yaml.safe_load(f).get(profile)

    if creds is None:
        raise KeyError(f"Profile '{profile}' could not be found in '{profiles_path}'")

    # Used to access private cloud storage outside of Highlighter S3
    cloud_cred_dicts = creds.get(KEY_CLOUD, None)
    if cloud_cred_dicts is not None:
        cloud_creds = {}
        for cred_dict in cloud_cred_dicts:
            _creds = validate_cloud_creds(cred_dict)
            cloud_creds[_creds.type] = _creds
    else:
        cloud_creds = None

    return creds[KEY_API_TOKEN], creds[KEY_ENDPOINT_URL], cloud_creds


def try_get_existing_asyncio_loop():
    try:
        loop = asyncio.get_running_loop()
    except:
        loop = None

    return loop


class HLClient(object):
    EXECUTION_RETRYS = 10

    # Set to True if running in a notebook or any environment what
    # is running an an async loop
    # Manually set to bool True | False if you wish to override manually
    _async: Union[str, bool] = "AUTO"
    _instance = None

    def __init__(self, client: GQLClient, cloud_creds: Optional[Dict[str, str]] = None):
        self._client = client
        # Lazy-load schema on first use to prevent network request until needed
        self._schema = None
        self._schema_lock = threading.Lock()

        # Used to access private cloud storage outside of Highlighter S3
        self.cloud_creds = cloud_creds
        HLClient._instance = self

    def _ensure_schema(self):
        """Fetch and cache the GraphQL schema once, thread-safely."""
        if self._schema is None:
            with self._schema_lock:
                if self._schema is None:  # double-checked locking
                    self._schema = get_gql_schema(self)

    def refresh_schema(self):
        """Force a re-introspection of the schema (e.g., after server upgrade)."""
        with self._schema_lock:
            self._schema = get_gql_schema(self)

    def set_schema_for_tests(self, schema):
        """Allow tests to inject a stub schema without hitting the network."""
        with self._schema_lock:
            self._schema = schema

    @property
    def schema(self):
        """Public, read-only accessor that ensures the schema is loaded."""
        self._ensure_schema()
        return self._schema

    @classmethod
    def from_profile(cls, profile: str, profiles_path=None) -> "HLClient":
        profiles_path = profiles_path or CONST_DEFAULT_GRAPHQL_PROFILES_YAML
        api_token, endpoint_url, cloud_creds = get_credentials_from_profiles_yaml(
            profile, profiles_path=profiles_path
        )

        return cls.from_credential(api_token, endpoint_url, cloud_creds=cloud_creds)

    @classmethod
    def from_credential(
        cls,
        api_token: str,
        endpoint_url: str,
        cloud_creds: Optional[Dict[str, Any]] = None,
    ) -> "HLClient":
        transport = AIOHTTPTransport(
            url=endpoint_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {api_token}",
            },
        )
        client = GQLClient(
            transport=transport,
            fetch_schema_from_transport=True,
            execute_timeout=CONST_HLCLIENT_GQL_TIMEOUT_SEC,
        )
        return cls(client, cloud_creds=cloud_creds)

    def __repr__(self):
        return f"{self.endpoint_url}: [{self.api_token[:4]}...]"

    @classmethod
    def get_client(cls):
        """Instantiate a HLClient object as needed

        Singelton. If HLClient has already been instantiated this will return
        the existing instance, else will fallback on HLClient.get_client
        """
        if HLClient._instance is not None:
            return HLClient._instance
        return cls.from_env()

    @classmethod
    def clear_instance(cls):
        """Clear singleton instance, typically used in tests"""
        HLClient._instance = None

    @classmethod
    def from_env(cls) -> "HLClient":
        api_token = os.environ[ENV_HL_WEB_GRAPHQL_API_TOKEN]
        endpoint_url = os.environ[ENV_HL_WEB_GRAPHQL_ENDPOINT]
        cloud_creds = cls.cloud_creds_from_env()
        return cls.from_credential(api_token, endpoint_url, cloud_creds=cloud_creds)

    @classmethod
    def cloud_creds_from_env(cls) -> Optional[Dict[str, S3Creds]]:
        session = boto3.Session()
        session_credentials = session.get_credentials()
        aws_default_region = session.region_name
        aws_access_key_id = session_credentials.access_key if session_credentials is not None else None
        aws_secret_access_key = session_credentials.secret_key if session_credentials is not None else None

        if (
            (aws_default_region is not None)
            and (aws_access_key_id is not None)
            and (aws_secret_access_key is not None)
        ):
            cloud_creds = {
                S3Creds.__type__: S3Creds(
                    type=S3Creds.__type__,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_default_region=aws_default_region,
                )
            }
        else:
            cloud_creds = None
        return cloud_creds

    def export_credentials_to_environment(self):
        """Export credentials to environment variables."""
        os.environ[ENV_HL_WEB_GRAPHQL_API_TOKEN] = self.api_token
        os.environ[ENV_HL_WEB_GRAPHQL_ENDPOINT] = self.endpoint_url

        if self.cloud_creds is not None:
            for key, val in self.cloud_creds.items():
                if key == S3Creds.__type__:
                    for var_name, var in val.dict().items():
                        if var_name != "type":
                            os.environ[var_name.upper()] = var

    def append_credentials_to_env_file(self, outfile: str):
        """Append export KEY=VALUE lines for stored credentials"""
        token = self.api_token
        endpoint = self.endpoint_url

        # Token and Endpoint should always be present
        lines = [
            f"export {ENV_HL_WEB_GRAPHQL_API_TOKEN}={token}",
            f"export {ENV_HL_WEB_GRAPHQL_ENDPOINT}={endpoint}",
        ]

        # Cloud creds are optional. They are only needed if the client needs
        # to download data from a 3rd party's cloud bucket

        if self.cloud_creds is not None:
            for cloud_type, creds in self.cloud_creds.items():
                lines.extend(
                    [f"export {key}={value}" for key, value in creds.as_environment_variables().items()]
                )

        with open(str(outfile), "a+") as f:
            f.write("\n".join(lines))

    @property
    def endpoint_url(self):
        return self._client.transport.url

    @property
    def api_token(self):
        return self._client.transport.headers["Authorization"].split()[1]

    @property
    def account_name(self) -> str:
        return self.endpoint_url.split("//")[-1].split(".")[0]

    def get_s3_client(self):
        assert self.cloud_creds is not None
        assert S3Creds.__type__ in self.cloud_creds
        s3_creds = self.cloud_creds[S3Creds.__type__]
        s3_client = boto3.client(
            "s3",
            region_name=s3_creds.aws_default_region,
            aws_access_key_id=s3_creds.aws_access_key_id,
            aws_secret_access_key=s3_creds.aws_secret_access_key,
        )
        return s3_client

    def execute(self, request_str: str, variable_values=None) -> Dict[str, dict]:
        result = None

        LOGGER.debug(f"network_fn_decorator at call time: {decorators.network_fn_decorator}")

        def _execute(request_str: str, variable_values=None):
            LOGGER.debug(f"_execute: {request_str}")
            request_gql = gql(request_str)

            # Change behaviour if an asyncio loop is already running.
            # This is important when running in notebook enviroments.
            # I suggest keeping as "AUTO" but if for somereason you need
            # to maunually set this flag you can
            if self._async == "AUTO":
                loop = try_get_existing_asyncio_loop()
            elif self._async == True:
                loop = asyncio.get_running_loop()
            elif self._async == False:
                loop = None
            else:
                raise ValueError(
                    (
                        f"Invalid value for HLClient._async expected one of: (True, False, 'AUTO'). "
                        f"Got {self._async}"
                    )
                )

            if loop is None:
                result = self._client.execute(request_gql, variable_values=variable_values)
            else:
                # An event loop is already running (probs because this is being run
                # from Jupyter, Spyder or an IPython interpreter
                pool = concurrent.futures.ThreadPoolExecutor()
                result = pool.submit(
                    asyncio.run,
                    self._client.execute_async(
                        request_gql,
                        variable_values=variable_values,
                    ),
                ).result()

            return result

        return decorators.network_fn_decorator(_execute)(request_str, variable_values=variable_values)

    def __getstate__(self):
        state = dict(
            api_token=self.api_token,
            endpoint_url=self.endpoint_url,
            cloud_creds=self.cloud_creds,
        )
        return state

    def __setstate__(self, d):
        client = HLClient.from_credential(**d)
        self.__dict__ = client.__dict__.copy()

    def __getattr__(self, key) -> Callable[..., Any]:
        # methods = vars(type(self))
        # if key in methods:
        #     return methods[key]

        key = snake_to_camel(key)
        schema = self.schema
        if key not in get_all_queries(schema) + get_all_mutations(schema):
            raise ValueError(f"{key} is not a known query or mutation")

        def f(*, return_type: BaseModel, **kwargs):
            return_type_dict = get_gql_return_type(return_type)

            obj_type, target_gql_obj = get_gql_obj(schema, key)

            arg_lst = []
            arg_names = [x["name"] for x in target_gql_obj["args"]]
            for k in kwargs:
                if k not in arg_names:
                    raise ValueError(f"unknown gql argument '{k}' for '{key}'")

            for x in target_gql_obj["args"]:
                if x["name"] in kwargs:
                    arg_lst.append((x["name"], to_gql_type(x["type"])))

            indent = 0
            if len(arg_lst):
                lines = [
                    Line(line="%s _(" % obj_type.lower(), indent=indent),
                    *[Line(line=f"${x}: {t}", indent=indent + 1) for x, t in arg_lst],
                    Line(line=")", indent=indent),
                    Line(line="{", indent=indent),
                    Line(line=f"{key}(", indent=indent + 1),
                    *[Line(line=f"{x}: ${x}", indent=indent + 2) for x, _ in arg_lst],
                    Line(line=f")", indent=indent + 1),
                    *return_type_formatting(return_type_dict, indent + 1),
                    Line(line="}", indent=indent),
                ]
            else:
                lines = [
                    Line(line="%s _" % obj_type.lower(), indent=indent),
                    Line(line="{", indent=indent),
                    Line(line=f"{key}", indent=indent + 1),
                    *return_type_formatting(return_type_dict, indent + 1),
                    Line(line="}", indent=indent),
                ]

            generated_request_str = "\n".join([" " * 4 * x.indent + x.line for x in lines])
            LOGGER.debug(f"executing {obj_type}:\n{generated_request_str}\nWith args {kwargs}")
            response = self.execute(generated_request_str, variable_values=kwargs)
            if "errors" in response:
                raise ValueError(response["errors"])

            result = response[key]
            try:
                return return_type(**result)
            except Exception as e:
                LOGGER.debug(f"response: {response}")
                if getattr(return_type, "_name", None) == "List":
                    # for List[BaseModel]
                    return [return_type.__args__[0](**x) for x in result]
                raise e

        return f

    def hint(self, query_or_mutation: str):
        obj_type, target_gql_obj = get_gql_obj(self.schema, query_or_mutation)
        py_pos_arg_lst = []
        py_key_arg_lst = []
        for x in target_gql_obj["args"]:
            py_type = to_python_type(x["type"])
            if not py_type.startswith("Optional"):
                py_pos_arg_lst.append((x["name"], py_type))
            else:
                py_key_arg_lst.append((x["name"], py_type))

        args = [
            (
                Line(line=f"{n}: {t} = None,", indent=0)
                if t.startswith("Optional")
                else Line(line=cs.yellow(f"{n}: {t},"), indent=0)
            )
            for n, t in py_pos_arg_lst + py_key_arg_lst
        ]
        print(cs.red_black(query_or_mutation))
        print("\n".join([" " * 4 * x.indent + x.line for x in args]))


from threading import local

_thread_local = local()


def get_threadsafe_hlclient(api_token, endpoint_url) -> "HLClient":
    """
    Return a *per-thread* HLClient.

    The first call in each thread creates a fresh HLClient (via from_env);
    subsequent calls re-use that same instance.  Different threads never
    share the underlying gql.Client, so it's safe with the `gql` library.
    """
    if not hasattr(_thread_local, "hl_client"):
        # Pick whichever factory suits your deployment:
        #  - from_env()   : uses HL_* environment variables
        #  - from_profile('dev') : loads ~/.highlighter-profiles.yaml
        _thread_local.hl_client = HLClient.from_credential(api_token, endpoint_url)
    return _thread_local.hl_client
