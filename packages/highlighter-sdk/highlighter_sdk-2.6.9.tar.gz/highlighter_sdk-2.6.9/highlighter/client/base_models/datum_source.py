from typing import Optional

from ...core import GQLBaseModel

__all__ = ["DatumSource"]


class DatumSource(GQLBaseModel):
    """How did a piece-of-data 'datum' come to be."""

    frame_id: Optional[int] = None
    host_id: Optional[str] = None
    pipeline_element_name: Optional[str] = None
    training_run_id: Optional[int] = None
    confidence: float

    def to_json(self):
        return self.model_dump()

    def serialize(self):
        return self.to_json()
