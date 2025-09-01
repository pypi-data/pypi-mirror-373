import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from shapely import wkt

from ....core import OBJECT_CLASS_ATTRIBUTE_UUID, PIXEL_LOCATION_ATTRIBUTE_UUID
from ...interfaces import IWriter
from .common import (
    CocoAnnotationRecord,
    CocoCategory,
    CocoImageRecord,
    get_bbox_area,
    segmentation_to_bbox,
    shapely_to_segmentation,
)

PathLike = Union[str, Path]


def validate_categories(
    categories: List[CocoCategory],
    unique_object_classes,
):
    # Validate no duplicate ids
    unique_ids = set([c.id for c in categories])
    if len(unique_ids) != len(categories):
        raise ValueError(f"Got dupliate category ids in: {categories}")

    # Validate ids are consecutive an start at 1
    if not all([a == b for a, b in zip(sorted(unique_ids), range(0, len(unique_ids)))]):
        raise ValueError("category.id are not consecutive and starting at 1 got: " f"{categories}")

    # Validate all unique_object_classes are accounted for in
    # categories
    category_names = [c.name for c in categories]
    if (len(category_names) != len(unique_object_classes)) or (
        len(set(category_names) - set(unique_object_classes)) > 0
    ):
        diff_table = _tabulate_list_diff(
            sorted(category_names), sorted(unique_object_classes), "coco_categories", "hl dataset classes"
        )
        raise ValueError(f"categories dont match unique_object_classes, got: \n{diff_table}")

    return categories


def _tabulate_list_diff(a, b, a_title, b_title):
    """Create a readable diff for 2 lists

    abc | abc
    xyz | ---
    --- | foo
    bar | bar

    """
    ab = sorted(set(a + b))
    left_cols = []
    right_cols = []
    for ele in ab:
        left_cols.append(ele if ele in a else "-" * len(ele))
        right_cols.append(ele if ele in b else "-" * len(ele))

    table = [f"{a_title:<40} | {b_title}"]
    table.extend([f"{l:40} | {r}" for l, r in zip(left_cols, right_cols)])
    return "\n".join(table)


