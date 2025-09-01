import os
from pathlib import Path

from .labeled_uuid import LabeledUUID

__all__ = [
    "DEPRECATED_CAPABILITY_IMPLEMENTATION_FILE",
    "OBJECT_CLASS_ATTRIBUTE_UUID",
    "PIXEL_LOCATION_ATTRIBUTE_UUID",
    "DATA_FILE_ATTRIBUTE_UUID",
    "EMBEDDING_ATTRIBUTE_UUID",
    "TRACK_ATTRIBUTE_UUID",
    "HL_DOWNLOAD_TIMEOUT",
    "HL_DIR",
]

DEPRECATED_CAPABILITY_IMPLEMENTATION_FILE = "DeprecatedCapabilityImplementationFile"
OBJECT_CLASS_ATTRIBUTE_UUID = LabeledUUID("df10b67d-b476-4c4d-acc2-c1deb5a0e4f4", label="object_class")
PIXEL_LOCATION_ATTRIBUTE_UUID = LabeledUUID("594fcdba-c3dc-4fad-b1c1-f5f537e1d16c", label="pixel_location")
DATA_FILE_ATTRIBUTE_UUID = LabeledUUID("2b13c2d0-02ae-4bcc-9086-df3cdacf3563", label="image")
EMBEDDING_ATTRIBUTE_UUID = LabeledUUID("8beab557-8d83-4257-82d0-101341236c5b", label="embedding")
TRACK_ATTRIBUTE_UUID = LabeledUUID("32a44d06-62be-4be8-9b0e-884af6dfd6f3", label="track")
HL_DOWNLOAD_TIMEOUT = int(os.environ.get("HL_DOWNLOAD_TIMEOUT", "300"))
HL_DIR = Path(os.environ.get("HL_DIR", Path.home() / ".highlighter"))
