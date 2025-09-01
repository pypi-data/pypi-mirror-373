from abc import ABC, abstractmethod
from typing import Tuple

import pandas as pd

from ..dataset import Dataset

__all__ = ["DatasetSplitter"]


class DatasetSplitter(ABC):
    @abstractmethod
    def split(self, dataset: Dataset) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass
