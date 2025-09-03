from ..Types import (
    SAVED_S3,
    SAVED_REDSHIFT,
    PREFECT_DMS,
    INCREMENTAL,
    PRE_DELETED_S3,
    FULL,
)
from ..Models.ExtractionOperation import ExtractionOperation as ExtractionOperationModel


class ExtractionOperation:
    def __init__(self, conn=None):
        self.conn = conn

    def create(self, struct, url, load_option, status, platform):
        cursor = self.conn.cursor()

        sql = f"""
            insert into dataeng.relations_extraction_operations
            (target_schema, target_table, url, load_option, platform, status, created_at, updated_at, received_at)
            values
            ('{struct.target_schema}', '{struct.target_table}', '{url}', '{load_option}', '{platform}', '{status}', 'now()', 'now()', 'now()')
        """

        cursor.execute(sql)

        cursor.close()

    def update(self, url, status):
        cursor = self.conn.cursor()

        sql = f"""
            update dataeng.relations_extraction_operations
            set status = '{status}', updated_at = 'now()'
            where url = '{url}'
        """

        cursor.execute(sql)
        cursor.close()

    def update_batch(self, operations, status):
        cursor = self.conn.cursor()

        sql = f"""
            update dataeng.relations_extraction_operations
            set status = '{status}', updated_at = 'now()'
            where url in ({','.join([f"'{o.url}'" for o in operations])})
        """

        cursor.execute(sql)
        cursor.close()

    def get(self, struct, limit=50):
        cursor = self.conn.cursor()

        sql = f"""
            select target_schema, target_table, url, load_option, platform, status, received_at, created_at, updated_at
            from dataeng.relations_extraction_operations
            where target_schema = '{struct.target_schema}'
            and target_table = '{struct.target_table}'
            and status = '{SAVED_S3}'
            and platform = '{PREFECT_DMS}'
            and load_option = '{INCREMENTAL}'
            order by received_at asc
            limit {limit}
        """

        cursor.execute(sql)
        operations = cursor.fetchall()
        return_operations_models = []

        for operation in operations:
            return_operations_models.append(
                ExtractionOperationModel(
                    target_schema=operation[0],
                    target_table=operation[1],
                    url=operation[2],
                    load_option=operation[3],
                    platform=operation[4],
                    status=operation[5],
                    received_at=operation[6],
                    created_at=operation[7],
                    updated_at=operation[8],
                )
            )

        cursor.close()
        return return_operations_models

    def mark_as_deleted_s3_old_full_operations(self, struct, url):
        cursor = self.conn.cursor()

        sql = f"""
            update dataeng.relations_extraction_operations
            set status = '{PRE_DELETED_S3}', updated_at = 'now()'
            where status = '{SAVED_REDSHIFT}' and url != '{url}'
            and target_table = '{struct.target_table}'
            and target_schema = '{struct.target_schema}'
            and load_option = '{FULL}'
        """

        cursor.execute(sql)
        cursor.close()
