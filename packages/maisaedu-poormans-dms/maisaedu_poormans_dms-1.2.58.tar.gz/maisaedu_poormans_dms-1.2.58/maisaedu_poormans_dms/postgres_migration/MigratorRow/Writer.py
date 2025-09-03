from maisaedu_utilities_prefect.database.postgres import (
    select,
    execute,
    copy,
    insert_batch,
)
from ..Contracts.MigratorRowWriterInterface import MigratorRowWriterInterface
from dataclasses import dataclass
from psycopg2.extras import Json


@dataclass
class MigratorWriter(MigratorRowWriterInterface):
    source_conn: object
    target_conn: object
    write_batch_size: int
    on_conflict: str
    copy_config: object
    ignore_columns: object
    use_copy: bool = True

    def __init__(
        self,
        target_conn: object,
        target_table_name: object,
        write_batch_size: int,
        on_conflict: str,
        copy_config: object,
        ignore_columns: object,
        use_copy: bool = True
    ):
        self.target_conn = target_conn
        self.target_table_name = target_table_name
        self.write_batch_size = write_batch_size
        self.on_conflict = on_conflict
        self.copy_config = copy_config
        self.ignore_columns = ignore_columns
        self.use_copy = use_copy

    def __bind_on_conflict(self):
        if self.on_conflict is True:
            self.on_conflict = ''
        if self.on_conflict is None:
            return self.on_conflict
        if "[[all]]" in self.on_conflict.lower():
            result = select(
                self.target_conn,
                f"""
                select STRING_AGG('"' || column_name || '"=excluded."' || column_name || '"', ', ')
                FROM information_schema.columns
                WHERE table_schema || '.' || table_name = '{self.target_table_name}';
            """,
            )
            return self.on_conflict.replace("[[all]]", result[0][0])
        else:
            return self.on_conflict

    def __check_ignore_column_value(self, column):
        if column in list(map(lambda x: x.lower(), self.ignore_columns)):
            return True
        else:
            return False

    def truncate_target_table(self, default_commit: bool) -> None:
        query = f"delete from {self.target_table_name}"
        execute(self.target_conn, query, default_commit)

    def insert_data_into_target_table(
        self, batches: list, columns_names: list, default_commit: bool
    ) -> float:
        on_conflict = self.__bind_on_conflict()

        total_inserted = 0
        for batch in batches:
            insert_list = []
            for row in batch:
                insert_row = {}
                for index, value in enumerate(row):
                    if self.__check_ignore_column_value(columns_names[index]):
                        insert_row['"' + columns_names[index] + '"'] = None
                    else:
                        if type(value) == str:
                            if value == "":
                                insert_row['"' + columns_names[index] + '"'] = " "
                            else:
                                value = value.replace(";", "semicolon")
                                value = value.replace("\r", "")
                                insert_row[
                                    '"' + columns_names[index] + '"'
                                ] = value.replace("\n", "")
                        elif type(value) == dict:
                            insert_row['"' + columns_names[index] + '"'] = Json(value)
                        else:
                            insert_row['"' + columns_names[index] + '"'] = value

                insert_list.append(insert_row)

                if len(insert_list) > self.write_batch_size:
                    if self.on_conflict is None and self.use_copy:
                        copy(
                            self.target_conn,
                            self.target_table_name,
                            insert_list,
                            copy_config=self.copy_config,
                            default_commit=default_commit,
                        )
                    else:
                        on_conflict = '' if on_conflict is None else on_conflict
                        insert_batch(
                            self.target_conn,
                            insert_list,
                            self.target_table_name,
                            on_conflict,
                            self.write_batch_size,
                            default_commit,
                        )
                    total_inserted += len(insert_list)
                    insert_list = []

            if len(insert_list) > 0:
                if self.on_conflict is None and self.use_copy:
                    copy(
                        self.target_conn,
                        self.target_table_name,
                        insert_list,
                        copy_config=self.copy_config,
                        default_commit=default_commit,
                    )
                else:
                    on_conflict = '' if on_conflict is None else on_conflict
                    insert_batch(
                        self.target_conn,
                        insert_list,
                        self.target_table_name,
                        on_conflict,
                        self.write_batch_size,
                        default_commit,
                    )
                total_inserted += len(insert_list)

        return total_inserted
