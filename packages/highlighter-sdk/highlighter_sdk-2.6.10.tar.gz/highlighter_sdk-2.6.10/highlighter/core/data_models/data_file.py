import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Union
from uuid import UUID

from pydantic import PrivateAttr
from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import Session as SASession
from sqlmodel import Field, Relationship, Session, SQLModel, select

from highlighter.client.data_files import get_data_files
from highlighter.client.gql_client import HLClient
from highlighter.core.config import HighlighterRuntimeConfig
from highlighter.core.data_models.account_mixin import AccountMixin
from highlighter.core.data_models.data_file_source import DataFileSource
from highlighter.core.data_models.data_sample import DataSample
from highlighter.core.data_models.data_source import DataSource
from highlighter.core.gql_base_model import GQLBaseModel
from highlighter.core.utilities import get_slug, sha512_of_content

logger = logging.getLogger(__name__)


class DataFile(SQLModel, AccountMixin, GQLBaseModel, table=True):
    """Extensible DataFile that buffers *samples* then flushes via `save()`.

    content_type
        One of the keys recognised by the highlighter.io.writers registry.

    Usage::

        df = DataFile(data_source_uuid=ds_uuid, content_type="video")
        for f in vfi:
            df.add_samples(DataSample(content=f.content, media_frame_index=i))
        df.save(session, writer_opts={"fps": 12})

    """

    # ----------------------- SQL columns & relationships --------------------
    file_id: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    content_type: str = Field(sa_column=Column(String))
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    media_frame_index: int = 0
    original_source_url: Optional[str] = Field(sa_column=Column(String, default=None))
    file_hash: str = Field(sa_column=Column(String))

    data_file_sources: list["DataFileSource"] = Relationship(back_populates="data_file")
    data_source_uuid: UUID = Field(foreign_key="datasource.uuid")
    data_source: "DataSource" = Relationship(back_populates="data_files")

    legacy_image_id: int = Field(sa_column=Column(Integer, nullable=True))
    mime_type: str = Field(sa_column=Column(String))

    _content: Optional[bytes] = None  # payload (single‑blob case)
    _samples: List[DataSample] = []  # in-memory buffer (not persisted)

    # PrivateAttr should not be saved to db
    _enforce_unique_files: bool = PrivateAttr(default=False)

    @property
    def enforce_unique_files(self) -> bool:
        """if enforce_unique_files == False, skip file hash check"""
        return self._enforce_unique_files

    @enforce_unique_files.setter
    def enforce_unique_files(self, val: bool) -> None:
        self._enforce_unique_files = val

    # ----------------------------- Paths helpers ---------------------------
    _data_dir: Optional[Path] = None

    def get_data_dir(self) -> Path:
        if self._data_dir is None:
            # FIXME: How do we best pull HighlighterRuntimeConfig out of here?
            hl_data_models_dir = HighlighterRuntimeConfig.load().data_models_dir(
                HLClient.get_client().account_name
            )
            self._data_dir = (
                hl_data_models_dir
                / get_slug(DataSource.__qualname__)
                / str(self.data_source_uuid)
                / get_slug(self.__class__.__name__)
            )
        return self._data_dir

    @property
    def uuid(self) -> UUID | None:
        """used by append_data_files_to_not_finalised_assessment"""
        return self.file_id

    @property
    def content(self) -> bytes | None:
        """Getter for content"""
        return self._content

    @content.setter
    def content(self, value: bytes):
        """Setter for content with validation"""
        if not isinstance(value, bytes):
            raise ValueError("Content must be bytes")
        self._content = value

    def add_samples(self, samples: Union[DataSample, Union[List[DataSample], Tuple[DataSample]]]) -> None:
        """Buffer one or a list of samples in RAM until `save_local()` is called and the buffer is cleared."""
        if isinstance(samples, DataSample):
            self._samples.append(samples)
        elif isinstance(samples, (list, tuple)):
            self._samples.extend(samples)

    def samples_length(self) -> int:
        return len(self._samples)

    # ----------------------------- Persistence -----------------------------
    def save_local(
        self,
        session,
        *,
        writer_opts: Optional[dict] = None,
    ) -> None:
        """Serialise buffered samples with the chosen `format_` and commit.

        Parameters
        ----------
        writer_opts
            Passed verbatim to the writer constructor obtained via
            `get_writer(format_, **writer_opts)`.
        """
        from highlighter.io.registry import get_writer

        if not self._samples:
            raise ValueError("No samples to save.")

        if self.content is not None:
            self.write_content_to_disk()
        else:
            writer_opts = writer_opts or {}

            writer = get_writer(self.content_type, **writer_opts)

            # Prepare output path
            ext = writer.extension
            filename = f"{self.file_id}.{ext}"
            out_dir = self.get_data_dir()
            os.makedirs(out_dir, exist_ok=True)
            out_path = out_dir / filename

            # Stream‑encode with on‑the‑fly hashing
            # import hashlib
            # hasher = hashlib.sha512()

            # class _HashingWrapper(io.BufferedWriter):
            #    def __init__(self, raw):
            #        super().__init__(raw)
            #    def write(self, b):  # type: ignore[override]
            #        hasher.update(b)
            #        return super().write(b)

            # try:
            #    with open(out_path, "wb") as raw, _HashingWrapper(raw) as sink:
            #        writer.write(self._samples, sink)
            # except Exception:
            #    # Clean up partial file to avoid orphaned blobs
            #    if out_path.exists():
            #        try:
            #            out_path.unlink()
            #        except OSError:
            #            pass
            #    raise

            with open(out_path, "wb") as sink:
                writer.write(self._samples, sink)

            logger.info(f" >>> DataFile written {len(self._samples)} samples")
            with open(out_path, "rb") as f:
                payload = f.read()
                file_hash = sha512_of_content(payload)

        # Update metadata
        self.original_source_url = self.original_source_url or f"{self.file_id}.{ext}"
        self.file_hash = file_hash  # hasher.hexdigest()

        session.add(self)
        session.commit()
        session.refresh(self)
        _enforce_recorded_at_is_utc(None, None, self)
        assert self.recorded_at.tzinfo is not None

        # flush buffer
        self._samples.clear()

    def save_to_cloud(self, session, hl_client=None):
        if self.original_source_url is None or self.original_source_url == "":
            raise ValueError("Error: need original_source_url to save file to cloud")

        if self.data_source_uuid is None:
            raise ValueError("Error: need data_source_uuid to save file to cloud")

        if self.recorded_at is None or self.recorded_at.tzinfo is None:
            raise ValueError("Error: need recorded_at or recorded_at timezone info")

        from highlighter.client import HLClient
        from highlighter.client.data_files import create_data_file

        hl_client = hl_client or HLClient.get_client()

        response = create_data_file(
            hl_client,
            data_file_path=self.path_to_content_file,
            data_source_uuid=self.data_source_uuid,
            recorded_at=self.recorded_at.isoformat(),
            uuid=str(self.file_id),
            content_type=self.content_type,
        )

        self.legacy_image_id = response.id
        self.mime_type = response.mime_type
        session.add(self)
        session.commit()
        _enforce_recorded_at_is_utc(None, None, self)
        assert self.recorded_at.tzinfo is not None

        logger.info(
            f"DataFile recorded_at({self.recorded_at.isoformat()}) saved to cloud with id {self.file_id} with response {response}"
        )

        return response

    @property
    def path_to_content_file(self):
        if self.original_source_url is None:
            raise ValueError(f"Error: data file with ID {self.file_id} has no original_source_url")
        else:
            return self.get_data_dir() / self.original_source_url

    def write_content_to_disk(self):
        os.makedirs(os.path.dirname(self.path_to_content_file), exist_ok=True)

        if os.path.exists(self.path_to_content_file):
            raise ValueError(f"Error: path to content file already exists for data file {self.file_id}")

        if self.content is None:
            raise ValueError(
                f"Error: trying to write content to disk and content is None for data file {self.file_id}"
            )

        with open(self.path_to_content_file, "wb") as file:
            file.write(self.content)


