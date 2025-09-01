from typing import TypeVar
from uuid import UUID

from sqlmodel import Field, select

T = TypeVar("T", bound="AccountMixin")


class AccountMixin:
    account_uuid: UUID = Field(index=True)

    @classmethod
    def base_query(cls, account_uuid: UUID):
        return select(cls).where(cls.account_uuid == account_uuid)
