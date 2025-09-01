from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

__all__ = [
    "TestDatabase",
]


class TestDatabase:
    """The Highlighter agent database"""

    engine: Engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    def __init__(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        return Session(self.engine)
