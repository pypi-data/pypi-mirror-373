from abc import ABC, abstractmethod
from typing import List, Tuple

from .base_models import AttributeRecord, ImageRecord


class IReader(ABC):
    @abstractmethod
    def read(self) -> Tuple[List[AttributeRecord], List[ImageRecord]]:
        pass


class IWriter(ABC):
    """
    Create a concrete implementation of this class to write
    a dataset to disk
    """

    @abstractmethod
    def write(self, dataset: "Dataset"):
        pass
