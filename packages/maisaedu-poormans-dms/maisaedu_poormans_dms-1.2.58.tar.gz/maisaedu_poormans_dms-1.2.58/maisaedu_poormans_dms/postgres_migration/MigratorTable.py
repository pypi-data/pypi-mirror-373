from maisaedu_utilities_prefect.utils import build_prefect_logger
from maisaedu_utilities_prefect.database.postgres import select, execute
from dataclasses import dataclass


@dataclass
class MigratorTable:
    source_conn: object
    target_conn: object
    target_schema_name: str
    target_table_name: str
    source_schema_name: str
    source_table_name: str

    def __init__(self, source_conn: object, target_conn: object):
        self.source_conn = source_conn
        self.target_conn = target_conn

    def __get_source_create_table_code(self):
        query = f"""
            SELECT 
                (('CREATE TABLE '::text || '"' || '{self.target_schema_name}' || '"' || '.'::text || '"' || '{self.target_table_name}' || '"' ||'
            (
            '::text) || array_to_string(array_agg((((('    '::text || '"' || tabledefinition.column_name::text) || '"' || ' '::text) 
            || case 
                when tabledefinition.type ilike '%character varying%' then 'text' 
                when tabledefinition.type ilike '%citext%' then 'text' 
                else tabledefinition.type end) || ' '::text) || tabledefinition.not_null), ',
            '::text)) || '
            );
            '::text AS code
            FROM ( SELECT c.relname,
                        ns.nspname,
                        a.attname AS column_name,
                        format_type(a.atttypid, a.atttypmod) AS type,
                            CASE
                                WHEN a.attnotnull THEN 'NOT NULL'::text
                                ELSE 'NULL'::text
                            END AS not_null
                    FROM pg_class c,
                        pg_attribute a,
                        pg_type t,
                        pg_namespace ns
                    WHERE a.attrelid = c.oid AND a.atttypid = t.oid AND c.relnamespace = ns.oid
                    ORDER BY a.attnum) tabledefinition
                JOIN pg_tables pt ON pt.schemaname = tabledefinition.nspname AND pt.tablename = tabledefinition.relname
                where tabledefinition.nspname = '{self.source_schema_name}' and tabledefinition.relname = '{self.source_table_name}'
                and type not in ('oid', 'tid', 'xid', 'cid')
            GROUP BY tabledefinition.relname, tabledefinition.nspname;
        """
        result = select(self.source_conn, query)
        return result[0][0]

    def __create_target_table(self, code_create_table):
        execute(self.target_conn, code_create_table)
        execute(
            self.target_conn,
            f"ALTER TABLE {self.target_schema_name}.{self.target_table_name} OWNER TO prefect;",
        )

    def __get_source_indexes_code(self):
        query = f"""
            select indexdef from pg_catalog.pg_indexes where schemaname = '{self.source_schema_name}' and tablename = '{self.source_table_name}';
        """
        result = select(self.source_conn, query)
        return result

    def __create_target_indexes(self, indexes):
        for index in indexes:
            index_code = index[0].replace(
                f"{self.source_schema_name}.{self.source_table_name}",
                f"{self.target_schema_name}.{self.target_table_name}",
            )
            execute(self.target_conn, index_code)

    def __set_schemas_and_tables_names(self, source_table_name, target_table_name):
        slipted_source_table_name = source_table_name.split(".")
        slipted_target_table_name = target_table_name.split(".")
        self.source_schema_name = slipted_source_table_name[0]
        self.source_table_name = slipted_source_table_name[1]
        self.target_schema_name = slipted_target_table_name[0]
        self.target_table_name = slipted_target_table_name[1]

    def __check_if_target_table_already_exist(self):
        query = f"""
            select * from pg_tables as pt where pt.schemaname = '{self.target_schema_name}' AND pt.tablename = '{self.target_table_name}'
        """

        result = select(self.target_conn, query)
        if len(result) > 0:
            return True
        else:
            return False

    def create_table(self, source_table_name: str, target_table_name: str) -> None:
        self.__set_schemas_and_tables_names(source_table_name, target_table_name)
        if self.__check_if_target_table_already_exist():
            build_prefect_logger().info(
                f"Table {target_table_name} already exist, skipping process"
            )
        else:
            build_prefect_logger().info(
                f"Table {target_table_name} does not exist, creating table ..."
            )
            code_create_table = self.__get_source_create_table_code()
            self.__create_target_table(code_create_table)
            build_prefect_logger().info(f"Table {target_table_name} created")
            build_prefect_logger().info(
                f"Creating indexes for table {target_table_name} ..."
            )
            indexes = self.__get_source_indexes_code()
            self.__create_target_indexes(indexes)
            build_prefect_logger().info(
                f"Indexes for table {target_table_name} created"
            )
