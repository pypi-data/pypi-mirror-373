import os
from pathlib import Path
from typing import List, Tuple, Union
from uuid import UUID, uuid4

from ....client.io import _pil_open_image_path
from ....core import OBJECT_CLASS_ATTRIBUTE_UUID
from ...base_models import AttributeRecord, ImageRecord
from ...interfaces import IReader

PathLike = Union[str, Path]


def is_uuid(s):
    try:
        _ = UUID(s)
        return True
    except ValueError as e:
        return False


def get_class_dir_uuids(root_dir):
    uuids = [
        item
        for item in os.listdir(root_dir)
        if (os.path.isdir(os.path.join(root_dir, item)) and is_uuid(item))
    ]
    return uuids


class TorchImageFolderReader(IReader):
    format_name = "torch-image-folder"

    def __init__(
        self,
        root_dir: PathLike,
        attribute_id: str = str(OBJECT_CLASS_ATTRIBUTE_UUID),
        attribute_name: str = OBJECT_CLASS_ATTRIBUTE_UUID.label,
    ):
        """Read a ImageFolder classification dataset from disk into
        highlighter Dataset format

        root_dir: Root dir of classification dataset. This dir should
        contain dirs named for theHighlighterEntityAttributeEnumID used for
        the classification task.

        attribute_id: Default OBJECT_CLASS_ATTRIBUTE_UUID
        attribute_name: Default 'object_class'

        """
        self.root_dir = str(root_dir)
        self.attribute_id = attribute_id
        self.attribute_name = attribute_name

    def read(self) -> Tuple[List[AttributeRecord], List[ImageRecord]]:
        class_uuids = get_class_dir_uuids(self.root_dir)

        attribute_records = []
        data_file_records = []
        for value in class_uuids:
            image_filenames = os.listdir(os.path.join(self.root_dir, value))
            for filename in image_filenames:
                data_file_id = Path(filename).stem
                w, h = _pil_open_image_path(os.path.join(self.root_dir, self.attribute_id, filename)).size

                data_file_records.append(
                    ImageRecord(
                        data_file_id=data_file_id, width=w, height=h, filename=filename, extra_fields={}
                    )
                )

                attribute_records.append(
                    AttributeRecord(
                        data_file_id=data_file_id,
                        entity_id=str(uuid4()),
                        attribute_id=self.attribute_id,
                        attribute_name=self.attribute_name,
                        value=value,
                    )
                )

        return data_file_records, attribute_records
