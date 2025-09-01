import logging
from collections import defaultdict
from typing import List, Optional, Union

from highlighter.agent.utilities.entity_writer import (
    EmbeddingAggregationMode,
    IEntityWriter,
)
from highlighter.client.base_models import Entity

logger = logging.getLogger(__name__)

__all__ = ["EntityAggregator"]


class EntityAggregator:
    """Aggregates an Entity's annotation.location and annotation.observations
    into tracks.

    An entity can have multiple tracks, see EntityTracks

    Args:
        minimum_track_frame_length (int): Only include tracks in the final
        result if the track has at least this number of frames.

        minimum_embedding_in_track_frame_length (int): Only include aggregate
        embeddings and include them in the final result if the track the at
        least this number of frames.

        embedding_aggregation_mode (EmbeddingAggregationMode): The method used to
        aggregate the embeddings for each frame in a track.
    """

    # TODO do this filtering in the tracker and make configurable
    DEFAULT_MINIMUM_TRACK_FRAME_LENGTH = 1
    DEFAULT_MINIMUM_EMBEDDING_TRACK_FRAME_LENGTH = 4

    def __init__(
        self,
        minimum_track_frame_length=DEFAULT_MINIMUM_TRACK_FRAME_LENGTH,
        minimum_embedding_in_track_frame_length=DEFAULT_MINIMUM_EMBEDDING_TRACK_FRAME_LENGTH,
        embedding_aggregation_mode: EmbeddingAggregationMode = EmbeddingAggregationMode.MOST_REPRESENTATIVE_WITHOUT_OUTLIERS,
        purge_interval: int = 50,
        writer: Optional[IEntityWriter] = None,
    ):

        self._minimum_track_frame_length = minimum_track_frame_length
        self._minimum_embedding_in_track_frame_length = minimum_embedding_in_track_frame_length
        self._proto_tracks = defaultdict(list)
        self._track_entities = defaultdict(list)
        self._next_purge = purge_interval
        self._embedding_aggregation_mode = EmbeddingAggregationMode(embedding_aggregation_mode)
        self._writer = writer

    def append_deprecated_eavts(self, eavts: List["EAVT"]):
        entities = Entity.entities_from_deprecated_eavts(eavts).values()
        self.append_entities(entities)

    def append_entities(self, entities: List[Entity]):
        if not entities:
            logger.debug("append_entities(): No entities to append")
            return

        logger.debug(f"append_entities(): Appending {len(entities)} entities")

        latest_frame_id = -1
        for entity in entities:
            if entity.id in self._track_entities:
                self._track_entities[entity.id].append(entity)
            else:
                self._proto_tracks[entity.id].append(entity)

                if len(self._proto_tracks[entity.id]) >= self._minimum_track_frame_length:
                    self._track_entities[entity.id] = self._proto_tracks.pop(entity.id)

            current_frame = entity.get_annotations()[0].datum_source.frame_id
            if current_frame > latest_frame_id:
                latest_frame_id = current_frame

        if latest_frame_id >= self._next_purge:
            self.purge_proto_tracks(latest_frame_id)

    def purge_proto_tracks(self, current_frame_id: int):
        for entity_id in self._proto_tracks.keys():
            last_track_frame = self._proto_tracks[entity_id][-1].annotation.datum_source.frame_id
            if (current_frame_id - last_track_frame) > self.minimum_track_frame_length:
                del self._proto_tracks[entity_id]

    def write(self):
        if self._writer is None:
            raise ValueError("You must pass an IEntityWriter to EntityAggregator")
        return self._writer.write(self._track_entities)
