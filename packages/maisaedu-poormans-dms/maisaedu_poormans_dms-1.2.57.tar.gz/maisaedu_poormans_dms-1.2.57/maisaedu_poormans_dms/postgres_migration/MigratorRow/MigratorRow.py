from maisaedu_utilities_prefect.utils import build_prefect_logger

from .Reader import MigratorReader
from .Writer import MigratorWriter
from ..Contracts.MigratorRowInterface import MigratorRowInterface
from dataclasses import dataclass


@dataclass
class MigratorRow(MigratorRowInterface):
    source_conn: object
    target_conn: object
    target_table_name: str
    source_table_name: str
    incremental_column: str
    where: str
    on_conflict: str
    read_batch_size: int
    write_batch_size: int
    copy_config: object
    ignore_columns: object
    migrator_reader: MigratorReader
    migrator_writer: MigratorWriter

    def __init__(self, source_conn: object, target_conn: object):
        self.source_conn = source_conn
        self.target_conn = target_conn

    def __set_configs(
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
        use_copy: bool = True,
    ):
        self.source_table_name = source_table_name
        self.target_table_name = target_table_name
        self.incremental_column = incremental_column
        self.where = where
        self.on_conflict = on_conflict
        self.read_batch_size = read_batch_size
        self.write_batch_size = write_batch_size
        self.copy_config = copy_config
        self.ignore_columns = ignore_columns
        self.use_copy = use_copy

    def __init_dependencies(self):
        self.migrator_reader = MigratorReader(
            self.source_conn,
            self.target_conn,
            self.source_table_name,
            self.target_table_name,
            self.incremental_column,
            self.where,
            self.read_batch_size,
        )
        self.migrator_writer = MigratorWriter(
            self.target_conn,
            self.target_table_name,
            self.write_batch_size,
            self.on_conflict,
            self.copy_config,
            self.ignore_columns,
            self.use_copy,
        )

    def __migrate_without_incremental_column(self):
        default_commit = False

        build_prefect_logger().info(f"Truncating {self.target_table_name} table ...")
        self.migrator_writer.truncate_target_table(default_commit)
        build_prefect_logger().info(f"Table {self.target_table_name} truncated")

        build_prefect_logger().info(
            f"Getting data from {self.source_table_name} table in batches and inserting into {self.target_table_name} table ..."
        )
        columns_names = self.migrator_reader.get_columns_names(
            self.migrator_reader.get_source_query_without_incremental_column
        )
        batches = self.migrator_reader.get_source_data(
            self.migrator_reader.get_source_query_without_incremental_column, "full"
        )
        total_inserted = self.migrator_writer.insert_data_into_target_table(
            batches, columns_names, default_commit
        )
        build_prefect_logger().info(
            f"Inserted {total_inserted} rows into {self.target_table_name} table"
        )

        self.target_conn.commit()

    def __migrate_with_incremental_column(self):
        default_commit = True

        build_prefect_logger().info(
            f"Getting data from {self.source_table_name} table in batches and inserting into {self.target_table_name} table ..."
        )
        columns_names = self.migrator_reader.get_columns_names(
            self.migrator_reader.get_source_query_with_incremental_column
        )
        batches = self.migrator_reader.get_source_data(
            self.migrator_reader.get_source_query_with_incremental_column, "incremental"
        )
        total_inserted = self.migrator_writer.insert_data_into_target_table(
            batches, columns_names, default_commit
        )
        build_prefect_logger().info(
            f"Inserted {total_inserted} rows into {self.target_table_name} table"
        )

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
        use_copy: bool = True,
    ) -> None:
        self.__set_configs(
            source_table_name,
            target_table_name,
            incremental_column,
            where,
            on_conflict,
            read_batch_size,
            write_batch_size,
            copy_config,
            ignore_columns,
            use_copy,
        )
        self.__init_dependencies()

        if self.incremental_column is None:
            self.__migrate_without_incremental_column()
        else:
            self.__migrate_with_incremental_column()