# TODO We can't always rely on getting session from connection
# More reliable way is to use `before_flush` hook then check if is insert, update, delete etc
def before_insert(_mapper, connection, target):
    """
    Hook method that runs just before inserting a new record
    """
    session = SASession.object_session(target)

    if session is None:
        session = Session(bind=connection)

    if target.original_source_url is None:
        raise ValueError("Error: need original_source_url to save data_file")

    if target.file_hash is None:
        if target.content is None:
            raise ValueError("DataFile content must be set before insertion")
        file_hash = sha512_of_content(target.content)
    else:
        file_hash = target.file_hash

    if target._enforce_unique_files:
        statement = select(DataFile).filter_by(file_hash=file_hash, data_source_uuid=target.data_source_uuid)
        results = session.exec(statement).all()

        if len(results) > 0:
            raise ValueError(
                f"Error: existing data_file ID(s) '{', '.join([str(df.file_id) for df in results])}' found by file_hash '{file_hash}' in agent database for data_source '{target.data_source_uuid}'"
            )

        hl_client = HLClient.get_client()
        existing_data_source_data_files = list(
            get_data_files(hl_client, file_hash=[file_hash], data_source_uuid=[str(target.data_source_uuid)])
        )

        if existing_data_source_data_files != []:
            if (
                len(existing_data_source_data_files) > 1
                or existing_data_source_data_files[0].uuid != target.file_id
            ):
                raise ValueError(
                    f"Error: file_hash {file_hash} already exists in Highlighter cloud in data_source_uuid {target.data_source_uuid} for data file ID(s) {', '.join([data_file.id for data_file in existing_data_source_data_files])}"
                )

    target.file_hash = file_hash


event.listen(DataFile, "before_insert", before_insert)


def before_delete(_mapper, connection, target):
    """
    Hook method that runs just before deleting a record
    """
    if os.path.exists(target.path_to_content_file):
        os.remove(target.path_to_content_file)


event.listen(DataFile, "before_delete", before_delete)


def _enforce_recorded_at_is_utc(mapper, connection, target: DataFile):
    """
    handle when data is written to SQLite
    """
    dt = target.recorded_at
    if dt is None:
        return
    if dt.tzinfo is None:
        target.recorded_at = dt.replace(tzinfo=timezone.utc)
    else:
        target.recorded_at = dt.astimezone(timezone.utc)


def _enforce_recorded_at_on_load(target: DataFile, context):
    _enforce_recorded_at_is_utc(None, None, target)


event.listen(DataFile, "before_insert", _enforce_recorded_at_is_utc)
event.listen(DataFile, "before_update", _enforce_recorded_at_is_utc)
event.listen(DataFile, "load", _enforce_recorded_at_on_load)
