import logging
from dataclasses import field
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from uuid import UUID

import numpy as np
from PIL import Image as PILImage
from pydantic import BaseModel, ConfigDict
from shapely.geometry import Polygon

from highlighter.client.base_models import Observation  # FIXME use data layer
from highlighter.core.enums import ContentTypeEnum

from .. import resize_image

logger = logging.getLogger(__name__)


class DataSample(BaseModel):
    """
    Video / image sample
    """

    content: Optional[bytes | str | np.ndarray | PILImage.Image | Observation] = None
    content_type: ContentTypeEnum = ContentTypeEnum.UNKNOWN
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stream_frame_index: int = 0
    media_frame_index: int = 0
    # TODO: Replace with data_source_id once we re-target annotations and submissions from data_files to data_sources
    data_file_id: Optional[UUID] = None

    # Configure pydantic to allow np.ndarray types
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __post_init__(self):
        if not isinstance(self.content, (bytes, str, np.ndarray, PILImage.Image, Observation)):
            raise ValueError(
                f"Content must be bytes, str, np.ndarray, PIL.Image or Observation, got {type(self.content)}"
            )

    # TODO: handle non image data samples
    def to_ndarray(self) -> np.ndarray:
        """Always return an ``numpy.ndarray`` (H, W, 3, uint8)."""
        if isinstance(self.content, np.ndarray):
            return self.content
        if isinstance(self.content, PILImage.Image):
            return np.asarray(self.content)
        raise TypeError("Unsupported sample type: expected ndarray or PIL.Image.")

    @property
    def wh(self) -> Tuple[int, int]:
        assert self.content_type == "image"
        if isinstance(self.content, np.ndarray):
            h, w = self.content.shape[:2]
        elif isinstance(self.content, PILImage.Image):
            w, h = self.content.size
        else:
            raise ValueError(f"Invalid image type, got {type(self.content)}")
        return w, h

    def resize_content(self, width: int, height: int) -> Union[np.ndarray, PILImage.Image]:
        assert self.content_type == "image"
        return resize_image(self.content, width=width, height=height)

    def crop_content(
        self,
        locations: Union[
            List[Polygon], List[Tuple[int, int, int, int]], List[Tuple[float, float, float, float]]
        ],
        crop_args: Optional["CropArgs"] = None,
    ) -> List[Union[np.ndarray, PILImage.Image]]:
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
