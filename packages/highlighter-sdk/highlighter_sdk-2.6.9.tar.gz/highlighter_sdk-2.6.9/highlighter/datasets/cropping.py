from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from highlighter.core.exceptions import require_package

try:
    import cv2
except ModuleNotFoundError as _:
    cv2 = None
import numpy as np
from PIL import Image
from pydantic import BaseModel, field_validator
from shapely import affinity
from shapely import geometry as gm

PathLike = Union[str, Path]
LTRBRect = Tuple[int, int, int, int]

KEY_CROP_ROTATED_RECT = "crop_rotated_rect"

__all__ = [
    "CropArgs",
    "KEY_CROP_ROTATED_RECT",
    "crop_rect_from_poly",
    "crop_rectangle",
    "crop_rotated_rectangle",
]


class CropArgs(BaseModel):
    crop_rotated_rect: Optional[bool] = False
    scale: Optional[float] = None
    pad: Optional[int] = None
    warped_wh: Optional[Union[Tuple[int, int], List[int]]] = None

    @field_validator("warped_wh")
    @classmethod
    def _validate_warped_wh(cls, v):
        """If warped_wh is not None make sure it's a list and not a tuple
        because tuple is not json/safe_yaml serializable.
        """

        if isinstance(v, tuple):
            v = list(v)

        if v is not None:
            assert isinstance(v, tuple)
            assert len(v) == 2
        return v

    def dict(self, **kwargs):
        d = super().model_dump(**kwargs)
        if not self.crop_rotated_rect:
            d.pop("warped_wh")
        return d


def _get_wh_of_rotated_rect(np_corners: np.ndarray) -> Tuple[int, int]:
    # First 3 corners of the rectangle
    a, b, c = np_corners[0], np_corners[1], np_corners[2]
    ab = int(round(np.linalg.norm(b - a)))
    bc = int(round(np.linalg.norm(c - b)))
    if ab >= bc:
        w, h = ab, bc
    else:
        w, h = bc, ab

    return w, h


def _order_rect_points_bottom_left_ccw(rect: gm.Polygon) -> gm.Polygon:
    # 0. Note, the origin for Shapely is the bottom left with
    #    the positive x and y axis right and up respectivally.
    #    But, our coordinates have the origin at the top left
    #    and positive x,y being rigth and down.
    #    So our top right and clockwise will translate to shapely's
    #    Bottom left and counter-clockwise. See below for an illustration
    #
    #    Shapely coords:
    #
    #    +y
    #    |
    #    | 0,1      2,1
    #    * * * * * *
    #    *         *
    #    * * * * * * --- +x
    #     0,0      2,0

    #    Highlighter coords:
    #
    #     0,0      2,0
    #    * * * * * * --- +x
    #    *         *
    #    * * * * * *
    #    |0,1      2,1
    #    |
    #    +y
    #
    #
    # The following uses the shapely coordinate system, that way, if we
    # look for bottom left and order ccw we should be golden
    #
    # 1. Find the edges that belong to the major axis (longest)
    # 2. Select the bottom edge
    # 3. Find the left most point of the bottom edge
    # 4. Set bottom left point to 0th index
    # 5. remaining points follow ccw

    rect_points = np.array(rect.exterior.coords)[:-1]

    # Find major axis
    a, b, c, d = 0, 1, 2, 3
    x, y = 0, 1
    ab = gm.LineString((rect_points[a], rect_points[b]))
    bc = gm.LineString((rect_points[b], rect_points[c]))
    cd = gm.LineString((rect_points[c], rect_points[d]))
    da = gm.LineString((rect_points[d], rect_points[a]))
    edges = np.array([ab, bc, cd, da])
    longest = edges[np.argsort([edge.length for edge in edges])[-2:]]

    edge_0 = np.array(longest[0].coords)
    edge_1 = np.array(longest[1].coords)

    # Find bottom edge
    if edge_0[..., y].min() < edge_1[..., y].min():
        bottom_edge = edge_0
        top_edge = edge_1
    else:
        bottom_edge = edge_1
        top_edge = edge_0

    # arrange points starting from the left most point of the bottom
    # edge and moving counter clockwise
    if bottom_edge[0][x] > bottom_edge[1][x]:
        bottom_edge = bottom_edge[[1, 0]]
        top_edge = top_edge[[1, 0]]

    return gm.Polygon(bottom_edge.tolist() + top_edge.tolist())


