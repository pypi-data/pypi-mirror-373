import mimetypes
from pathlib import Path
from typing import List, Tuple
from warnings import warn

from shapely.wkt import loads as wkt_loads

from ....client import PixelLocationAttributeValue
from ....core import OBJECT_CLASS_ATTRIBUTE_UUID, try_make_polygon_valid_if_invalid
from ...base_models import AttributeRecord, ImageRecord
from ...interfaces import IReader

__all__ = [
    "HighlighterAssessmentsReader",
]


class HighlighterAssessmentsReader(IReader):
    format_name = "highlighter_assessments"

    def __init__(self, assessments_gen):
        self.assessments_gen = assessments_gen

    def read(self) -> Tuple[List[AttributeRecord], List[ImageRecord]]:
        attribute_records = []
        data_file_records = []
        for assessment in self.assessments_gen:
            data_file = assessment.image
            assessment_id = assessment.id
            hash_signature = assessment.hash_signature
            data_file_id = data_file.id
            filename_original = Path(data_file.original_source_url)

            ext = filename_original.suffix.lower()
            if ext == "":
                ext = mimetypes.guess_extension(data_file.mime_type)
                assert isinstance(ext, str)
                ext = ext.lower()

            filename = f"{data_file_id}{ext}"
            data_file_records.append(
                ImageRecord(
                    data_file_id=data_file_id,
                    width=data_file.width,
                    height=data_file.height,
                    filename=filename,
                    extra_fields={"filename_original": str(filename_original)},
                    assessment_id=assessment_id,
                    hash_signature=hash_signature,
                )
            )

            for eavt in assessment.entity_attribute_values:
                value = eavt.value
                if value is None:
                    value = eavt.entity_attribute_enum.id

                datum_source = eavt.entity_datum_source
                if datum_source is None:
                    conf = 1.0
                else:
                    conf = datum_source.confidence

                attribute_records.append(
                    AttributeRecord(
                        data_file_id=data_file_id,
                        entity_id=eavt.entity_id,
                        attribute_id=eavt.entity_attribute.id,
                        attribute_name=eavt.entity_attribute.name,
                        value=value,
                        confidence=conf,
                    )
                )

            for annotation in assessment.annotations:
                if annotation.location is None:
                    warn("Null value found in location. Get it together bro.")
                    continue

                confidence = getattr(annotation, "confidence", None)
                try:
                    geometry = wkt_loads(annotation.location)
                    geometry = try_make_polygon_valid_if_invalid(geometry)
                    pixel_location_attribute_value = PixelLocationAttributeValue.from_geom(
                        geometry, confidence=confidence
                    )
                except Exception as e:
                    print(
                        f"Invalid Polygon, assessment: {assessment_id}, annotation: {annotation.id}, data_file: {data_file_id} "
                    )
                    continue

                object_class = annotation.object_class
                attribute_records.append(
                    AttributeRecord(
                        data_file_id=data_file_id,
                        entity_id=annotation.entity_id,
                        attribute_id=str(OBJECT_CLASS_ATTRIBUTE_UUID),
                        attribute_name=OBJECT_CLASS_ATTRIBUTE_UUID.label,
                        value=object_class.uuid,
                        frame_id=annotation.frame_id,
                        confidence=confidence,
                    )
                )

                attribute_records.append(
                    AttributeRecord.from_attribute_value(
                        data_file_id,
                        pixel_location_attribute_value,
                        entity_id=annotation.entity_id,
                        frame_id=annotation.frame_id,
                    )
                )

        return data_file_records, attribute_records
