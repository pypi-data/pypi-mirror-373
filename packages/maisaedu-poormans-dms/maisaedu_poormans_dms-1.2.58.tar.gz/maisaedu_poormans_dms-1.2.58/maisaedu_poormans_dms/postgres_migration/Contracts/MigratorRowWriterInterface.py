from abc import ABC, abstractmethod


class MigratorRowWriterInterface(ABC):
    @abstractmethod
    def truncate_target_table(self, default_commit: bool) -> None:
        pass

    @abstractmethod
    def insert_data_into_target_table(
        self, batches: list, columns_names: list, default_commit: bool
    ) -> float:
        pass
