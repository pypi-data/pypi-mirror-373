import os
import uuid
from pathlib import Path
from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy import Column, String, event
from sqlmodel import Field, Relationship, SQLModel

from highlighter.client.gql_client import HLClient
from highlighter.core.config import HighlighterRuntimeConfig
from highlighter.core.data_models.account_mixin import AccountMixin
from highlighter.core.utilities import get_slug


# TODO Decide best way to get a session across SDK codebase
class DataFileSource(SQLModel, AccountMixin, table=True):
    data_dir: ClassVar[Optional[Path]] = None

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), sa_column=Column(String, primary_key=True))
    url: str = Field(sa_column=Column(String, default=None, primary_key=True))
    payload: str = Field(sa_column=Column(String, default=None, primary_key=True))
    request_hash: str = Field(sa_column=Column(String, default=None, primary_key=True))
    data_file_id: Optional[UUID] = Field(default=None, foreign_key="datafile.file_id")
    data_file: Optional["DataFile"] = Relationship(back_populates="data_file_sources")

    @classmethod
    def get_data_dir(cls) -> Path:
        if cls.data_dir is None:
            # FIXME: How do we best pull HighlighterRuntimeConfig out of here?
            hl_data_models_dir = HighlighterRuntimeConfig.load().data_models_dir(
                HLClient.get_client().account_name
            )
            cls.data_dir = hl_data_models_dir / get_slug(cls.__qualname__)
        return cls.data_dir

    def get_response(self):
        if self.data_file is None:
            raise ValueError(
                f"Error when getting response for DataFileSource {self.id}: No associated data file found"
            )

        return self.data_file.content

    @property
    def path_to_content_file(self):
        if self.data_file is None:
            raise ValueError(
                f"Error when getting path to content file for DataFileSource {self.id}: No associated data file found"
            )

        return self.data_file.path_to_content_file

    def write_content_to_disk(self):
        if self.data_file is None:
            raise ValueError(
                f"Error when getting path to content file for DataFileSource {self.id}: No associated data file found"
            )

        self.data_file.write_content_to_disk()


def after_load(target, _):
    """
    Called when an object is loaded from the database
    """
    if not os.path.exists(target.data_file.path_to_content_file):
        raise ValueError(f"Error: file on disk not found when loading DataFileSource id {target.id}")


event.listen(DataFileSource, "load", after_load)
