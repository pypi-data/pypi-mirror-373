import logging
from typing import Dict, List, Optional, Sequence, Tuple, Union
from warnings import warn

import numpy as np
from PIL import Image
from shapely import affinity
from shapely import geometry as geom
from shapely import make_valid
from shapely.ops import unary_union
from shapely.validation import explain_validity

from .exceptions import require_package

try:
    import cv2
except ModuleNotFoundError as _:
    cv2 = None

logger = logging.getLogger(__name__)

__all__ = [
    "get_top_left_bottom_right_coordinates",
    "multipoly_from_mask",
    "multipolygon_from_coords",
    "polygon_from_coords",
    "polygon_from_left_top_width_height_coords",
    "polygon_from_mask",
    "polygon_from_tlbr",
    "try_make_polygon_valid_if_invalid",
    "resize_image",
]


def polygon_from_left_top_width_height_coords(coords: Union[Tuple[float, float, float, float], np.ndarray]):
    """Create a LocationAttributeValue for a box in the form [x,y,w,h]

    Args:
        coords: A sequence of box in the form [x,y,w,h]
    """
    x0, y0, w, h = coords
    x1 = x0 + w
    y1 = y0 + h
    _coords = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
    return geom.Polygon(_coords)


def try_make_polygon_valid_if_invalid(shape):
    if shape.is_valid:
        return shape

    invalid_explaination = explain_validity(shape)
    valid_shape = make_valid(shape)
    if not isinstance(valid_shape, (geom.MultiPolygon, geom.Polygon)):
        raise ValueError(f"Invalid Polygon/MultiPolygon {shape} -> {invalid_explaination}")
    logger.debug(f"Fixed invalid geometry {shape} with {invalid_explaination} to {valid_shape}")

    return valid_shape


def polygon_from_coords(
    coords: Sequence[
        Union[Tuple[float, float], Tuple[float, float, float], np.ndarray, Sequence[geom.Point]]
    ],
    fix_invalid_polygons: bool = False,
):
    """
    Args:
        coords: A sequence of (x, y [,z]) numeric coordinate pairs or triples, or
        an array-like with shape (N, 2) or (N, 3).
        Also can be a sequence of Point objects.
    """
    if len(coords) < 3:
        raise ValueError(f"Polygon must have at least 3 coordinates: {coords}")

    value = geom.Polygon(coords)
    if fix_invalid_polygons:
        value = try_make_polygon_valid_if_invalid(value)
    return value


def polygon_from_tlbr(x: Tuple[int, int, int, int]) -> geom.Polygon:
    """
    from top left bottom right format
    """
    top_left = x[0], x[1]
    top_right = x[2], x[1]
    bottom_right = x[2], x[3]
    bottom_left = x[0], x[3]
    return geom.Polygon(np.array([top_left, top_right, bottom_right, bottom_left]))


def multipolygon_from_coords(
    coords: Sequence[Sequence[Tuple[float, float]]],
    fix_invalid_polygons: bool = False,
):
    """
    Args:
        coords: A nested sequence of (x, y) numeric coordinate pairs, or
        an array-like with shape (N, 2).
    """
    shapes = []
    for poly_xys in coords:
        shape = geom.Polygon(poly_xys)
        if fix_invalid_polygons:
            shape = try_make_polygon_valid_if_invalid(shape)
        shapes.append(shape)

    if len(shapes) == 1:
        value = shapes[0]
    else:
        value = unary_union(shapes)
    return value


def get_top_left_bottom_right_coordinates(
    value: geom.Polygon, scale: float = 1.0, scale_about_origin: bool = True, pad: int = 0
) -> Tuple[int, int, int, int]:
    """
    to top left bottom right format
    """
    bounds: geom.Polygon = geom.box(*value.bounds)

    if scale_about_origin:
        bounds = affinity.scale(bounds, xfact=scale, yfact=scale, origin=(0, 0, 0))
    else:
        bounds = affinity.scale(bounds, xfact=scale, yfact=scale, origin="center")

    bounds = tuple([int(i) for i in bounds.buffer(pad, join_style="bevel").bounds])
    return bounds


