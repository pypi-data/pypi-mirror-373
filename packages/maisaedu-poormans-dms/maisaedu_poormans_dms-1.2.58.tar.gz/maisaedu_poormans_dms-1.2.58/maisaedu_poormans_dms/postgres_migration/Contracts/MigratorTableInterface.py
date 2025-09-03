from abc import ABC, abstractmethod

class MigratorTableInterface(ABC):

    @abstractmethod
    def create_table(self, source_table_name: str, target_table_name: str) -> None:
        pass