class CocoWriter(IWriter):
    format_name = "coco"
    annotation_count = -1
    image_count = -1

    def __init__(
        self,
        annotations_dir: PathLike,
        category_attribute_id: str = OBJECT_CLASS_ATTRIBUTE_UUID,
        categories: Optional[List[Union[CocoCategory, Dict]]] = None,
    ):
        """Write annotations files.

        Args:
            annotations_dir: the dir to store the JSON file
            class_attribute_intentifier: value from the annotations_df.attribute_id  column select categories from
            categories: value from the annotations_df.values column to use as categories

            TODO: negative_sampling: if True, create bbox with (0, 0, 0, 0) in annotation for negative sampling
              creating 'pure' COCO JSON files.

        Example:
            | data_file_id | attribute_id | value |
            | ------------ | ------------ | ----- |
            | 001          | 1            | a     |
            | 001          | 1            | c     |
            | 001          | 2            | x     |
            | 002          | 1            | a     |
            | 002          | 1            | b     |
            | 002          | 2            | y     |

            If category_attribute_id="1" and categories=None
            the we would create a coco dataset with the categories [a,b,c]

            If category_attribute_id="1" and categories=[a,c]
            the we would create a coco dataset with the categories [a,c]

            If category_attribute_id="2" and categories=None
            the we would create a coco dataset with the categories [x,y]
        """
        self.annotations_dir = Path(annotations_dir)
        self.category_attribute_id = category_attribute_id

        def to_base_model(c):
            if isinstance(c, dict):
                return CocoCategory(**c)
            return c

        # Ensure we're working with the CocoCategory BaseModel
        if categories is None:
            self.categories = None
        else:
            self.categories: List[CocoCategory] = [to_base_model(c) for c in categories]

    def write(
        self,
        dataset: "Dataset",
    ):
        self.annotations_dir.mkdir(parents=True, exist_ok=True)

        unique_object_classes = dataset.annotations_df[
            dataset.annotations_df.attribute_id == self.category_attribute_id
        ].value.unique()

        # sort so datasets with the same object_classes
        # have identical 'categories' when saved to Coco format.
        # This assures when using different datasets (ie train and test)
        # that were download separately that the categories are alligned
        # so evaluation works. This can be overridden by using the optional
        # categories arg
        unique_object_classes.sort()

        # Allign categories with passed in categories
        # else fall back on sorted unique_object_classes
        if self.categories is not None:
            self.categories = validate_categories(self.categories, unique_object_classes)
            self.categories = sorted(self.categories, key=lambda c: c.id)
            self.object_class_value_to_cat_id = {}
            self.coco_categories = []
            for cat in self.categories:
                self.coco_categories.append(cat.dict())
                self.object_class_value_to_cat_id[cat.name] = cat.id

        else:
            self.object_class_value_to_cat_id = {
                object_class: i for i, object_class in enumerate(unique_object_classes)
            }

            self.coco_categories = [
                {"id": i, "name": object_class} for i, object_class in enumerate(unique_object_classes)
            ]

        def to_coco_annotation(grp):
            entity_id = grp.name
            if grp.shape[0] != grp.attribute_id.unique().shape[0]:
                print(f"WANING: DROPING DUPLICATE ROWS for entity: {grp.name}")
                grp = grp.drop_duplicates(subset=["attribute_id"])

            data = grp.set_index("attribute_id").to_dict("index")

            # Initially try both uuid and label
            # we'll probs just move to uuid I think
            object_class_attr = data.pop(
                OBJECT_CLASS_ATTRIBUTE_UUID,
                data.pop(str(OBJECT_CLASS_ATTRIBUTE_UUID), data.pop(OBJECT_CLASS_ATTRIBUTE_UUID.label, None)),
            )

            if object_class_attr is None:
                print((f"entity: {entity_id}, No OBJECT_CLASS"))
                # "expected an object class attribute for each entity "
                # f"got: {grp}"))
                return None

            object_class_value = object_class_attr["value"]
            category_id = self.object_class_value_to_cat_id[object_class_value]
            data_file_id = object_class_attr["data_file_id"]

            location_attr = data.pop(
                PIXEL_LOCATION_ATTRIBUTE_UUID,
                data.pop(
                    str(PIXEL_LOCATION_ATTRIBUTE_UUID), data.pop(PIXEL_LOCATION_ATTRIBUTE_UUID.label, None)
                ),
            )

            if location_attr is None:
                print((f"entity: {entity_id}, No LOCATION"))
                # "expected a location attribute for each entity "
                # f"got: {grp}"))
                return None

            location = location_attr["value"]
            if isinstance(location, str):
                location = wkt.loads(location)

            segmentation = shapely_to_segmentation(location)
            bbox = segmentation_to_bbox(segmentation)
            area = get_bbox_area(bbox)

            extra_fields = {attr_id: attr["value"] for attr_id, attr in data.items()}
            extra_fields["entity_id"] = str(entity_id)
            self.annotation_count += 1
            return CocoAnnotationRecord(
                id=self.annotation_count,
                image_id=data_file_id,
                category_id=category_id,
                segmentation=segmentation,
                area=area,
                bbox=bbox,
                # Added to schema to allow extensions and interoperability
                # with Highlighter AnnotationType.metadata
                extra_fields=extra_fields,
            ).dict()

        def to_coco_image(row):
            self.image_count += 1
            filename = Path(row.filename)
            stem, suffix = filename.stem, filename.suffix.lower()
            filename = f"{stem}{suffix}"
            return CocoImageRecord(
                id=row.data_file_id,
                file_name=filename,
                width=row.width,
                height=row.height,
                # Added to schema to allow extensions and interoperability
                # with Highlighter Image.metadata
                extra_fields=row.extra_fields,
                # Added so multiple splits can be held in one CocoDataset
                split=row.split,
            ).dict()

        for split in dataset.data_files_df.split.unique():
            split_data_files_df = dataset.data_files_df[dataset.data_files_df.split == split]
            split_annos_df = dataset.annotations_df[
                dataset.annotations_df.data_file_id.isin(split_data_files_df.data_file_id)
            ]
            coco_annotations = split_annos_df.groupby("entity_id").apply(to_coco_annotation)
            coco_annotations = [e for e in coco_annotations if e is not None]
            coco_images = split_data_files_df.apply(lambda row: to_coco_image(row), axis=1).to_list()
            coco = {
                "annotations": coco_annotations,
                "images": coco_images,
                "categories": self.coco_categories,
            }
            with (self.annotations_dir / f"{split}.json").open("w") as f:
                json.dump(coco, f)
