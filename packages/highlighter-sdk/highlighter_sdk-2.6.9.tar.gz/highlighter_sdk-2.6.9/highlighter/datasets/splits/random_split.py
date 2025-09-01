from typing import List, Tuple

import numpy as np
import pandas as pd

from ...core import OBJECT_CLASS_ATTRIBUTE_UUID
from ..dataset import Dataset
from .base_splitter import DatasetSplitter

__all__ = ["RandomSplitter"]


class RandomSplitter(DatasetSplitter):
    def __init__(
        self,
        seed: int = 42,
        fracs: List[float] = [0.8, 0.2],
        names: List[str] = ["train", "test"],
        retrys: int = 10,
    ):
        if not (0.999999 < sum(fracs) < 1.00001):
            raise ValueError(f"Split fracs must sum to 1.0, got: {fracs}")

        if len(names) > len(set(names)):
            raise ValueError(f"Split names must be unique, got: {names}")

        self.seed = seed
        self.fracs = fracs
        self.names = names
        self.retrys = retrys

    def _count_unique_classes_in_split(self, data_files_df, annotations_df, split):
        split_data_file_ids = data_files_df[data_files_df.split == split].data_file_id.unique()

        df = annotations_df[annotations_df.attribute_id == OBJECT_CLASS_ATTRIBUTE_UUID]
        unique_classes = df[df.data_file_id.isin(split_data_file_ids)].value.unique()
        return unique_classes.shape[0]

    def split(self, dataset: Dataset) -> Tuple[pd.DataFrame, pd.DataFrame]:
        for _ in range(self.retrys):
            data_files_df, annotations_df = self._split(dataset)

            split_class_counts = set(
                [
                    self._count_unique_classes_in_split(data_files_df, annotations_df, split)
                    for split in self.names
                ]
            )
            if len(split_class_counts) == 1:
                return data_files_df, annotations_df
            self.seed += 1

        raise ValueError(
            f"Unable to generate splits where all object classes are in all splits. Retrys: {self.retrys}"
        )

    def _split(self, dataset: Dataset) -> Tuple[pd.DataFrame, pd.DataFrame]:
        data_file_ids = dataset.data_files_df.data_file_id.unique()
        np.random.seed(seed=self.seed)
        np.random.shuffle(data_file_ids)

        slice_start = 0
        dataset.data_files_df.loc[:, "split"] = self.names[0]
        for frac, name in zip(self.fracs[1:], self.names[1:]):
            slice_end = round(data_file_ids.shape[0] * frac) + slice_start
            split_ids = data_file_ids[slice_start:slice_end]
            dataset.data_files_df.loc[dataset.data_files_df.data_file_id.isin(split_ids), "split"] = name
            slice_start = slice_end

        return dataset.data_files_df, dataset.annotations_df
