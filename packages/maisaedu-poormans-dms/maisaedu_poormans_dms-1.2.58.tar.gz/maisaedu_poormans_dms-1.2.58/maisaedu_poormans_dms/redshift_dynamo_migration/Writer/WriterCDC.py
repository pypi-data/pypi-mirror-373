from ..models.Struct import Struct

class WriterCDC:
    def __init__(self, env, conn, logger, struct: Struct):
        self.env = env
        self.conn = conn
        self.logger = logger
        self.struct = struct

        self.partition_key = self.struct.partition_key
        self.sort_key = self.struct.sort_key

        self.target = f"{self.struct.target_schema}.{self.struct.target_table}"
        self.view_name = self._get_view_name()

    def _get_view_name(self):
        table_name = self.struct.target_table.replace("dynamo_", "")
        return f"{self.struct.source_schema}.{self.struct.database}_{table_name}_stream"

    def create_temp_table(self):
        self.cursor.execute(f"""
            CREATE TEMP TABLE tmp_cdc (
              event_name varchar(255),
              partition_key varchar(2048),
              sort_key varchar(2048),
              item super,
              updated_at timestamp
            );
            REFRESH MATERIALIZED VIEW {self.view_name};
        """)

    def insert_data_to_temp(self):
        self.cursor.execute(f"""
            INSERT INTO tmp_cdc
            SELECT
              "payload"."eventName"::varchar AS event_name,
              "payload"."dynamodb"."Keys".{self.partition_key}::varchar AS partition_key,
              "payload"."dynamodb"."Keys".{self.sort_key}::varchar AS sort_key,
              "payload"."dynamodb"."NewImage" AS item,
              TIMESTAMP 'epoch' + ("payload"."dynamodb"."ApproximateCreationDateTime"::bigint / 1e6) * INTERVAL '1 second' AS updated_at
            FROM (
                   SELECT *,
                          ROW_NUMBER() OVER (PARTITION BY "payload"."dynamodb"."Keys".{self.partition_key}, "payload"."dynamodb"."Keys".{self.sort_key} ORDER BY "payload"."dynamodb"."ApproximateCreationDateTime" DESC) as row_num
                   FROM {self.view_name}
                   WHERE
                        (("payload"."dynamodb"."ApproximateCreationDateTime"::bigint) / 1e6) > (coalesce(extract('epoch' from (select max(updated_at) from {self.target})), 0) - {self.struct.incremental_interval_delta})
                 ) subquery
            WHERE row_num = 1;
        """)

    def delete_records(self):
        self.cursor.execute(f"""
            CREATE TEMP TABLE tmp_delete_ids (partition_key varchar(2048), sort_key varchar(2048));
            INSERT INTO tmp_delete_ids
            SELECT partition_key, sort_key
            FROM tmp_cdc
            WHERE event_name = 'REMOVE';

            DELETE FROM {self.target}
            USING tmp_delete_ids tmp
            WHERE
                {self.target}.partition_key = tmp.partition_key
                AND {self.target}.sort_key = tmp.sort_key
        """)

    def insert_records(self):
        self.cursor.execute(f"""
            INSERT INTO {self.target} (partition_key, sort_key, item, updated_at)
            SELECT
              tmp.partition_key,
              tmp.sort_key,
              tmp.item,
              tmp.updated_at
            FROM tmp_cdc tmp
            LEFT JOIN {self.target} t ON tmp.partition_key = t.partition_key AND tmp.sort_key = t.sort_key
            WHERE tmp.event_name IN ('INSERT', 'MODIFY') AND t.id IS NULL
        """)

    def update_records(self):
        self.cursor.execute(f"""
            UPDATE {self.target} t
            SET
                item = tmp.item,
                updated_at = tmp.updated_at
            FROM tmp_cdc tmp
            WHERE t.partition_key = tmp.partition_key AND t.sort_key = tmp.sort_key
                AND tmp.event_name = 'MODIFY';
        """)

    def cleanup(self):
        self.cursor.execute(f"""
            DROP TABLE tmp_delete_ids;
            DROP TABLE tmp_cdc;
        """)

    def save(self):
        with self.conn.redshift.cursor() as cursor:
            self.cursor = cursor

            self.create_temp_table()
            self.insert_data_to_temp()
            self.delete_records()
            self.insert_records()
            self.update_records()
            self.cleanup()