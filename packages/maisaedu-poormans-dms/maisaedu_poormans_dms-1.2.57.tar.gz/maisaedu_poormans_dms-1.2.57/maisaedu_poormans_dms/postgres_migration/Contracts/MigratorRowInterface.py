from abc import ABC, abstractmethod


class MigratorRowInterface(ABC):
    @abstractmethod
    def migrate(
        self,
        source_table_name: str,
        target_table_name: str,
        incremental_column: str,
        where: str,
        on_conflict: str,
        read_batch_size: int,
        write_batch_size: int,
        copy_config: object,
        ignore_columns: object,
    ) -> None:
        pass
