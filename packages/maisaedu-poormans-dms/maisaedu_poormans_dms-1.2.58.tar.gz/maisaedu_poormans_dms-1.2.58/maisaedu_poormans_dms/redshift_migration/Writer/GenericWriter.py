from ..Types import PROD


class GenericWriter:
    def __init__(self, env, struct, migrator_redshift_connector, logger):
        self.env = env
        self.struct = struct
        self.migrator_redshift_connector = migrator_redshift_connector
        self.logger = logger

    def set_temp_target_relation(self):
        self.temp_target_relation = (
            f'"temp_{self.struct.target_schema}_{self.struct.target_table}"'
        )

    def set_target_relation(self):
        self.target_relation = (
            f'"{self.struct.target_schema}"."{self.struct.target_table}"'
        )

    def create_table_temp_target_relation(self):
        self.target_cursor.execute(
            f"""
                CREATE TEMP TABLE {self.temp_target_relation} (LIKE {self.target_relation});
            """
        )

    def create_table_temp_target_relation_to_remove_dups(self):
        columns = []
        for a in self.struct.columns_upsert:
            columns.append(f'"{a}"')

        pk_columns = ', '.join(columns)

        self.target_cursor.execute(
            f"""
                create temp table {self.temp_target_relation} as (
                    SELECT distinct a.* FROM {self.target_relation} as a
                    join (
                        SELECT {pk_columns}, count(*) FROM {self.target_relation} 
                        group by {pk_columns} having count(*) > 1
                    ) as subselect 
                        on 1=1 
                        {self.create_statement_comparison_pk_columns('subselect', 'a')}
                );
            """
        )

    def copy_data_to_target(self, url, target):
        self.target_cursor.execute(
            f"""
                COPY {target}
                FROM '{url}'
                IAM_ROLE '{self.migrator_redshift_connector.iam_role}'
                FORMAT AS CSV
                BLANKSASNULL
                TRUNCATECOLUMNS
                IGNOREHEADER 1
                TIMEFORMAT 'auto'
            """
        )

    def insert_data_from_temp_to_target(self):
        self.target_cursor.execute(
            f"""
                INSERT INTO {self.target_relation}
                SELECT * FROM {self.temp_target_relation};
            """
        )

    def delete_using_temp_target_from_target(self):
        self.target_cursor.execute(
            f"""
                    DELETE FROM {self.target_relation}
                    USING {self.temp_target_relation}
                    WHERE 1=1
                        {self.create_statement_comparison_pk_columns(self.target_relation, self.temp_target_relation)}
                    ;
                """
        )

    def delete_all_data_from_target(self):
        self.target_cursor.execute(
            f"""
                DELETE FROM {self.target_relation};
            """
        )

    def drop_table_temp_target_relation(self):
        self.target_cursor.execute(
            f"""
                DROP TABLE {self.temp_target_relation};
            """
        )

    def get_serialization_if_has_super(self):
        for c in self.struct.columns:
            if c["target_type"] == "super":
                return "SERIALIZETOJSON"
        return ""

    def create_statement_comparison_pk_columns(self, target_relation, temp_target_relation):
        statement_upsert = ""
        for c in self.struct.columns_upsert:
            statement_upsert = (
                statement_upsert
                + f"""
                    and {target_relation}."{c}" = {temp_target_relation}."{c}" 
                """
            )

        return statement_upsert
    
    def clean_duplicate_inconsistencies(self):
        cursor = self.migrator_redshift_connector.target_conn.cursor()

        self.target_cursor = cursor

        self.migrator_redshift_connector.target_conn.autocommit = False

        self.set_temp_target_relation()
        self.set_target_relation()
        self.create_table_temp_target_relation_to_remove_dups()
        self.delete_using_temp_target_from_target()
        self.insert_data_from_temp_to_target()
        self.drop_table_temp_target_relation()

        self.migrator_redshift_connector.target_conn.commit()
        self.migrator_redshift_connector.target_conn.autocommit = True

    def save_to_redshift(self, operations):
        cursor = self.migrator_redshift_connector.target_conn.cursor()

        self.target_cursor = cursor

        self.set_temp_target_relation()
        self.set_target_relation()

        if len(self.struct.columns_upsert) == 0:
            self.is_upsert = False
        else:
            self.is_upsert = True

        self.save_data(operations)
