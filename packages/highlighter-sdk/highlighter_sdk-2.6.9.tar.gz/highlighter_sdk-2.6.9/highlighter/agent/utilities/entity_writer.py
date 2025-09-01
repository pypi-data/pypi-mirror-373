import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import IO, Any, BinaryIO, Dict, List, Optional, Union
from uuid import UUID, uuid4

import fastavro
import numpy as np
from scipy.spatial.distance import pdist, squareform
from shapely.geometry import LineString, MultiPolygon

from highlighter.client import HLClient
from highlighter.client import aws_s3 as hls3
from highlighter.client.base_models import Annotation, Entity, Observation
from highlighter.core.const import EMBEDDING_ATTRIBUTE_UUID, OBJECT_CLASS_ATTRIBUTE_UUID

__all__ = [
    "ByteAvroEntityWriter",
    "EmbeddingAggregationMode",
    "EntityToAvroConverter",
    "FileAvroEntityWriter",
    "FileAvroObservationWriter",
    "IEntityWriter",
    "S3AvroEntityWriter",
]


class EmbeddingAggregationMode(str, Enum):
    AVERAGE = "average"
    MOST_REPRESENTATIVE_WITHOUT_OUTLIERS = "most_representative_without_outliers"


def similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Get the full similarity matrix using 1 - cosine_distance.

    Args:
        embeddings: NxM numpy array where N is the number of embeddings to compare and M
        is the length of each vector

    Returns:
        an NxN array where matrix[r][c] is the distance from embeddings[i] to
        embeddings[j]

    """
    dist_upper_triangle = pdist(embeddings, metric="cosine")
    dist_matrix = squareform(dist_upper_triangle)
    similarity_matrix = 1 - dist_matrix
    np.fill_diagonal(similarity_matrix, 1)  # Set diagonal to 1
    return similarity_matrix


def average_embedding(embeddings: np.ndarray) -> np.ndarray:
    return embeddings.mean(axis=0)


def most_representative_without_outliers(embeddings: np.ndarray) -> np.ndarray:
    """Find the embedding that is closest to all other embeddings using
    1-cosine similarity as the distance metric

    If the number of embeddings is < 10 then we don't check for outliers
    """
    grid = similarity_matrix(embeddings)
    l = len(embeddings)  # noqa
    if l < 10:
        idx = np.argmax(np.sum(grid, axis=1))
        return embeddings[idx]

    grid = np.sort(grid, axis=1)
    bi, ti = l // 10, l - l // 10
    # print(l, bi, ti)
    grid = grid[:, bi:ti]
    idx = np.argmax(np.sum(grid, axis=1))
    return embeddings[idx]


def find_top_k_embeddings(embeddings: np.ndarray, k: int) -> np.ndarray:
    l = len(embeddings)  # noqa
    step = l // k
    result = np.empty((k, embeddings.shape[1]))
    for i in range(k):
        if i + 1 == k:
            result[i] = most_representative_without_outliers(embeddings[i * step :])
        else:
            result[i] = most_representative_without_outliers(embeddings[i * step : (i + 1) * step])
    return result


@dataclass
class TrackDatumSource:
    confidence: float
    frameId: int


@dataclass
class TrackObservation:
    entityId: str
    entityAttributeId: str
    entityDatumSource: TrackDatumSource
    value: Optional[Any]
    time: datetime
    entityAttributeEnumId: Optional[str] = None


@dataclass
class XY:
    x: float
    y: float


@dataclass
class Bounds:
    min: XY
    max: XY


@dataclass
class TrackDetection:
    frame_id: int
    geometry_type: int  # values (invalid 0, polygon 10,  line 20)
    confidence: float
    bounds: Optional[Bounds] = None
    wkt: Optional[str] = None


@dataclass
class Track:
    data_file_id: Optional[str] = None
    track_id: str = field(default_factory=lambda: str(uuid4()))
    detections: List[TrackDetection] = field(default_factory=list)
    eavts: List[TrackObservation] = field(default_factory=list)


@dataclass
class EntityTracks:
    id: str  # <- Entity.id
    object_class: str = ""
    tracks: List[Track] = field(default_factory=lambda: [Track()])
    embeddings: List[List[float]] = field(default_factory=lambda: [])

    def asdict(self):
        return asdict(self)


class EntityToAvroConverter:
    class CompressionCodec(str, Enum):
        NULL = "null"
        SNAPPY = "snappy"

    @staticmethod
    def _append_embeddings(
        observation: Observation,
        entity_tracks: EntityTracks,
    ) -> EntityTracks:
        entity_tracks.embeddings.append([int(i) for i in observation.value])
        return entity_tracks

    @staticmethod
    def _append_object_class(
        observation: Observation,
        entity_tracks: EntityTracks,
    ) -> EntityTracks:
        entity_tracks.object_class = str(observation.value)
        return entity_tracks

    @staticmethod
    def _append_enum(observation: Observation, entity_tracks: EntityTracks) -> EntityTracks:
        time = observation.occurred_at if hasattr(observation, "occurred_at") else observation.time
        entity_tracks.tracks[0].eavts.append(
            TrackObservation(
                entityId=str(observation.entity_id),
                entityAttributeId=str(observation.attribute_id),
                entityAttributeEnumId=str(observation.value),
                entityDatumSource=TrackDatumSource(
                    confidence=observation.datum_source.confidence,
                    frameId=observation.datum_source.frame_id,
                ),
                value=None,
                time=time,
            )
        )
        return entity_tracks

    @staticmethod
    def _append_sclar(observation: Observation, entity_tracks: EntityTracks) -> EntityTracks:
        time = observation.occurred_at if hasattr(observation, "occurred_at") else observation.time
        entity_tracks.tracks[0].eavts.append(
            TrackObservation(
                entityId=str(observation.entity_id),
                entityAttributeId=str(observation.attribute_id),
                entityAttributeEnumId="",
                entityDatumSource=TrackDatumSource(
                    confidence=observation.datum_source.confidence,
                    frameId=observation.datum_source.frame_id,
                ),
                value=observation.value,
                time=time,
            )
        )
        return entity_tracks

    APPEND_OBSERVATION_FNS = {
        "8beab557-8d83-4257-82d0-101341236c5b": _append_embeddings,
        "df10b67d-b476-4c4d-acc2-c1deb5a0e4f4": _append_object_class,
    }

    EmbeddingAggregationFn = {
        EmbeddingAggregationMode.AVERAGE: average_embedding,
        EmbeddingAggregationMode.MOST_REPRESENTATIVE_WITHOUT_OUTLIERS: most_representative_without_outliers,
    }

    @staticmethod
    def _annotation_to_track_frame(
        frame_id: int,
        annotation: Annotation,
    ) -> TrackDetection:
        x0, y0, x1, y1 = annotation.location.bounds
        confidence = annotation.datum_source.confidence
        if isinstance(annotation.location, MultiPolygon):
            return TrackDetection(
                frame_id=frame_id,
                wkt=str(annotation.location),
                geometry_type=10,
                confidence=confidence,
            )
        elif isinstance(annotation.location, LineString):
            return TrackDetection(
                frame_id=frame_id,
                wkt=str(annotation.location),
                geometry_type=20,
                confidence=confidence,
            )
        else:
            return TrackDetection(
                frame_id=frame_id,
                bounds=Bounds(
                    min=XY(x=float(x0), y=float(y0)),
                    max=XY(x=float(x1), y=float(y1)),
                ),
                geometry_type=0,
                confidence=confidence,
            )

    def __init__(
        self,
        schema: Union[str, Path, List],
        compression_codec: CompressionCodec = CompressionCodec.NULL,
    ):
        self.compression_codec = compression_codec

        if isinstance(schema, (str, Path)):
            self._schema = json.load(Path(schema).open("r"))
        elif isinstance(schema, list):
            self._schema = schema
        else:
            raise ValueError(f"Invaid schema dict or schema path, got: {schema}")

    def to_records(self, entities_dict: Dict[UUID, List[Entity]]) -> List[EntityTracks]:
        records = []
        for entity_id, entities in entities_dict.items():
            if not entities:
                continue
            entity_tracks = EntityTracks(id=str(entity_id))
            for entity in entities:
                for anno in entity.annotations:

                    if (frame_id := anno.datum_source.frame_id) is None:
                        raise ValueError(
                            f"To use the {self.__class__.__name__} you "
                            "must specify 'frame_id' on the Annotation.datum_source"
                        )

                    for obs in anno.observations:
                        if (obs.datum_source.frame_id is not None) and (
                            obs.datum_source.frame_id != frame_id
                        ):
                            raise ValueError(
                                f"Observation and Annotation have conflicting frame_id, got: {obs} --- and --- {anno}"
                            )
                        entity_tracks = self._append_observation(obs, entity_tracks)

                    entity_tracks = self._append_annotation(anno, entity_tracks)

            records.append(entity_tracks.asdict())
        return records

    def write_records(self, records: List[EntityTracks], fp: Union[BytesIO, IO]):
        fastavro.writer(fp, self._schema, records, codec=self.compression_codec)
        fp.flush()
        return fp

    def convert(self, entities_dict: Dict[UUID, List[Entity]], fp: Union[BytesIO, IO]):
        records = self.to_records(entities_dict)
        return self.write_records(records, fp)

    def _append_observation(self, observation: Observation, entity_tracks: EntityTracks) -> EntityTracks:
        attribute_id = str(observation.attribute_id)
        append_entity_fn = self.APPEND_OBSERVATION_FNS.get(attribute_id, self._append_enum)
        entity_tracks = append_entity_fn(observation, entity_tracks)
        return entity_tracks

    def _append_annotation(self, annotation: Annotation, entity_tracks: EntityTracks) -> EntityTracks:
        entity_tracks.tracks[0].data_file_id = str(annotation.data_file_id)
        entity_tracks.tracks[0].detections.append(
            self._annotation_to_track_frame(annotation.datum_source.frame_id, annotation)
        )
        return entity_tracks


class ObservationToAvroConverter:
    """Convert grouped observations into Avro *Entity* records."""

    class CompressionCodec(str):
        NULL = "null"
        SNAPPY = "snappy"

    def __init__(
        self,
        schema: Union[str, Path, List],
        compression_codec: CompressionCodec = CompressionCodec.NULL,
    ):
        self.compression_codec = compression_codec

        if isinstance(schema, (str, Path)):
            self._schema = json.load(Path(schema).open("r"))
        elif isinstance(schema, list):
            self._schema = schema
        else:
            raise ValueError(f"Invaid schema dict or schema path, got: {schema}")

    def to_records(self, grouped_observations: Dict[UUID, List[Observation]]) -> List[dict]:
        """Aggregate *grouped_observations* → Avro-serialisable Entity records."""

        records: List[dict] = []
        for entity_id, observations in grouped_observations.items():
            if not observations:
                continue

            entity_tracks = EntityTracks(id=str(entity_id))
            track = entity_tracks.tracks[0]
            first_anno = observations[0].annotation
            track.data_file_id = (
                str(first_anno.data_file_id) if first_anno else ""
            )  # FIXME handle multiple and generate separate tracks

            seen_frames: set[int] = set()
            for obs in observations:
                # if not isinstance(obs.value, (int, float)):
                #     continue

                attr_id = str(obs.attribute_id)
                value = getattr(obs, "value", None)

                if attr_id == EMBEDDING_ATTRIBUTE_UUID:
                    # FIXME: Do we handle embeddings on track, does this make sence?
                    # We did this for fish similarity lookup, to find similar
                    # instances of fish. But does putting embeddings in the avro
                    # tracks make sense.
                    entity_tracks.embeddings.append([int(v) for v in value])  # type: ignore[arg-type]
                    continue

                if attr_id == OBJECT_CLASS_ATTRIBUTE_UUID:
                    entity_tracks.object_class = str(
                        value
                    )  # TODO: consider whether we take the first or last observation
                    continue

                # handle different attribute types
                time = obs.occurred_at if hasattr(obs, "occurred_at") else obs.time
                track.eavts.append(
                    TrackObservation(
                        entityId=str(obs.entity_id),
                        entityAttributeId=str(obs.attribute_id),
                        entityAttributeEnumId="",
                        entityDatumSource=TrackDatumSource(
                            confidence=obs.datum_source.confidence,
                            frameId=obs.datum_source.frame_id,
                        ),
                        value=obs.value,
                        time=time,
                    )
                )

                track.data_file_id = str(obs.annotation.data_file_id)
                frame_id = obs.annotation.datum_source.frame_id
                x0, y0, x1, y1 = obs.annotation.location.bounds
                confidence = obs.annotation.datum_source.confidence
                track.detections.append(
                    TrackDetection(
                        frame_id=frame_id,
                        bounds=Bounds(
                            min=XY(x=float(x0), y=float(y0)),
                            max=XY(x=float(x1), y=float(y1)),
                        ),
                        geometry_type=10,
                        confidence=confidence,
                    )
                )

            records.append(entity_tracks.asdict())
        return records

    def write_records(self, records: List[EntityTracks], fp: Union[BytesIO, IO]):
        fastavro.writer(fp, self._schema, records, codec=self.compression_codec)
        fp.flush()
        return fp

    def convert(self, observations_dict: Dict[UUID, List[Observation]], fp: Union[BytesIO, IO]):
        records = self.to_records(observations_dict)
        return self.write_records(records, fp)


class IEntityWriter(ABC):
    @abstractmethod
    def write(self, entities: Dict[UUID, List[Entity]]):
        pass


class ByteAvroEntityWriter(IEntityWriter):

    def __init__(
        self,
        schema: Union[str, Path, List],
        compression_codec: EntityToAvroConverter.CompressionCodec = EntityToAvroConverter.CompressionCodec.NULL,
    ):
        self.converter = EntityToAvroConverter(schema, compression_codec=compression_codec)

    def write(self, entities: Dict[UUID, List[Entity]]):
        avro_bytes = BytesIO()
        self.converter.convert(entities, avro_bytes)
        return bytes(avro_bytes.getbuffer())


class FileAvroEntityWriter(IEntityWriter):
    def __init__(
        self,
        schema: Union[str, Path, List],
        output: Union[str, Path, BinaryIO],
        compression_codec: EntityToAvroConverter.CompressionCodec = EntityToAvroConverter.CompressionCodec.NULL,
    ):
        self.converter = EntityToAvroConverter(schema, compression_codec=compression_codec)

        # if they passed us a file‐like, we’ll write to it directly;
        # otherwise coerce to Path
        if hasattr(output, "write"):
            self._sink_fileobj = output
            self._sink_path = None
        else:
            self._sink_fileobj = None
            self._sink_path = Path(output)

    def write(self, entities: Dict[UUID, List[Entity]]):
        avro_bytes = BytesIO()
        self.converter.convert(entities, avro_bytes)
        data = avro_bytes.getvalue()

        if self._sink_fileobj is not None:
            self._sink_fileobj.write(data)
        else:
            with self._sink_path.open("wb") as fp:
                fp.write(data)


# TODO: Refactor with FileAvroEntityWriter
class FileAvroObservationWriter(IEntityWriter):
    def __init__(
        self,
        schema: Union[str, Path, List],
        output: Union[str, Path, BinaryIO],
        compression_codec: ObservationToAvroConverter.CompressionCodec = ObservationToAvroConverter.CompressionCodec.NULL,
    ):
        self.converter = ObservationToAvroConverter(schema, compression_codec=compression_codec)

        # if they passed us a file‐like, we’ll write to it directly;
        # otherwise coerce to Path
        if hasattr(output, "write"):
            self._sink_fileobj = output
            self._sink_path = None
        else:
            self._sink_fileobj = None
            self._sink_path = Path(output)

    def write(self, observations: Dict[UUID, List[Observation]]):
        avro_bytes = BytesIO()
        self.converter.convert(observations, avro_bytes)
        data = avro_bytes.getvalue()

        if self._sink_fileobj is not None:
            self._sink_fileobj.write(data)
        else:
            with self._sink_path.open("wb") as fp:
                fp.write(data)


class S3AvroEntityWriter(IEntityWriter):
    def __init__(
        self,
        schema: Union[str, Path, List],
        filename: str,
        client: Optional[HLClient] = None,
        compression_codec: EntityToAvroConverter.CompressionCodec = EntityToAvroConverter.CompressionCodec.NULL,
    ):
        self.converter = EntityToAvroConverter(schema, compression_codec=compression_codec)
        self.filename = filename

        if client is None:
            self.client = HLClient.from_env()
        else:
            self.client: HLClient = client

    def write(self, entities: Dict[UUID, List[Entity]]):
        avro_bytes = BytesIO()
        self.converter.convert(entities, avro_bytes)
        shrine_file = hls3.upload_file_to_s3_in_memory(
            self.client, bytes(avro_bytes.getbuffer()), self.filename, mimetype="application/avro"
        )
        return shrine_file
