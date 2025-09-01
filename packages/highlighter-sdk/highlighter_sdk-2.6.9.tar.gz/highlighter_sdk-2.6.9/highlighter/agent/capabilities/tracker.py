import logging
import random
import uuid
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
import pykalman as km
import torch
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment

from highlighter.agent.capabilities.base_capability import Capability, StreamEvent
from highlighter.client.base_models.entity import Entity

from .bbox_ops import bbox_overlaps

logger = logging.getLogger(__name__)


class Tracker(Capability):

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        match_iou_threshold: float = 0.3
        high_threshold: float = 0.8
        num_frames_retain: int = 10
        enable_kalman_filter: bool = True
        kalman_filter_min_length: int = 10

    def __init__(self, context):
        super().__init__(context)
        match_iou_threshold, _ = self._get_parameter("match_iou_threshold")
        high_threshold, _ = self._get_parameter("high_threshold")
        num_frames_retain, _ = self._get_parameter("num_frames_retain")
        enable_kalman_filter, _ = self._get_parameter("enable_kalman_filter")
        kalman_filter_min_length, _ = self._get_parameter("kalman_filter_min_length")
        self.byte_tracker = ByteTracker(
            match_iou_thr=match_iou_threshold,
            enable_kalman_filter=enable_kalman_filter,
            high_threshold=high_threshold,
            num_frames_retain=num_frames_retain,
            kalman_filter_min_length=kalman_filter_min_length,
        )

    def process_frame(
        self,
        stream,
        entities: Dict[UUID, Entity],
    ) -> Tuple[StreamEvent, Dict]:

        self.byte_tracker.track_entities(stream.frame_id, entities)
        return StreamEvent.OKAY, {"tracked_entities": entities}


class KalmanFilterForTracking:
    def __init__(self, data: np.ndarray):

        data = np.array(data)
        x, n_dim = data.shape

        self.n_dim = n_dim
        self.kf = km.KalmanFilter(
            n_dim_obs=self.n_dim, n_dim_state=n_dim * 2, transition_matrices=make_transition_matrix(n_dim * 2)
        )
        state_mean_seq, state_variance_seq = self.kf.filter(data)
        self.state_mean = state_mean_seq[-1]
        self.state_variance = state_variance_seq[-1]

    def update(self, x):
        self.state_mean, self.state_variance = self.kf.filter_update(
            self.state_mean, self.state_variance, observation=x
        )

    def predict(self) -> np.ndarray:
        """
        make a prediction on where the bounding box will land
        """
        state_mean, _ = self.kf.filter_update(self.state_mean, self.state_variance, observation=None)
        return np.array(state_mean[: self.n_dim])


