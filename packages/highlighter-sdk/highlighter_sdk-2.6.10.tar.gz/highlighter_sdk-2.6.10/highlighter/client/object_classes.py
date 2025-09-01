import logging
from typing import Any, Dict, List, Optional

from ..core import GQLBaseModel, LabeledUUID, paginate
from .base_models import ObjectClass, ObjectClassTypeConnection

__all__ = [
    "read_object_classes",
    "create_object_classes",
]

logger = logging.getLogger(__name__)


def read_object_classes(
    client,
    workflow_id: Optional[int] = None,
    **kwargs,
):
    """See graphiql docs for objectClassConnection for current valid arguments"""
    if workflow_id is None:
        return paginate(client.objectClassConnection, ObjectClassTypeConnection, **kwargs)
    else:

        class ProjectType(GQLBaseModel):
            object_classes: List[ObjectClass]

        return client.project(return_type=ProjectType, id=workflow_id).object_classes


def create_object_classes(
    client,
    names: List[str],
) -> Dict[str, LabeledUUID]:
    """Create object classes in a Highlighter account

    Returns a mapping from the names to the Highlighter ObjectClass UUID

    Note:
      Will check for existing names (case incentive) and use the existing
      ObjectClass UUID as necessary
    """

    existing_object_classes = {o.name.lower(): o.uuid for o in read_object_classes(client)}

    class ReturnType(GQLBaseModel):
        errors: Any = None
        object_class: ObjectClass

    name_to_id_lookup = {}
    for name in names:
        _name = name.lower()
        if name in existing_object_classes:
            logger.debug(f"Found existing object class: {_name}")
            name_to_id_lookup[_name] = LabeledUUID(existing_object_classes[_name], label=_name)
        else:
            result = client.createObjectClass(
                return_type=ReturnType,
                name=_name,
                default=False,
            ).object_class
            name_to_id_lookup[result.name] = LabeledUUID(result.uuid, label=result.name)

    return name_to_id_lookup
