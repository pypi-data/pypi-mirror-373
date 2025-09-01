import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel
from shapely import wkt
from shapely.geometry import MultiPolygon, Polygon

PathLike = Union[str, Path]


class CocoKeys:
    IMAGE_ID = "image_id"
    ID = "id"
    CAT_ID = "category_id"
    SEG = "segmentation"
    AREA = "area"
    BBOX = "bbox"
    WIDTH = "width"
    HEIGHT = "height"
    EXTRA_FIELDS = "extra_fields"
    FILE_NAME = "file_name"
    IMAGES = "images"
    ANNOS = "annotations"
    CATS = "categories"
    NAME = "name"
    # pycocotools, a common tool for reading/evaluating
    # coco datasets expects this field. TBH I've never used
    # it. Some info here if you're interested:
    # https://github.com/facebookresearch/Detectron/issues/100
    ISCROWD = "iscrowd"


def location_array_to_bbox(location_array):
    """
    [[x0,y0],[x1,y1],...[xn,yn]]
    to
    [x0,y0,w,h]
    """
    xs = [x for [x, y] in location_array]
    ys = [y for [x, y] in location_array]
    xmin, ymin = min(xs), min(ys)
    xmax, ymax = max(xs), max(ys)
    return [xmin, ymin, xmax - xmin, ymax - ymin]


def segmentation_to_location_array(seg):
    """[[x0,y0,x1,y1,x2,y2,x3,y3]]
    to
    [[x0,y0],[x1,y1], [x2,y2], [x3,y3]]

    Note:
    """
    return [[x, y] for x, y in zip(seg[0:-1:2], seg[1::2])]


def segmentation_to_bbox(seg):
    """[[x0,y0,x1,y1,x2,y2,x3,y3]]
    to
    [x0,y0,w,h]
    """
    if len(seg) > 1:
        warnings.warn("segmentation_to_bbox currently only supports " "single polygon, not multipolygons.")
    loc_arr = segmentation_to_location_array(seg[0])
    return location_array_to_bbox(loc_arr)


def _poly_has_interiors(poly):
    """
    Crude check for presence of
    interior polygon
    """
    for i in poly.interiors:
        return True
    return False


def shapely_poly_to_segmentation(poly):
    points = []
    if _poly_has_interiors(poly):
        raise NotImplementedError(
            ("Coco dataset spec does not support interior " f"polygons. ie: Polys with holes, got {poly.wkt}")
        )
    for x, y in zip(*poly.exterior.coords.xy):
        points += [int(x), int(y)]
    return [points[:-2]]


def shapely_multipoly_to_segmentation(multi_poly):
    points = []
    for poly in multi_poly.geoms:
        points.append(
            shapely_poly_to_segmentation(poly)[0],
        )
    return points


def shapely_to_segmentation(shape):
    conversion_fns = {
        Polygon: shapely_poly_to_segmentation,
        MultiPolygon: shapely_multipoly_to_segmentation,
    }
    to_segmentation = conversion_fns.get(type(shape), None)
    if to_segmentation is None:
        raise KeyError((f"Cannot convert shapely geometry '{type(shape)}' to segmentation."))
    else:
        return to_segmentation(shape)


def wkt_to_segmentation(wkt_str):
    """Convert WKT Polygon or MultiPolygon to
    coco segmentation
    ie:
    [[xa0,ya0,xa1,ya1,xa2,ya2,xa3,ya3],
     [xb0,yb0,xb1,yb1,xb2,yb2,xb3,yb3],
     ...]

    """
    shape = wkt.loads(wkt_str)
    return shapely_to_segmentation(shape)


def segmentation_to_wkt(seg: List[List[int]]):
    """Convert segmentation polygon [[x0, y0, x1, y1, ...],...] to a WKT string

    Top left is 0,0
    Positive x-axis is right
    Positive y-axis is down

    If len(seg) == 1:
        Will create a POLYGON WKT string
    else:
        Will create a MULTIPOLYGON WKT string
    """

    def coords(xys):
        _coords = [(x, y) for x, y in zip(xys[:-1:2], xys[1::2])]
        # close the polygon
        _coords.append((xys[0], xys[1]))
        return _coords

    if len(seg) == 1:
        wkt = Polygon(coords(seg[0])).wkt
    else:
        polys = []
        for xys in seg:
            polys.append(Polygon(coords(xys)))
        wkt = MultiPolygon(polys).wkt
    return wkt


def bbox_to_wkt(bbox: Tuple[int, int, int, int]):
    """Convert bounding box x0, y0, w, h to a WKT string

    Top left is 0,0
    Positive x-axis is right
    Positive y-axis is down
    """

    x0, y0, w, h = bbox
    x1 = x0 + w
    y1 = y0 + h
    return segmentation_to_wkt(
        [
            [
                x0,
                y0,
                x1,
                y0,
                x1,
                y1,
                x0,
                y1,
            ]
        ]
    )


def get_bbox_area(bbox):
    x0, y0, w, h = bbox
    return w * h


class CocoImageRecord(BaseModel):
    """The image record from COCO with extensions for Highlighter inter-operability.

    https://cocodataset.org/#format-data

    Unused COCO fields
    - license: int
    - flickr_url: str
    - coco_url: str
    - date_captured: str

    """

    id: int
    # Absolute path to image. COCO uses only file name (not file path), but doesn't
    # keep track of the image directory either. We make the image location explicit
    # by using absolute paths to images.
    file_name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    # Added to schema to allow extensions and interoperability
    # with Highlighter Image.metadata
    extra_fields: Optional[Dict[str, Any]] = None
    # Added so multiple splits can be held in one CocoDataset
    split: Optional[str] = None


class CocoAnnotationRecord(BaseModel):
    """Annotation record format from COCO

    https://cocodataset.org/#format-data

    Un-used COCO fields:
    - iscrowd: int

    """

    id: int
    image_id: int
    category_id: int
    segmentation: List[List[int]]
    area: int
    bbox: List[int]  # [x0,y0,w,h]
    iscrowd: bool = False
    # Added to schema to allow extensions and interoperability
    # with Highlighter AnnotationType.metadata
    extra_fields: Optional[Dict[str, Any]] = None


class CocoCategory(BaseModel):
    id: int
    name: str
    other: Optional[str] = None