def make_transition_matrix(n: int):
    """
    this function creates transition matrices for a KalmanFilter
    for n = 6

    return
    [[1. 0. 0. 1. 0. 0.]
    [0. 1. 0. 0. 1. 0.]
    [0. 0. 1. 0. 0. 1.]
    [0. 0. 0. 1. 0. 0.]
    [0. 0. 0. 0. 1. 0.]
    [0. 0. 0. 0. 0. 1.]]
    """
    trans_mat = np.eye(n)
    half = n // 2
    if n % 2 != 0:
        half += 1

    for x in range(n // 2):
        trans_mat[x, x + half] = 1.0

    return trans_mat


class TrackInternalState(BaseModel):
    frame_ids: List[int]
    embeddings: List[Any]
    bounding_boxes: List[Any]  # torch.Tensor
    kalman_filter: Any  # KalmanFilterForTracker


class ByteTracker(BaseModel):
    high_threshold: float = 0.8
    match_iou_thr: float = 0.4
    num_frames_retain: int = 10
    enable_kalman_filter: bool = False
    kalman_filter_min_length: int = 10

    """
    with byte tracker, we divide the bboxes in two groups. one with high confidence and the other with lower confidence
    the high confidence ones can be used to both create new track and extend existing tracks, while the low confidence
    ones can only be used to extend existing tracks. the matching between bboxes and existing tracks are done in two
    rounds, first with ones with higher confidence, then with ones with lower confidence. Kalman filter is also used to
    predict the location of a tracker for a frame if it is not matched in both rounds, but for that, the length of track
    needs to be over `kalman_filter_min_length`

    * for better results, it is recommended to set the detector with lower threshold.
    """

    class Config:
        extra = "allow"

    def __init__(self, *args, **kwargs):
        """
        high_threshold: the value that divide bboxes into the high confidence group and the low confidence group
        match_iou_thr: minimum value will be considered as a match using iou
        num_frames_retain: the number of frames, a track will be kept in memory without a match
        enale_kalman_filter: switch for kalman_filter
        kalman_filter_min_length: the minimum sequence length required to use kalman filter for predictions.
        """
        super().__init__(**kwargs)

        self.tracks: Dict[UUID, TrackInternalState] = {}
        self.rnd = random.Random()  # nosec random
        if logger.isEnabledFor(logging.DEBUG):
            self.rnd.seed(0)
            logger.debug("tracker configuration:")
            for k, v in vars(self).items():
                if isinstance(k, (int, float, str)):
                    logger.debug(f"{k}={v}")

    def track_entities(self, frame_id: int, entities: Dict[UUID, Entity]) -> Dict[UUID, Entity]:
        if len(entities) == 0:
            return {}

        for entity in entities.values():
            if len(entity.get_annotations()) > 1:
                raise NotImplementedError(
                    f"Cannot track entities with multiple locations in a frame. Entity ID: {entity}"
                )
        entities_with_annotations = [
            entity for entity in entities.values() if len(entity.get_annotations()) > 0
        ]
        annotations = np.array([entity.get_annotations()[0] for entity in entities_with_annotations])
        bboxes = np.array([list(a.location.bounds) + [a.datum_source.confidence] for a in annotations])
        entity_ids = [entity.id for entity in entities_with_annotations]
        track_ids = np.array(
            [annotation.track_id if annotation.track_id else uuid4() for annotation in annotations]
        )
        external_ids = list(zip(entity_ids, track_ids))
        assigned_ids = self(frame_id, bboxes, external_ids)
        """
        Reassign entity IDs so that annotations and observations along the same track are grouped together
        as an entity.
        The entity ID of the first annotation in a track is assigned to the rest of the annotations and observations
        in the track.
        Note: A fresh track ID is assigned by the tracker, so that entities may later be unified without also unifying the tracks.
        """
        for entity, (assigned_entity_id, track_id) in zip(entities_with_annotations, assigned_ids):
            del entities[entity.id]
            entity.reassign_id(assigned_entity_id)
            entity.get_annotations()[0].track_id = track_id
            entities[entity.id] = entity
        return entities

    def __call__(self, frame_id: int, bboxes: np.ndarray, external_ids: List[Any] = None) -> List[Any]:
        """
        internal ids are monotonically increasing
        bboxes [x0, y0, x1, y1, confidence]
        embedding is not needed

        external_ids: A list of entity ids for each box.
        len(external_ids) must equal bboxes.shape[0]
        """
        assert len(external_ids) == bboxes.shape[0]

        no_bbox_present = bboxes.shape[0] == 0
        # if not bboxes found in current frame, short circuit it
        if no_bbox_present:
            self.pop_invalid_tracks(frame_id)
            return []

        if len(bboxes.shape) != 2 or bboxes.shape[1] != 5:
            raise ValueError(f"bboxes are not in required format with {bboxes.shape}")

        # remove pytorch
        bboxes_with_confidence = torch.Tensor(bboxes)
        num_bboxes = len(bboxes_with_confidence)
        confidences = bboxes[:, -1]
        bboxes = bboxes_with_confidence[:, :4]
        bboxes_with_high_confidence = bboxes[confidences > self.high_threshold, :]  # strip confidence
        bboxes_with_high_confidence_indexes = np.arange(num_bboxes)[confidences > self.high_threshold]
        bboxes_with_low_confidence = bboxes[confidences < self.high_threshold, :]
        bboxes_with_low_confidence_indexes = np.arange(num_bboxes)[confidences <= self.high_threshold]

        # no tracks
        if len(self.tracks) == 0:
            ids = external_ids
        else:

            ids: List[Optional[UUID]] = [None] * num_bboxes
            track_ids = list(self.tracks.keys())
            matched = [False] * len(track_ids)
            for bbox_indexes, _bboxes in [
                (bboxes_with_high_confidence_indexes, bboxes_with_high_confidence),
                (bboxes_with_low_confidence_indexes, bboxes_with_low_confidence),
            ]:
                available_track_ids = [x for m, x in zip(matched, track_ids) if not m]
                if not available_track_ids:
                    break

                track_bboxes = torch.cat(
                    [self.tracks[x].bounding_boxes[-1][None] for x in available_track_ids]
                )

                iou_grid = bbox_overlaps(track_bboxes, _bboxes).cpu().numpy()
                dists = 1 - iou_grid
                row, col = linear_sum_assignment(dists)
                # if frame_id == 155:
                #    breakpoint()
                for r, c in zip(row, col):
                    dist = dists[r, c]
                    if dist < 1 - self.match_iou_thr:
                        ids[bbox_indexes[c]] = available_track_ids[r]
                        matched[r] = True

            # if _id is still None that means they have not been assigned to a track.
            # here we create a ids (or use an external_id). This way we will return
            # an id for each box, but only the ones starting new tracks or adding
            # to existing tracks will update self.tracks
            for i, _id in enumerate(ids):
                if _id is None:
                    ids[i] = external_ids[i]

        # update or init tracks with high confidence boxes
        for idx in bboxes_with_high_confidence_indexes:
            _id = ids[idx]
            bbox = bboxes[idx]
            if _id in self.tracks:
                self.update_track(_id, frame_id, [], bbox)
            else:
                self.init_track(_id, frame_id, [], bbox)

        # update existing tracks with low_confidence boxes
        for idx in bboxes_with_low_confidence_indexes:
            _id = ids[idx]
            bbox = bboxes[idx]
            if _id in self.tracks:
                self.update_track(_id, frame_id, [], bbox)

        # update the kalman filter for the tracks even if the track cannot be matched with bbox
        if self.enable_kalman_filter:
            for _id, track in self.tracks.items():
                if track.frame_ids[-1] < frame_id:
                    self.update_track(_id, frame_id, [], None)

        self.pop_invalid_tracks(frame_id)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"inference on frame: {frame_id}")
            bboxes_numpy = bboxes.numpy()
            columns = ["x0", "y0", "x1", "y1"]
            logger.debug(pd.DataFrame(bboxes_numpy, columns=columns).to_markdown())
            logger.debug(pd.DataFrame(bboxes_numpy, columns=columns).to_json())
            current_tracks = []
            for _id, state in self.tracks.items():
                bboxes_lst = bboxes_numpy.tolist()
                last = state.bounding_boxes[-1].tolist()
                try:
                    idx = [all(abs(i - j) < 2 for i, j in zip(x, last)) for x in bboxes_lst].index(True)
                except ValueError:
                    idx = None
                current_tracks.append(
                    {"prefix": str(_id)[:10], "location": idx, "frames": len(state.frame_ids)}
                )
            logger.debug(pd.DataFrame(current_tracks).to_markdown())
        return ids

    @staticmethod
    def xyxy2xyah(bboxes):
        """Transform bounding boxes."""
        cx = (bboxes[:, 2] + bboxes[:, 0]) / 2
        cy = (bboxes[:, 3] + bboxes[:, 1]) / 2
        w = bboxes[:, 2] - bboxes[:, 0]
        h = bboxes[:, 3] - bboxes[:, 1]
        xyah = torch.stack([cx, cy, w / h, h], -1)
        return xyah

    def init_track(self, id, frame_id, embedding, bbox: torch.Tensor):
        """Initialize a track."""
        self.tracks[id] = TrackInternalState(
            frame_ids=[frame_id], embeddings=[embedding], bounding_boxes=[bbox], kalman_filter=None
        )

    def update_track(self, id, frame_id, embedding, bbox: Optional[torch.Tensor]):
        """Update a track."""
        track = self.tracks[id]
        if bbox is not None:
            track.frame_ids.append(frame_id)
            track.embeddings.append(embedding)
            track.bounding_boxes.append(bbox)
        # attach kalman filter
        if not self.enable_kalman_filter:
            return

        if len(track.bounding_boxes) == self.kalman_filter_min_length:
            bounding_boxes = np.vstack([x.numpy() for x in track.bounding_boxes])
            track.kalman_filter = KalmanFilterForTracking(bounding_boxes)

        # update kalman filter with bbox
        elif self.enable_kalman_filter and track.kalman_filter and (bbox is not None):
            track.kalman_filter.update(bbox.numpy())

        # blind update kalman filter
        elif self.enable_kalman_filter and track.kalman_filter and (bbox is None):
            loc = track.kalman_filter.predict()
            # for predicted bounding box, we don't update the frame_id
            track.bounding_boxes.append(torch.Tensor(loc))
            track.kalman_filter.update(loc)

    def pop_invalid_tracks(self, frame_id):
        """Pop out invalid tracks."""
        terminated_track_ids = []
        for track_id, track in self.tracks.items():
            # case1: disappeared frames >= self.num_frames_retain
            case1 = frame_id - track.frame_ids[-1] >= self.num_frames_retain
            if case1:
                terminated_track_ids.append(track_id)
        return [self.tracks.pop(x) for x in terminated_track_ids]

    def get_uuid(self) -> UUID:
        return uuid.UUID(int=self.rnd.getrandbits(128), version=4)
