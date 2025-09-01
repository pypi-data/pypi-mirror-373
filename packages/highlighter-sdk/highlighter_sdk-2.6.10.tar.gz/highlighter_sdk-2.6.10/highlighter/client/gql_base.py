import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from gql.transport.aiohttp import log as aiohttp_logger
from gql.transport.requests import log as request_logger
from pydantic import BaseModel

from highlighter.client._colors import ColoredString
from highlighter.core import snake_to_camel

# These loggers should be set in highlighter
# when they are added we can remove these
LOGLEVEL = os.environ.get("GQL_LOGLEVEL", "WARNING")
request_logger.setLevel(LOGLEVEL)
aiohttp_logger.setLevel(LOGLEVEL)

cs = ColoredString()
gt2pt = {
    "Int": "int",
    "Float": "float",
    "Boolean": "bool",
    "String": "str",
    "ISO8601DateTime": "datetime.datetime",
    "ID": "str",
    "JSON": "str",
}


def get_gql_schema(client: "HLClient"):
    request_str = """
        query IntrospectionQuery {
          __schema {
            queryType {
              name
            }
            mutationType {
              name
            }
            subscriptionType {
              name
            }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args {
                ...InputValue
              }
            }
          }
        }

        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type {
            ...TypeRef
          }
          defaultValue
        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """
    return client.execute(request_str)


class Line(BaseModel):
    indent: int = 0
    line: str


BlankLine = Line(line="\n")


def inner_type(x: Dict) -> Optional[str]:
    def w(x: Optional[Dict]) -> Optional[str]:
        if x is None:
            return None
        if x["ofType"] is None and x["kind"] == "OBJECT":
            return x["name"]
        return w(x["ofType"])

    return w(x["type"])


def to_python_type(x) -> str:
    def recur(x) -> str:
        kind = x["kind"]
        if kind == "SCALAR":
            return gt2pt.get(x["name"]) or x["name"]
        elif kind == "ENUM":
            return "str"

        elif kind == "INPUT_OBJECT":
            return "Dict"

        elif kind == "LIST":
            return f"List[{recur(x['ofType'])}]"

        elif kind == "NON_NULL":
            return recur(x["ofType"])

        else:
            raise ValueError(f"unknown kind {kind} detected")

    result = recur(x)
    if x["kind"] != "NON_NULL":
        result = f"Optional[{result}]"
    return result


def to_gql_type(x) -> str:
    kind = x["kind"]

    if kind in ["SCALAR", "ENUM", "INPUT_OBJECT"]:
        return x["name"]

    elif kind == "LIST":
        return f"[{to_gql_type(x['ofType'])}]"

    elif kind == "NON_NULL":
        return f"{to_gql_type(x['ofType'])}!"

    else:
        raise ValueError(f"tell me what kind we encountered here: {kind}")


def get_all_from(gql_schema: Dict, q_or_m: str) -> List[str]:
    types = gql_schema["__schema"]["types"]
    result = []
    for x in types:
        if x["name"] == q_or_m:
            for y in x["fields"]:
                result.append(y["name"])
    return result


def get_all_mutations(gql_schema: Dict) -> List[str]:
    return get_all_from(gql_schema, "Mutation")


def get_all_queries(gql_schema: Dict) -> List[str]:
    return get_all_from(gql_schema, "Query")


def get_return_type(gql_schema: Dict, name: str, depth=0, max_depth=2) -> Optional[Dict]:
    types = gql_schema["__schema"]["types"]
    if depth > max_depth:
        return None

    target = None
    for x in types:
        if x["name"] == name:
            target = x
            break

    if not target:
        return None

    result = {}
    for x in target["fields"]:
        # print(x)
        it = inner_type(x)
        result[x["name"]] = None
        if it:
            result[x["name"]] = get_return_type(gql_schema, it, depth + 1)
            if result[x["name"]] is None:
                # remove object type in the last object depth
                # solve problem where user -> account  and account -> user
                del result[x["name"]]
    return result


def return_type_formatting(o, indent: int = 0) -> List[Line]:
    result = [Line(line="{", indent=indent)]
    for k in o:
        result.append(Line(line=k, indent=indent + 1))
        nested_obj = o.get(k)
        if nested_obj:
            result.extend(return_type_formatting(nested_obj, indent + 1))

    result.append(Line(line="}", indent=indent))
    return result


def get_gql_obj(gql_schema: Dict, name: str) -> Tuple[str, Dict]:
    types = gql_schema["__schema"]["types"]
    for x in types:
        if x["name"] in ["Query", "Mutation"]:
            for y in x["fields"]:
                if y["name"] == name:
                    return x["name"], y
    raise ValueError(f" {name} not found")


def get_gql_request_str(gql_schema: Dict, name: str, max_depth: int, indent: int = 0) -> List[Line]:
    obj_type, target_gql_obj = get_gql_obj(gql_schema, name)

    arg_lst = []
    for x in target_gql_obj["args"]:
        arg_lst.append((x["name"], to_gql_type(x["type"])))

    # python types
    return_type = inner_type(target_gql_obj)

    result = get_return_type(gql_schema, return_type, max_depth=max_depth)

    return [
        Line(line="%s _(" % obj_type.lower(), indent=indent),
        *[Line(line=f"${x}: {t}", indent=indent + 1) for x, t in arg_lst],
        Line(line=")", indent=indent),
        Line(line="{", indent=indent),
        Line(line=f"{name}(", indent=indent + 1),
        *[Line(line=f"{x}: ${x}", indent=indent + 2) for x, _ in arg_lst],
        Line(line=f")", indent=indent + 1),
        *return_type_formatting(result, indent=indent + 1),
        Line(line="}", indent=indent),
    ]


def get_imports():
    return [
        Line(line="from typing import Optional, List, Dict"),
        Line(line="from gql import gql"),
        Line(line="from client import get_client"),
        Line(line="import datetime"),
        Line(line="from enum import Enum"),
    ]


def get_gql_return_type(b: BaseModel):
    try:
        if getattr(b, "_name", "") in ("List", "Optional"):
            return get_gql_return_type(b.__args__[0])

        elif not issubclass(b, BaseModel):
            return None
    except:
        return None

    result = {}
    for n, f in b.model_fields.items():
        camel_name = snake_to_camel(n)
        result[camel_name] = get_gql_return_type(f.annotation)
    return result
