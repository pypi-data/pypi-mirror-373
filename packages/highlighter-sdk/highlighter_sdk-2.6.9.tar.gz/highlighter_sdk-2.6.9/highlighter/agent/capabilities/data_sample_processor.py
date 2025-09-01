import logging
import os
import queue
import threading
import traceback
import uuid
from enum import Enum
from threading import Lock
from typing import Callable, Iterator, List, Optional
from uuid import UUID

from sqlmodel import Session

from highlighter.client import HLClient, assessments
from highlighter.client.gql_client import get_threadsafe_hlclient
from highlighter.core.data_models import DataFile, DataSample
from highlighter.core.enums import ContentTypeEnum
from highlighter.core.shutdown import runtime_stop_event

# sentinel used to tell the worker “no more DataFiles coming”
_STOP = object()


class RecordMode(str, Enum):
    OFF = "off"  # stream only, no persistence
    LOCAL = "local"  # DataFile.save_local() only
    CLOUD = "cloud"  # DataFile.save_to_cloud() only
    BOTH = "both"  # local + CLOUD


class DataSampleProcessor:
    """
    Wraps *any* iterator that yields `DataSamples` and optionally groups and saves
    them into `DataFiles`

    Parameters
    ----------
    iterator : Iterator[DataSample]
        Source of samples (e.g., VideoReader).
    record : RecordMode, default "off"
        Enable/disable on-the-fly persistence.
    session : Session | None
        Active SQLModel session – required when `record=True`.
    data_source_uuid, account_uuid : UUID | None
        Stored in the generated `DataFile`s (required when `record=True`).
    samples_per_file : int, default 5000
        How many samples per `DataFile`.
    writer_opts : dict | None
        Passed straight to `DataFile.save_local()`.
    content_type : str, default `ContentTypeEnum.IMAGE`
        `DataFile.content_type` to use when persisting.
    enforce_unique_files : bool, default False

    Usage
    ----------

    # 1.  Build a DataSample iterator (here: one VideoReader on an MP4 file)
    video_path = Path("/data/camera_01/2025-06-16_13-00m_00s.mp4")

    data_sample_iterator = VideoReader(
        source_url=str(video_path),
        output_type=OutputType.numpy,   # or OutputType.pillow
        sample_fps=12,                  # optional – resample FPS
    )

    # 2.  Wrap it in a DataSampleProcessor **with recording enabled**
    with Session(hl_engine) as session:
        processor = DataSampleProcessor(
            iterator=data_sample_iterator,
            record=RecordMode.OFF,              # <-- enable persistence
            session_factory=lambda: Session(db_engine),  # SQLModel session for save_local()
            data_source_uuid=uuid.uuid4(),      # associate DataFiles with a source
            account_uuid=uuid.uuid4(),          # (replace with real IDs in prod)
            samples_per_file=25,                # batch size
            writer_opts={"frame_rate": 24.0},   # forwarded to DataFile.save_local()
            # content_type defaults to IMAGE because each sample is a frame
        )

        # 3.  Iterate over frames – every 25th frame triggers a DataFile write
        for data_sample in processor:
            # do something with each frame (e.g. display, run ML inference, etc.)
            pass

        # 4.  Explicitly flush tail batch (<25 frames) once the iterator is done
        processor.flush()

        # Optional: inspect the DataFiles that were saved
        print(f"Saved {len(processor.saved_files)} DataFiles:")
        for df in processor.saved_files:
            print(" •", df.original_source_url)
    """

    def __init__(
        self,
        *,
        iterator: Iterator[DataSample],
        record: RecordMode = RecordMode.OFF,
        session_factory: Optional[Callable[[], Session]] = None,
        data_source_uuid: Optional[UUID] = None,
        account_uuid: Optional[UUID] = None,
        samples_per_file: int = 5000,
        writer_opts: Optional[dict] = None,
        content_type: str = ContentTypeEnum.IMAGE,
        queue_size: int = 8,
        enforce_unique_files: bool = False,
        data_file_id: Optional[UUID] = None,
    ):
        self._stop_event = runtime_stop_event or threading.Event()
        self.logger = logging.getLogger(__name__)
        if isinstance(record, str):
            try:
                record = RecordMode(record.lower())
            except ValueError:
                allowed = ", ".join(m.value for m in RecordMode)
                raise ValueError(f"record must be one of {{{allowed}}}")
        elif isinstance(record, RecordMode):
            # already a valid enum → nothing to do
            pass
        else:
            allowed = ", ".join(m.value for m in RecordMode)
            raise ValueError(f"record must be one of {{{allowed}}}")

        if record != RecordMode.OFF:
            if session_factory is None:
                raise ValueError("session_factory required when record ≠ 'off'")
            if data_source_uuid is None or account_uuid is None:
                raise ValueError("data_source_uuid and account_uuid are required")

        self._record_mode: RecordMode = record  # save enum
        self._save_local = record in (RecordMode.LOCAL, RecordMode.BOTH)
        self._save_cloud = record in (RecordMode.CLOUD, RecordMode.BOTH)

        self._iterator = iterator
        self._record = record
        self._session_factory = session_factory
        self._data_source_uuid = data_source_uuid
        self._account_uuid = account_uuid
        self._samples_per_file = samples_per_file
        self._writer_opts = writer_opts
        self._content_type = content_type
        self._enforce_unique_files = enforce_unique_files

        # batching state (only used if record=True)
        self._buffer: List[DataSample] = []
        self._saved_ids: List[UUID] = []
        self._saved_lock = Lock()  # guard cross-thread writes

        # background worker setup
        self._q: queue.Queue[DataFile | object] = queue.Queue(maxsize=queue_size)
        self._worker_exception: Optional[Exception] = None

        self._assessment = None
        self._current_data_file_id = uuid.uuid4() if data_file_id is None else data_file_id

        self._recording_start = None
        self._batch_start = None
        self._stream_batch_start_frame_index = 0  # current buffer's starting stream frame id

        if self._record_mode is not RecordMode.OFF:
            self.hl_client = HLClient.get_client()
            self._worker = threading.Thread(
                target=self._worker_loop,
                name="DataSampleSaver",
                daemon=True,
            )
            self._worker.start()
        else:
            self._worker = None

    def __iter__(self):
        return self

    def __next__(self) -> DataSample:
        try:
            sample = next(self._iterator)
            sample.data_file_id = self._current_data_file_id
        except StopIteration:
            self.flush()  # ← guarantees clean shutdown
            raise  # ← propagate to caller

        if self._record_mode is not RecordMode.OFF:
            if self._recording_start is None:
                self._recording_start = sample.recorded_at  # TODO: or datetime.now()

            if self._batch_start is None:
                self._batch_start = sample.recorded_at  # TODO: or datetime.now()

            cloned = sample.model_copy(deep=False)
            cloned.stream_frame_index = sample.media_frame_index  # keep the global one
            cloned.media_frame_index = (
                sample.stream_frame_index - self._stream_batch_start_frame_index
            )  # per-file index

            self._buffer.append(cloned)

            if self._samples_per_file > 0 and len(self._buffer) >= self._samples_per_file:
                self._stream_batch_start_frame_index = sample.stream_frame_index + 1
                self._flush_buffer_async()

        return sample

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        return False  # Don’t suppress exceptions from user code

    def __del__(self):
        try:
            self.flush()
        except Exception:
            raise
            # TODO: last-chance logging; avoid raising in __del__
            # import logging, traceback
            # logging.getLogger(__name__).error("Exception during flush:\n%s",
            #                                   traceback.format_exc())

    def flush(self):
        """
        Persist any residual samples, block until background saves complete,
        and propagate worker exceptions.
        """
        if self._record_mode is not RecordMode.OFF:
            if self._buffer:
                self._flush_buffer_async()

            # signal worker to exit and wait
            self._q.put(_STOP)
            if self._worker is not None:
                self._worker.join()

            if self._worker_exception:
                raise self._worker_exception  # re-raise in caller thread

    @property
    def saved_files(self) -> List[DataFile]:
        """
        Return a fresh list of DataFile instances re-loaded from the database,
        so their column attributes are fully populated and won’t try to lazy-load
        on a closed session.
        """
        with self._saved_lock:
            if self._record_mode is RecordMode.OFF or not self._saved_ids:
                return []

            ids_snapshot = list(self._saved_ids)

        if not ids_snapshot:
            return []

        session = self._session_factory()
        try:
            files = [session.get(DataFile, id) for id in ids_snapshot]
        finally:
            session.close()

        # ensure private attribute _data_dir exists so that get_data_dir() works
        for df in files:
            # Guarantee the pydantic-private storage exists
            priv = getattr(df, "__pydantic_private__", None)
            if priv is None:
                object.__setattr__(df, "__pydantic_private__", {})
                priv = df.__pydantic_private__  # type: ignore[attr-defined]

            # Initialise _data_dir slot if absent
            if "_data_dir" not in priv:
                priv["_data_dir"] = None

        return files

    def _flush_buffer_async(self):
        """Move current buffer into a new DataFile and queue it to worker."""
        df = DataFile(
            file_id=self._current_data_file_id,
            account_uuid=self._account_uuid or uuid.uuid4(),
            data_source_uuid=self._data_source_uuid or uuid.uuid4(),
            content_type=self._content_type,
            enforce_unique_files=self._enforce_unique_files,
            recorded_at=self._batch_start,
        )
        df.add_samples(self._buffer)
        self._buffer = []  # reset for next batch
        self._current_data_file_id = uuid.uuid4()
        self._batch_start = None

        self._q.put(df)  # may block if queue is full

    def _worker_loop(self):
        """
        Receives DataFile objects, opens its *own* SQLModel Session, writes
        them to disk (and cloud), then marks task done.  Stores first
        exception encountered.
        """
        try:
            hl_client = get_threadsafe_hlclient(self.hl_client.api_token, self.hl_client.endpoint_url)

            session: Optional[Session] = None
            while not self._stop_event.is_set():
                try:
                    data_file = self._q.get(timeout=0.5)  # TODO: what is the best timeout? use global?
                except queue.Empty:
                    continue  # loop and check stop_event again

                if data_file is _STOP:
                    break  # clean exit

                if session is None:
                    session = self._session_factory()  # lazy open

                samples_length = data_file.samples_length()
                match self._record_mode:
                    case RecordMode.OFF:
                        # Should never reach worker when OFF, but keep for completeness
                        pass

                    case RecordMode.LOCAL:
                        data_file.save_local(session, writer_opts=self._writer_opts)
                        self.logger.info(
                            f'DataFile("{data_file.file_id}")#save_local {samples_length} samples to {data_file.path_to_content_file}'
                        )

                    case RecordMode.CLOUD:

                        # Need local file as staging for upload
                        data_file.save_local(session, writer_opts=self._writer_opts)
                        data_file.save_to_cloud(session, hl_client=hl_client)
                        self.logger.info(
                            f'DataFile("{data_file.file_id}")#save_to_cloud ({samples_length} samples uploaded {data_file.path_to_content_file})'
                        )
                        # After successful upload, remove local copy
                        try:
                            os.remove(data_file.path_to_content_file)
                        except FileNotFoundError:
                            self.logger.warning(
                                "Local file already removed: %s", data_file.path_to_content_file
                            )

                    case RecordMode.BOTH:
                        data_file.save_local(session, writer_opts=self._writer_opts)
                        self.logger.info(
                            f'DataFile("{data_file.file_id}")#save_local {samples_length} samples to {data_file.path_to_content_file}'
                        )
                        data_file.save_to_cloud(session, hl_client=hl_client)
                        self.logger.info(
                            f'DataFile("{data_file.file_id}")#save_to_cloud ({samples_length} samples uploaded {data_file.path_to_content_file})'
                        )
                    case _:
                        raise ValueError(f"Unhandled RecordMode: {self._record_mode}")

                with self._saved_lock:
                    self._saved_ids.append(data_file.file_id)

                self._q.task_done()

            # done – commit & close
            if session is not None:
                session.close()

        except Exception as exc:
            self.logger.error(
                "Exception in worker thread [%s]: %s\n%s",
                threading.current_thread().name,
                str(exc),
                traceback.format_exc(),
            )
            self._worker_exception = exc
