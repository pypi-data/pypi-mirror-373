from typing import List

from ...core import GQLBaseModel
from .page_info import PageInfo

__all__ = ["ObjectClass", "ObjectClassTypeConnection"]


class ObjectClass(GQLBaseModel):
    id: str
    uuid: str
    name: str


class ObjectClassTypeConnection(GQLBaseModel):
    page_info: PageInfo
    nodes: List[ObjectClass]
