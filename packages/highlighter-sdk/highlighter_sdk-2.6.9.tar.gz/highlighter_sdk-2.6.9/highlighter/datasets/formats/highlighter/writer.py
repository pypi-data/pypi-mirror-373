from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from shapely.geometry.base import BaseGeometry
from tqdm import tqdm

from ....client import EAVT, DatumSource, HLClient, ObjectClass
from ....client import SubmissionType as Submission
from ....core import GQLBaseModel, LabeledUUID
from ...interfaces import IWriter

tqdm.pandas()


def is_valid_uuid(attr_id):
    if isinstance(attr_id, (LabeledUUID, UUID)):
        return True
    try:
        UUID(attr_id)
        return True
    except (ValueError, TypeError):
        return False


class CreateSubmissionPayload(GQLBaseModel):
    submission: Optional[Submission] = None
    errors: List[str]


class HighlighterAssessmentsWriter(IWriter):
    format_name = "highlighter_assessments"

    def __init__(
        self,
        client: HLClient,
        workflow_id: int,
        object_class_uuid_lookup: Optional[Dict[str, str]] = None,
        user_id: Optional[int] = None,
    ):
        self.client = client
        self.user_id = user_id
        self.workflow_id = workflow_id

        if object_class_uuid_lookup is None:
            self.object_class_uuid_lookup = self._get_project_object_class_uuid_lookup()
        else:
            self.object_class_uuid_lookup = object_class_uuid_lookup

    def _get_project_object_class_uuid_lookup(self):
        class Project(GQLBaseModel):
            object_classes: List[ObjectClass]

        object_classes = self.client.project(return_type=Project, id=self.workflow_id).object_classes
        lookup = {o.name: o.uuid for o in object_classes}
        lookup.update({o.id: o.uuid for o in object_classes})
        return lookup

    def write(
        self,
        dataset: "Dataset",
    ):
        """Write to highlighter assessments in project"""

        def img_group_to_subs(name, grp, dataset):
            data_file_id = name
            attrs = grp.to_dict("records")

            eavt_attrs = []
            for attr in attrs:
                entity_id = attr["entity_id"]
                attr_id = attr["attribute_id"]

                if is_valid_uuid(attr_id):
                    # Cast/validate attribute value
                    value = attr["value"]

                    if isinstance(value, str):
                        value = str(self.object_class_uuid_lookup.get(value, value))

                    # Is a shapely object
                    if isinstance(value, BaseGeometry):
                        value = value.wkt

                    eavt_attrs.append(
                        EAVT(
                            entity_id=entity_id,
                            attribute_id=attr_id,
                            value=value,
                            datum_source=DatumSource(confidence=float(attr["confidence"])),
                        ).gql_dict()
                    )
                else:
                    warnings.warn((f"Skipping invallid attribute_id, got: '{attr_id}'"))

            kwargs = {"userId": self.user_id}
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            response = self.client.create_submission(
                return_type=CreateSubmissionPayload,
                projectId=self.workflow_id,
                imageId=data_file_id,
                status="completed",
                startedAt=datetime.now(timezone.utc).isoformat(),
                eavtAttributes=eavt_attrs,
                **kwargs,
            )

            if (response.submission is None) or (response.errors):
                warnings.warn(
                    f"Failed to create assessment: {response.errors}\n{eavt_attrs}\ndata_file: {data_file_id}\nworkflow: {self.workflow_id} "
                )

            # We check if data_files_df is populated before adding these fields
            # because when we're just performing inference we may not have this
            # DataFrame populated.
            elif dataset.data_files_df.shape[0] > 0:
                # update assessment_id and hash
                dataset.data_files_df.loc[
                    dataset.data_files_df.data_file_id == data_file_id, "assessment_id"
                ] = response.submission.id
                dataset.data_files_df.loc[
                    dataset.data_files_df.data_file_id == data_file_id, "hash_signature"
                ] = response.submission.hash_signature

        # group annotations by data_file id and create assessments
        for name, grp in tqdm(dataset.annotations_df.groupby("data_file_id")):
            img_group_to_subs(name, grp, dataset)
