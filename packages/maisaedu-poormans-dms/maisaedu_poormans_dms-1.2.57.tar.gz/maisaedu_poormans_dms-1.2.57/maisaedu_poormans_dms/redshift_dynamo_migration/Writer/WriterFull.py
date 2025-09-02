from maisaedu_utilities_prefect.constants.redshift import get_iam_role
from ..models.Struct import Struct

TEMP_TABLE_NAME = 'tmp_full'
MAX_ERRORS = 100

class WriterFull:
    def __init__(self, env, conn, logger, struct: Struct):
        self.env = env
        self.conn = conn
        self.logger = logger
        self.struct = struct
        self.iam_role = get_iam_role(env)

        self.partition_key = self.struct.partition_key
        self.sort_key = self.struct.sort_key
        self.target = f"{self.struct.target_schema}.{self.struct.target_table}"

    def create_temp_table(self):
        self.cursor.execute(f"""
          CREATE TEMP TABLE {TEMP_TABLE_NAME} (
            id bigint identity(1,1) primary key,
            item super
          );
        """)

    def copy_data_to_target(self):
        self.cursor.execute(
            f"""
              COPY {TEMP_TABLE_NAME}
                FROM '{self.struct.s3_url}'
                IAM_ROLE '{self.iam_role}'
                GZIP JSON 'auto ignorecase'
                MAXERROR {MAX_ERRORS};
            """
        )

    def truncate_target_table(self):
        self.cursor.execute(f"TRUNCATE TABLE {self.target}")

    def insert_data_from_temp_to_target(self):
        self.cursor.execute(
            f"""
                INSERT INTO {self.target} (partition_key, sort_key, item, updated_at)
                SELECT
                  item.{self.partition_key}::varchar AS partition_key,
                  item.{self.sort_key}::varchar AS sort_key,
                  item,
                  NULL
                FROM
                  tmp_full;
            """
        )

    def cleanup(self):
        self.cursor.execute(f"DROP TABLE {TEMP_TABLE_NAME}")

    def save(self):
        with self.conn.redshift.cursor() as cursor:
            self.cursor = cursor

            self.create_temp_table()
            self.copy_data_to_target()
            self.truncate_target_table()
            self.insert_data_from_temp_to_target()
            self.cleanup()