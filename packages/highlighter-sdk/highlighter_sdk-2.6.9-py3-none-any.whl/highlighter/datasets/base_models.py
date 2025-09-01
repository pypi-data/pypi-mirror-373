from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ..client import AttributeValue
from ..core import LabeledUUID

__all__ = [
    "AttributeRecord",
    "ImageRecord",
    "S3Files",
]

DEFAULT_SPLIT_NAME = "data"
DEFAULT_DATA_FILES_KEY = "images"  # TODO: Update to 'files'
DEFAULT_ANNOS_KEY = "annotations"  # TODO: Update to 'attributes'
CLOUD_FILES_INFO_KEY = "cloud_files_info"


class ImageRecord(BaseModel):
    data_file_id: Union[int, str]
    width: Optional[int] = None
    height: Optional[int] = None
    filename: str
    split: Optional[str] = DEFAULT_SPLIT_NAME
    extra_fields: Optional[Dict] = None
    assessment_id: Optional[int] = None
    hash_signature: Optional[str] = None


# Extra fields are ignored and will be dropped when instantiating
# a the Object. This is done so things don't break if we load
# some older S3Files where 'type' is a field. If you plan on changing
# this you should consider what to do in this situation
class S3Files(BaseModel, extra="ignore"):
    """Information needed to donwload files/records from s3

    s3://my-bucket/datasets/123/  <-- bucket_name = my-bucket
        records_abc123.json       <-- records_prefix = datasets/123/records_abc123.json
        files_def456.tar.gz       <-- files_prefix = [datasets/123/files_def456.tar.gz,]
    """

    bucket_name: str
    prefix: str
    files: List[str]
    records: List[str] = []
    other: List = []


class AttributeRecord(BaseModel):
    data_file_id: Union[int, str]
    entity_id: UUID = Field(default_factory=uuid4)
    attribute_id: Optional[Union[LabeledUUID, UUID, str]] = None
    attribute_name: str
    value: Any = None
    confidence: Optional[float] = 1.0
    frame_id: Optional[int] = None

    time: Union[datetime, str] = Field(default_factory=datetime.now)
    pipeline_element_name: Optional[str] = None
    training_run_id: Optional[int] = None

    @field_validator("time")
    @classmethod
    def validate_isofrmat(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        else:
            return v

    @classmethod
    def from_attribute_value(
        cls,
        data_file_id: Union[int, str],
        attribute_value: AttributeValue,
        entity_id: Optional[UUID] = None,
        frame_id: Optional[int] = None,
        time: Optional[Union[datetime, str]] = None,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
    ):
        attribute_id = attribute_value.attribute_id
        attribute_name = getattr(attribute_value.attribute_id, "label", "")
        confidence = attribute_value.confidence
        value = attribute_value.value
        return cls(
            data_file_id=data_file_id,
            entity_id=uuid4() if entity_id is None else entity_id,
            attribute_id=attribute_id,
            attribute_name=attribute_name,
            value=value,
            confidence=confidence,
            frame_id=frame_id,
            time=datetime.now() if time is None else time,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
        )

    def dict(self, *args, **kwargs):
        _d = super().model_dump(*args, **kwargs)
        _d["time"] = _d["time"].isoformat()
        return _d

    def to_df_record(self):
        _d = self.dict(exclude_none=True)
        record = {
            "data_file_id": _d.pop("data_file_id"),
            "entity_id": str(_d.pop("entity_id")),
            "attribute_id": str(_d.pop("attribute_id")),
            "attribute_name": _d.pop("attribute_name"),
            "value": _d.pop("value"),
            "confidence": _d.pop("confidence"),
        }
        record["extra_fields"] = _d
        return record
