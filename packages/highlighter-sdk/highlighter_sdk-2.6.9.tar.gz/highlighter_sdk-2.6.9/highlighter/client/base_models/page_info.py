from typing import Optional

from ...core import GQLBaseModel

__all__ = ["PageInfo"]


class PageInfo(GQLBaseModel):
    has_next_page: bool
    end_cursor: Optional[str] = None
