from logging import getLogger
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from highlighter.core.exceptions import OptionalPackageMissingError

try:
    import cv2
except ModuleNotFoundError as _:
    raise OptionalPackageMissingError("cv2", "cv2")

import numpy as np
from pydantic import BaseModel

from highlighter.agent.capabilities.base_capability import Capability, StreamEvent
from highlighter.client.base_models.annotation import Annotation
from highlighter.client.base_models.entity import Entity
from highlighter.client.base_models.observation import Observation
from highlighter.client.io import read_image
from highlighter.core.data_models import DataSample

__all__ = ["MatchTemplate", "MatchTemplateCapability"]

logger = getLogger(__name__)


class _MatchTemplateCV2:
    def __init__(self, template: np.ndarray):

        self._t = template

        def fn(gray_frame, template):
            result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
            _, conf, _, max_loc = cv2.minMaxLoc(result)
            return max_loc[0], max_loc[1], conf

        self._fn = fn

    def __call__(self, gray_frame) -> Tuple[int, int, float]:
        return self._fn(gray_frame, self._t)


class MatchTemplate(BaseModel):
    """Match a template image to part of a large input image

    The template matching is done in grayscale color space, if an
    RGB or whatever image is passed in it will be converted to grayscale using
    cv2.cvtColor(..., cv2.COLOR_RGB2GRAY). The unmodified x,y coordinates
    returned by the matching functions corrispond to the top left of the template
    as it is passed over the input image. You can set .offset to augment the
    returned value. MatchTemplate.predict also return the confidence of the match
    which is the matching score for the matched patch.
    """

    template_path: str
    offset: Tuple[int, int] = (0, 0)
    conf_thresh: float = 0.0
    class_lookup: Optional[Dict[int, Tuple[UUID, str]]] = None

    def model_post_init(self, __context) -> None:
        self._template = self._load_template(self.template_path)
        self._match_template = _MatchTemplateCV2(self._template)

    def _load_template(self, template_path) -> np.ndarray:
        t = read_image(template_path)
        return self._rgb_to_gray(t)

    def _rgb_to_gray(self, image):
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    def _predict(self, image: np.ndarray) -> Tuple[int, int, int, int, float]:
        h, w = self._template.shape

        x, y, c = self._match_template(self._rgb_to_gray(image))
        x += self.offset[0]
        y += self.offset[1]
        return (int(x), int(y), int(x + w), int(y + h), c)

    def predict(self, data_samples: List[DataSample], **_) -> List[List[Annotation]]:
        annotations = []
        for d in data_samples:
            x0, y0, x1, y1, c = self._predict(d.content)
            if c < self.conf_thresh:
                logger.debug(f"Dropped: {x0}, {y0}, {x1}, {y1}, {c} < {self.conf_thresh}")
                continue

            anno = Annotation.from_left_top_right_bottom_box(
                (x0, y0, x1, y1),
                c,
                d.data_file_id,
                frame_id=d.media_frame_index,
                pipeline_element_name=self.__class__.__name__,
            )
            obj_uuid, obj_value = (
                self.class_lookup[0] if self.class_lookup else ("Found Template", UUID(int=0))
            )
            obs = Observation.make_object_class_observation(
                obj_uuid,
                obj_value,
                c,
                d.recorded_at,
            )
            anno.observations.add(obs)
            annotations.append([anno])
        return annotations

    def draw_box(self, x, y, box_w, box_h, frame, t=2, color=[255, 0, 0]):

        # Draw red dot at match center
        processed_frame = frame.copy()
        c = np.array(color, dtype=np.uint8)
        processed_frame[y : y + t, x : x + box_w, ...] = c  # draw top of rect
        processed_frame[y + box_h : y + box_h + t, x : x + box_w, ...] = c  # draw bottom of rect
        processed_frame[y : y + box_h, x : x + t, ...] = c  # draw left of rect
        processed_frame[y : y + box_h, x + box_w : x + box_w + t, ...] = c  # draw left of rect

        return processed_frame


class MatchTemplateCapability(Capability):

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        template_path: str
        offset: Tuple[int, int] = (0, 0)
        conf_thresh: float = 0.0
        class_lookup: Optional[Dict[int, Tuple[UUID, str]]] = None

    def __init__(self, context):
        super().__init__(context)

        matcher_args = {}
        for name, field in MatchTemplate.model_fields.items():
            if field.is_required():
                val, found = self._get_parameter(name)
                assert found, f"{name} is required but not found"
                matcher_args[name] = val
            else:
                default = field.default
                val, _ = self._get_parameter(name, default=default)
                matcher_args[name] = val

        self._matcher = MatchTemplate(**matcher_args)

    def process_frame(
        self, stream, data_samples: List[DataSample], entities: Dict[UUID, Entity] = {}
    ) -> Tuple[StreamEvent, dict]:
        annotations = self._matcher.predict(data_samples)
        entities = [a.get_or_create_entity() for anns in annotations for a in anns]
        return StreamEvent.OKAY, {"entities": {e.id: e for e in entities}}