def crop_rect_from_poly(
    data_file: Union[np.ndarray, Image.Image],
    poly: gm.Polygon,
    crop_args: Optional[Union[CropArgs, Dict]] = None,
) -> Union[np.ndarray, Image.Image]:
    crop_fns = {
        False: crop_rectangle,
        True: crop_rotated_rectangle,
    }

    if crop_args is None:
        crop_args = {}

    if isinstance(crop_args, dict):
        crop_args = CropArgs(**crop_args)
    elif not isinstance(crop_args, CropArgs):
        raise ValueError(f"invalid parameter 'crop_args' expected a CropArgs object, got {crop_args}")

    kwargs = crop_args.dict()

    crop_rotated_rect = kwargs.pop(KEY_CROP_ROTATED_RECT)

    return crop_fns[crop_rotated_rect](data_file, poly, **kwargs)


@require_package(cv2, "cv2", "opencv")
def crop_rotated_rectangle(
    data_file: Union[np.ndarray, Image.Image],
    poly: gm.Polygon,
    scale: Optional[float] = None,
    pad: Optional[int] = None,
    warped_wh: Optional[Tuple[int, int]] = None,
) -> Union[np.ndarray, Image.Image]:
    """Find the minimum_rotated_rectange for the input poly and apply
    cv2.warpPerspective to transform to to rectangular crop of shape warped_wh

    see: https://shapely.readthedocs.io/en/stable/manual.html#object.minimum_rotated_rectangle

    Resulting crops will be of the same type as the input data_file (np.ndarray | PIL.Image)

    Args:
        data_file: Source data_file
        poly: Polygon to crop out
        scale: (Optional) factor applied to poly before cropping about the origin
        pad: Optional pad (in pixels) applied to poly before cropping
        warped_wh: The desired output shape of the crop
    """
    assert isinstance(pad, int) or (
        pad is None
    ), f"Croping rotated rec only support a int for 'pad', got: {pad}"

    rot_rect = poly.minimum_rotated_rectangle

    if scale is not None:
        rot_rect = affinity.scale(rot_rect, xfact=scale, yfact=scale, origin=(0, 0, 0))

    if pad is not None:
        rot_rect = rot_rect.buffer(pad, join_style=2)

    # Shapely uses a different coordinate system to us and opencv.
    # We need to make sure the points in the src_points corrispond to
    # the points in dst_points, hence this function is needed. More detail in
    # its doc string.
    rot_rect = _order_rect_points_bottom_left_ccw(rot_rect)
    src_points = np.array(list(zip(*rot_rect.exterior.coords.xy)))[:-1].astype(np.float32)

    if warped_wh is None:
        warped_wh = _get_wh_of_rotated_rect(src_points)
    w, h = warped_wh

    dst_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)

    transform_mat = cv2.getPerspectiveTransform(src_points, dst_points)

    if isinstance(data_file, Image.Image):
        src = np.array(data_file)
    elif isinstance(data_file, np.ndarray):
        src = data_file
    else:
        raise ValueError(f"Invalid data_file intput type: {type(data_file)}")

    out = cv2.warpPerspective(src, transform_mat, warped_wh, flags=cv2.INTER_LINEAR)

    return out if isinstance(data_file, np.ndarray) else Image.fromarray(out)


def crop_rectangle(
    data_file: Union[np.ndarray, Image.Image],
    rect: Union[LTRBRect, gm.Polygon],
    scale: Optional[float] = None,
    pad: Optional[int] = None,
) -> Union[np.ndarray, Image.Image]:
    """Crop an XY Axis aligned rectangle crop data_file

    Resulting crops will be of the same type as the input data_file (np.ndarray | PIL.Image)

    Args:
        data_file: Source data_file
        rect: Left, Top, Right, Bottom tuple representing the rectangle to crop
        scale: Optional factor applied to rect before cropping
        pad: Optional pad (in pixels) applied to rect before cropping

    Note: Pillow.Image.crop does not give a 💩 if a crop goes out-of-bounds
    it will just add zeros as needed.
    """
    if isinstance(rect, gm.Polygon):
        rect = rect.bounds

    if scale is not None:
        rect = [x * scale for x in rect]

    if pad is None:
        pad = (0, 0)
    elif isinstance(pad, (float, int)):
        pad = (int(pad), int(pad))
    assert isinstance(pad, tuple)

    def pad_rect(rect, w_pad, h_pad):
        l, t, r, b = rect
        l -= w_pad
        r += w_pad
        t -= h_pad
        b += h_pad
        return (l, t, r, b)

    l, t, r, b = rect
    l, t, r, b = pad_rect((l, t, r, b), *pad)

    if isinstance(data_file, Image.Image):
        crop = data_file.crop((l, t, r, b))
    elif isinstance(data_file, np.ndarray):
        crop = Image.fromarray(data_file).crop((l, t, r, b))
        crop = np.array(crop, dtype=data_file.dtype)
    else:
        raise ValueError(f"Invalid data_file intput type: {type(data_file)}")
    return crop
