from typing import Optional
from uuid import UUID

from ...core import GQLBaseModel

__all__ = ["User"]


class User(GQLBaseModel):
    id: int
    display_name: Optional[str] = None
    email: str
    uuid: Optional[UUID] = None
