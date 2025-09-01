from enum import Enum, unique


@unique
class ContentTypeEnum(str, Enum):  # inherit from str to support pydantic serialise to json
    UNKNOWN = "unknown"
    AUDIO = "audio"
    IMAGE = "image"
    JSON = "json"
    KML = "kml"
    OBSERVATION = "observation"
    TEXT = "text"
    VIDEO = "video"
    WEB_PAGE = "web_page"