@require_package(cv2, "cv2", "opencv")
def polygon_from_mask(
    mask: np.ndarray,
    approx_level: float = 0.01,
    dilate_args: Optional[Dict] = {"kernel": (5, 5), "iterations": 7},
) -> Optional[np.ndarray]:
    """Convert a boolean mask into an nparray of coordinates representing
    a polygon [x0, y0, ... xn, yn]

      coords run anti-clockwise
      coords are approximate
    """
    if dilate_args is not None:

        # Define the dilation kernel
        kernel = np.ones(dilate_args["kernel"], np.uint8)
        mask_as_uint = mask.astype(np.uint8) * 255

        # Dilate the blurred mask
        _mask = cv2.dilate(mask_as_uint, kernel, iterations=dilate_args["iterations"])
    else:
        _mask = mask.astype(np.uint8) * 255

    # JANK OPEN CV VERSION CHECK to account for different cv2.findContours
    # returned tuple size
    contours_tuple = cv2.findContours(_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours_tuple) == 2:
        contours, _ = contours_tuple
    else:
        _, contours, _ = contours_tuple

    if len(contours) > 0:
        cnt = np.concatenate(contours, axis=0)
    else:
        warn("Could not convert mask to polygon points, return None")
        return None

    # FIXME Don't convexify by default?

    if len(contours) > 1:
        # See if I can reduce the number of points:
        cnt = cv2.convexHull(cnt)

    epsilon = approx_level * cv2.arcLength(cnt, True)
    cnt = cv2.approxPolyDP(cnt, epsilon, True)

    if cnt.shape[0] < 3:
        warn("Mask results in invalid polygon points, return None")
        return None

    return np.squeeze(cnt).flatten()


@require_package(cv2, "cv2", "opencv")
def multipoly_from_mask(
    mask: np.ndarray,
    dilate_args: Optional[Dict] = {"kernel": (5, 5), "iterations": 7},
) -> Optional[List[Tuple[int, int]]]:

    if dilate_args is not None:

        # Define the dilation kernel
        kernel = np.ones(dilate_args["kernel"], np.uint8)
        mask_as_uint = mask.astype(np.uint8) * 255

        # Dilate the blurred mask
        _mask = cv2.dilate(mask_as_uint, kernel, iterations=dilate_args["iterations"])
    else:
        _mask = mask.astype(np.uint8) * 255

    # JANK OPEN CV VERSION CHECK to account for different cv2.findContours
    # returned tuple size
    contours_tuple = cv2.findContours(_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours_tuple) == 2:
        contours, _ = contours_tuple
    else:
        _, contours, _ = contours_tuple

    approx = [
        np.squeeze(cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)).reshape((-1, 2))
        for cnt in contours
    ]
    # it's not a valid polygon if it has less than 3 vertices
    approx = [coords for coords in approx if len(coords) > 2]

    if len(approx) == 0:
        return None

    return approx


def resize_image(image: Union[np.ndarray, Image.Image], width: int = 0, height: int = 0):
    """
    Resize an image while maintaining the aspect ratio.

    Args:
        image (numpy.ndarray or PIL.Image.Image): The input image.
        width (int): The desired width (0 to auto-adjust based on height).
        height (int): The desired height (0 to auto-adjust based on width).

    Returns:
        numpy.ndarray or PIL.Image.Image: The resized image.
    """
    if cv2 is None:
        raise OptionalPackageMissingError("cv2", "opencv")

    if isinstance(image, np.ndarray):  # OpenCV (numpy array)
        h, w = image.shape[:2]
    elif isinstance(image, Image.Image):  # PIL Image
        w, h = image.size
    else:
        raise TypeError("Unsupported image type. Use numpy.ndarray or PIL.Image.")

    # Maintain aspect ratio if height or width is zero
    if width == 0 and height > 0:
        scale = height / h
        width = int(w * scale)
    elif height == 0 and width > 0:
        scale = width / w
        height = int(h * scale)
    elif width == 0 and height == 0:
        raise ValueError("Both width and height cannot be zero.")

    # Resize with the appropriate library
    if isinstance(image, np.ndarray):
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    else:
        return image.resize((width, height), Image.Resampling.LANCZOS)
