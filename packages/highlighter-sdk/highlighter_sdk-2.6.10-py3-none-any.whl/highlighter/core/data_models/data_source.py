import logging
import uuid
from typing import List, Optional
from uuid import UUID

from gql.transport.exceptions import TransportQueryError
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from highlighter.client import HLClient
from highlighter.client.base_models.base_models import DataSourceType
from highlighter.core.data_models.account_mixin import AccountMixin
from highlighter.core.gql_base_model import GQLBaseModel

logger = logging.getLogger(__name__)


class DataSource(SQLModel, AccountMixin, GQLBaseModel, table=True):
    name: str = Field(sa_column=Column(String))
    uuid: UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True)
    data_files: list["DataFile"] = Relationship(back_populates="data_source")

    def save_to_cloud(self):
        cloud_data_source_results = None

        try:
            cloud_data_source_results = HLClient.get_client().data_source(
                return_type=DataSourceType,
                uuid=self.data_source_uuid,
            )
        except TransportQueryError as e:
            self.logger.info(
                f"data_source_id not found in Highlighter cloud: {self.data_source_id}, saving local data source to cloud"
            )

        if cloud_data_source_results is None:

            class CreateDataSourcePayload(GQLBaseModel):
                data_source: Optional[DataSourceType]
                errors: List[str]

            response = HLClient.get_client().create_data_source(
                return_type=CreateDataSourcePayload,
                uuid=str(self.uuid),
                name=self.name,
            )

            logger.info(f"DataSource saved to cloud with uuid {self.uuid} with response {response}")

            return response
        elif cloud_data_source_results.uuid != self.uuid:
            self.logger.info(
                f"data_source_id not found in Highlighter cloud: {self.data_source_id}, saving local data source to cloud"
            )
            with self.database.get_session() as session:
                self.uuid = cloud_data_source_results.uuid
                session.add(self)
                session.commit()
                session.refresh(self)
