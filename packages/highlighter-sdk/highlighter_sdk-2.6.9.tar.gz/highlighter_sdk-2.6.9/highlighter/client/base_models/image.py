from typing import List, Optional
from uuid import UUID

from ...core import GQLBaseModel
from .page_info import PageInfo

__all__ = ["Image", "ImagePresigned", "ImageConnection"]


class Image(GQLBaseModel):
    id: str
    uuid: UUID
    width: Optional[int] = None
    height: Optional[int] = None
    original_source_url: str
    mime_type: str


class ImagePresigned(Image):
    file_url_original: str


class ImageConnection(GQLBaseModel):
    page_info: PageInfo
    nodes: List[ImagePresigned]
