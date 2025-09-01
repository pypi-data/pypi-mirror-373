import json
from pathlib import Path
from typing import List, Tuple, Union
from uuid import uuid4

from highlighter.core.geometry import (
    multipolygon_from_coords,
    polygon_from_left_top_width_height_coords,
)

from ....client import PixelLocationAttributeValue
from ....core import OBJECT_CLASS_ATTRIBUTE_UUID
from ...base_models import AttributeRecord, ImageRecord
from ...interfaces import IReader
from .common import CocoKeys

PathLike = Union[str, Path]


class CocoReader(IReader):
    format_name = "coco"

    def __init__(
        self,
        annotations_file: PathLike,
        bbox_only: bool = False,
        fix_invalid_polygons: bool = False,
    ):
        """Read a coco dataset from disk into highlighter DataFrame format

        By default, the coco reader will preference the segmentation label
        over the bbox label because we can always infer a bbox from a segmentation
        but not vice versa. You can optionally override this behavior by setting
        the bbox_only option to True. This can be useful if the segmentation labels
        are very large and take a long time to parse

        Args:
          annotations_file: Where to save coco json
          bbox_only: Preference bbox label over segmentation

        """
        self.annotations_file = Path(annotations_file)
        self.bbox_only = bbox_only
        self.fix_invalid_polygons = fix_invalid_polygons

    def read(self) -> Tuple[List[AttributeRecord], List[ImageRecord]]:
        with self.annotations_file.open("r") as f:
            coco_data = json.load(f)

        id_to_name = {ele.pop(CocoKeys.ID): ele for ele in coco_data[CocoKeys.CATS]}

        def get_category_name(cat_id):
            return id_to_name[cat_id][CocoKeys.NAME]

        def get_uuid():
            return str(uuid4())

        def get_pixel_location_attribute_value(anno, bbox_only=self.bbox_only):
            if bbox_only:
                poly = polygon_from_left_top_width_height_coords(anno[CocoKeys.BBOX])
                value = PixelLocationAttributeValue.from_geom(poly)

            elif CocoKeys.SEG in anno:
                multi_poly_pts = []
                for seg_xy_flat in anno[CocoKeys.SEG]:
                    seg_xy_pts = [(x, y) for x, y in zip(seg_xy_flat[:-1:2], seg_xy_flat[1::2])]
                    multi_poly_pts.append(seg_xy_pts)
                multipoly = multipolygon_from_coords(
                    multi_poly_pts, fix_invalid_polygons=self.fix_invalid_polygons
                )
                value = PixelLocationAttributeValue.from_geom(multipoly)

            elif CocoKeys.BBOX in anno:
                poly = polygon_from_left_top_width_height_coords(anno[CocoKeys.BBOX])
                value = PixelLocationAttributeValue.from_geom(poly)

            else:
                ValueError(
                    (
                        f"Each coco annotation must have either a {CocoKeys.SEG} or "
                        f"{CocoKeys.BBOX}, got: {anno}"
                    )
                )
            return value

        data_files = {ele.pop(CocoKeys.ID): ele for ele in coco_data[CocoKeys.IMAGES]}

        # Annotations can be polygons or masks. We just want the polygons.
        # https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py#L255
        attribute_records = []
        data_file_records = []
        processed_data_file_ids = set()
        for anno in coco_data[CocoKeys.ANNOS]:
            # print(coco_data[CocoKeys.ANNOS])
            extra_fields = anno.get(CocoKeys.EXTRA_FIELDS, {})
            entity_uuid = extra_fields.pop("entity_id", get_uuid())
            data_file_id = anno[CocoKeys.IMAGE_ID]
            data_file = data_files[data_file_id]

            if data_file_id not in processed_data_file_ids:
                processed_data_file_ids.update([data_file_id])
                data_file_records.append(
                    ImageRecord(
                        data_file_id=data_file_id,
                        width=data_file[CocoKeys.WIDTH],
                        height=data_file[CocoKeys.HEIGHT],
                        filename=data_file[CocoKeys.FILE_NAME],
                        extra_fields=data_file.get(CocoKeys.EXTRA_FIELDS, {}),
                    )
                )

            attribute_records.append(
                AttributeRecord(
                    data_file_id=data_file_id,
                    entity_id=entity_uuid,
                    attribute_id=str(OBJECT_CLASS_ATTRIBUTE_UUID),
                    attribute_name=OBJECT_CLASS_ATTRIBUTE_UUID.label,
                    value=get_category_name(anno[CocoKeys.CAT_ID]),
                )
            )

            attribute_records.append(
                AttributeRecord.from_attribute_value(
                    data_file_id,
                    get_pixel_location_attribute_value(anno),
                    entity_id=entity_uuid,
                )
            )

            for key, value in extra_fields.items():
                attribute_records.append(
                    AttributeRecord(
                        data_file_id=data_file_id,
                        entity_id=entity_uuid,
                        attribute_id=key,
                        attribute_name="ToDo",  # ToDo: Try and lookup from hl
                        value=value,
                    )
                )

        return data_file_records, attribute_records
