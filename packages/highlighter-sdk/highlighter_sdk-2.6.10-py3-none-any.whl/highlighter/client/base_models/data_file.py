import warnings
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
from uuid import UUID

import numpy as np
from PIL import Image
from shapely.geometry import Polygon

from ...core import GQLBaseModel, draw_annotations_on_image, resize_image

__all__ = ["DataFile"]

warnings.simplefilter("always", DeprecationWarning)  # Force showing deprecation warnings


class DataFile(GQLBaseModel):
    file_id: Optional[UUID] = None
    content_type: str
    content: Any
    recorded_at: datetime = datetime.now()
    media_frame_index: int = 0
    original_source_url: Optional[str] = None

    @classmethod
    def from_image(
        cls,
        content: Union[np.ndarray, Image.Image, str, Path],
        file_id: UUID,
        media_frame_index: int = 0,
        original_source_url: Optional[str] = None,
    ):
        if isinstance(content, (str, Path)):
            content = Image.open(content)

        assert isinstance(content, (np.ndarray, Image.Image))

        return cls(
            file_id=file_id,
            content_type="image",
            content=content,
            media_frame_index=media_frame_index,
            original_source_url=original_source_url,
        )

    def get_id(self) -> UUID:
        return self.file_id

    @property
    def wh(self) -> Tuple[int, int]:
        assert self.content_type == "image"
        if isinstance(self.content, np.ndarray):
            h, w = self.content.shape[:2]
        elif isinstance(self.content, Image.Image):
            w, h = self.content.size
        else:
            raise ValueError(f"Invalid image type, got {type(self.content)}")
        return w, h

    def resize(self, width: int, height: int) -> "DataFile":
        assert self.content_type == "image"
        self.content = resize_image(self.content, width=width, height=height)
        return self

    def crop_content(
        self,
        locations: Union[
            List[Polygon], List[Tuple[int, int, int, int]], List[Tuple[float, float, float, float]]
        ],
        crop_args: Optional["CropArgs"] = None,
    ) -> List[Union[np.ndarray, Image.Image]]:
        from highlighter.datasets.cropping import crop_rect_from_poly

        assert self.content_type == "image"

        if isinstance(locations[0], tuple) and isinstance(locations[0][0], float):
            ori_w, ori_h = self.wh
            polys = [
                Polygon(
                    [
                        (int(x0 * ori_w), int(y0 * ori_h)),
                        (int(x1 * ori_w), int(y0 * ori_h)),
                        (int(x1 * ori_w), int(y1 * ori_h)),
                        (int(x0 * ori_w), int(y1 * ori_h)),
                        (int(x0 * ori_w), int(y0 * ori_h)),
                    ]
                )
                for x0, y0, x1, y1 in locations
            ]
        elif isinstance(locations[0], tuple) and isinstance(locations[0][0], int):
            ori_w, ori_h = self.wh
            polys = [
                Polygon(
                    [
                        (x0, y0),
                        (x1, y0),
                        (x1, y1),
                        (x0, y1),
                        (x0, y0),
                    ]
                )
                for x0, y0, x1, y1 in locations
            ]
        elif isinstance(locations[0], Polygon):
            polys = locations
        else:
            raise ValueError(f"Invalid crop locations, got, {locations}.")
        return [crop_rect_from_poly(self.content, p, crop_args) for p in polys]

    def draw_annotations(self, annotations: "Annotations"):
        overlay = draw_annotations_on_image(self.content, annotations)
        return overlay

    class ContentTypeEnum(Enum):
        UNKNOWN = "unknown"
        IMAGE = "image"
        VIDEO = "video"
        TEXT = "text"
        JSON = "json"
        AUDIO = "audio"
        WEB_PAGE = "web_page"
        KML = "kml"
