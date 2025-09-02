from ..Types import (
    target_type_is_numeric,
    LOCAL,
    FULL,
    INCREMENTAL,
)
from .GenericReader import GenericReader
from ..Contracts.ReaderInterface import ReaderInterface

class PostgresReader(GenericReader, ReaderInterface):
    def get_incremental_statement(self):
        if (
            (
                self.struct.source_incremental_column is not None
                and self.struct.target_incremental_column is not None
                and (self.load_option is None) 
            ) or (self.load_option == INCREMENTAL)
        ):
            sql = f"""
                select max("{self.struct.target_incremental_column}") as max_value
                from "{self.struct.target_schema}"."{self.struct.target_table}"
            """

            cursor = self.migrator_redshift_connector.target_conn.cursor()

            cursor.execute(sql)
            result = cursor.fetchall()

            if len(result) == 0 or result[0][0] is None:
                sql_return = ""
                self.load_option = FULL
            else:
                for c in self.struct.columns:
                    if c["target_name"] == self.struct.target_incremental_column:
                        target_type = c["target_type"]

                if target_type_is_numeric(target_type):
                    sql_return = f'and "{self.struct.source_incremental_column}" > {result[0][0]}'
                else:
                    if (
                        self.struct.incremental_interval_delta is None
                        or self.struct.incremental_interval_delta == ""
                    ):
                        sql_return = f"and \"{self.struct.source_incremental_column}\" > '{result[0][0]}'"
                    else:
                        sql_return = f"and \"{self.struct.source_incremental_column}\" >= '{result[0][0]}'::timestamp - interval '{self.struct.incremental_interval_delta}'"

                self.load_option = INCREMENTAL

            cursor.close()

            return sql_return
        else:
            if (self.load_option is None):
                self.load_option = FULL
            return ""

    def get_columns_source(self):
        return " * "

    def get_order_by_sql_statement(self):
        if self.struct.source_incremental_column is not None:
            return f' order by "{self.struct.source_incremental_column}" asc'
        else:
            return ""

    def get_limit_sql_statement(self):
        if self.migrator_redshift_connector.env == LOCAL:
            return f" limit 100"
        else:
            return f""

    def get_sql_statement(self):
        sql = f"""
            select {self.get_columns_source()} 
            from "{self.struct.source_schema}"."{self.struct.source_table}" 
            where 1=1
            {self.get_incremental_statement()} 
            {self.get_order_by_sql_statement()}
            {self.get_limit_sql_statement()}
        """
        return sql
