from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field
from shapely.geometry import Polygon

from highlighter.client.base_models.annotation import Annotation
from highlighter.client.base_models.datum_source import DatumSource
from highlighter.client.base_models.entity import Entity
from highlighter.client.base_models.image import Image
from highlighter.client.base_models.observation import Observation
from highlighter.client.base_models.user import User
from highlighter.core.hl_base_model import HLDataModel, HLModelMap
from highlighter.core.labeled_uuid import LabeledUUID

__all__ = [
    "NEW_Submission",
]


class NEW_Submission(HLDataModel):

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    id: UUID
    data_file_id: int
    entities: HLModelMap = Field(..., default_factory=lambda: HLModelMap(Entity))
    created_at: datetime = Field(..., default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self):
        data = self.model_dump()
        data["id"] = str(data["id"])
        data["created_at"] = data["created_at"].isoformat()
        data["entities"] = [en.to_json() for en in data["entities"].values()]
        return data

    @classmethod
    def from_json(cls, json_path):
        # ToDo
        pass


if __name__ == "__main__":
    import json

    i = 0
    su_id = UUID(int=i)
    su = NEW_Submission(
        id=su_id,
        data_file_id=i,
    )
    for e in range(2):
        en_id = UUID(int=int(f"{i}{e}"))
        en = Entity(id=en_id)
        su.entities.add(en)

        # Add a single global observation
        gl_ob_id = UUID(int=e)
        gl_ob = Observation(
            id=gl_ob_id,
            entity_id=en_id,
            attribute_id=uuid4(),
            value=f"gl_ob_value_{e}",
            datum_source=DatumSource(confidence=0.8),
        )
        en.global_observations.add(gl_ob)

        for a in range(2):
            an_id = UUID(int=int(f"{i}{e}{a}"))
            coords = ((0, 0), (a + 10, 0), (a + 10, a + 10), (0, a + 10), (0, 0))
            an = Annotation(
                id=an_id,
                entity_id=en_id,
                location=Polygon(coords),
                datum_source=DatumSource(confidence=1.0),
            )
            en.annotations.add(an)

            for o in range(2):
                ob_id = UUID(int=int(f"{i}{e}{a}{o}"))

                ob = Observation(
                    id=ob_id,
                    entity_id=en_id,
                    attribute_id=uuid4(),
                    value=f"foo_{i}{e}{a}{o}",
                    datum_source=DatumSource(confidence=0.5),
                )
                an.observations.add(ob)

    with open("test_submission.json", "w") as f:
        json.dump(su.to_json(), f, indent=2)
