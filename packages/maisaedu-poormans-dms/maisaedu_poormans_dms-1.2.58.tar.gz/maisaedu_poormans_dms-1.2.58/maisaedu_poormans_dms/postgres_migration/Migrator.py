from maisaedu_utilities_prefect.database.postgres import connect
from .MigratorTable import MigratorTable
from .MigratorRow.MigratorRow import MigratorRow
from .Contracts.MigratorInterface import MigratorInterface
from dataclasses import dataclass


@dataclass
class Migrator(MigratorInterface):
    source_dsn: str
    target_dsn: str
    source_conn: object
    target_conn: object

    def __init__(self, source_dsn: str, target_dsn: str):
        self.source_dsn = source_dsn
        self.target_dsn = target_dsn

    def __create_source_connection(self):
        self.source_conn = connect(self.source_dsn)

    def __create_target_connection(self):
        self.target_conn = connect(self.target_dsn)

    def __close_source_connection(self):
        self.source_conn.close()

    def __close_target_connection(self):
        self.target_conn.close()

    def create_table(self, source_table_name: str, target_table_name: str):
        self.__create_source_connection()
        self.__create_target_connection()
        migrator_table = MigratorTable(self.source_conn, self.target_conn)
        migrator_table.create_table(source_table_name, target_table_name)
        self.__close_source_connection()
        self.__close_target_connection()

    def migrate(
        self,
        source_table_name: str,
        target_table_name: str,
        incremental_column: str = None,
        where: str = "1=1",
        on_conflict: str = None,
        read_batch_size: int = 10000,
        write_batch_size: int = 10000,
        copy_config: object = None,
        ignore_columns: object = [],
        use_copy: bool = True,
    ) -> None:
        self.__create_source_connection()
        self.__create_target_connection()
        migrator_table = MigratorRow(self.source_conn, self.target_conn)
        migrator_table.migrate(
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
        self.__close_source_connection()
        self.__close_target_connection()
