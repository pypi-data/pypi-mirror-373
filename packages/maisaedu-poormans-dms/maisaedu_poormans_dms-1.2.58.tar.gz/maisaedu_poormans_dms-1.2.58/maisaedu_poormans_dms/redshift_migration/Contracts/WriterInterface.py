from abc import ABC, abstractmethod
from typing import List
from ..Models.ExtractionOperation import ExtractionOperation


class WriterInterface(ABC):
    @abstractmethod
    def save_data(self, operations: List[ExtractionOperation]) -> None:
        pass
