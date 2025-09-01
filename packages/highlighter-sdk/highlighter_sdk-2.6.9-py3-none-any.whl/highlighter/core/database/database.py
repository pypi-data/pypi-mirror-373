from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from highlighter.core.config import HighlighterRuntimeConfig

__all__ = [
    "Database",
]


class Database:
    """The Highlighter agent database"""

    def __init__(self):
        # FIXME: How do we best pull HighlighterRuntimeConfig out of here?
        hl_cfg = HighlighterRuntimeConfig.load()
        self.highlighter_path_to_database_file = str(hl_cfg.agent.db_file())
        SQLModel.metadata.create_all(self.engine)

    @property
    def engine(self) -> Engine:
        return create_engine(
            f"sqlite:///{self.highlighter_path_to_database_file}", connect_args={"check_same_thread": False}
        )

    def get_session(self):
        return Session(self.engine)
