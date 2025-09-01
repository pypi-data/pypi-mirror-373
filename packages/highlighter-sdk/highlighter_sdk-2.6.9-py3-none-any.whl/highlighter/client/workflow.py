from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from .gql_client import HLClient
from .object_classes import read_object_classes

__all__ = ["create_workflow"]


def create_workflow(
    client: HLClient,
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    object_class_ids: Optional[List[int]] = None,
    object_class_uuids: Optional[List[Union[str, UUID]]] = None,
):
    class Project(BaseModel):
        id: int
        name: str

    class ReturnType(BaseModel):
        errors: Any = None
        project: Optional[Project] = None

    if (object_class_ids is not None) and (object_class_uuids is not None):
        raise ValueError(f"Cannot have both object_class_ids and object_class_uuids")

    if object_class_uuids is not None:
        uuid_strs = [str(u) for u in object_class_uuids]
        object_classes = read_object_classes(client, uuid=uuid_strs)
        object_class_ids = [o.id for o in object_classes]

    result = client.createProject(
        return_type=ReturnType,
        name=name,
        description=description,
        parentId=parent_id,
        objectClassIds=object_class_ids,
    )

    if result.errors:
        raise ValueError(f"{result.errors}")
    return result.project
