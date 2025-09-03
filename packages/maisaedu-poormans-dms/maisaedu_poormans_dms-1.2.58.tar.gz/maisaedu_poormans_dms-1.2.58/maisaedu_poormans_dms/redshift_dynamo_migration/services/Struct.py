import boto3
from ..models.Struct import Struct as StructModel
from ..Connector import Connector

SOURCE_ENGINE = "dynamo"
AWS_REGION = "us-east-1"
DEFAULT_INCREMENTAL_INTERVAL_DELTA = 3600

class Struct:
    def __init__(self, env=None, aws_credentials=None):
        self.conn = Connector(env)
        self.conn.connect()

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_credentials["aws_edtech_prefect_deploy_access_key_id"],
            aws_secret_access_key=aws_credentials["aws_edtech_prefect_deploy_secret_access_key"],
            region_name=AWS_REGION
        )

    def get(self, database, bucket, tables="all"):
        with self.conn.redshift.cursor() as cursor:
            clause = ""
            if tables != "all":
                joined_tables = ",".join(map(lambda t: f"'{t}'", tables))
                clause = f"and target_table in ({joined_tables})"

            cursor.execute(
                f"""
                  select 
                      database,
                      source_schema,
                      source_table,
                      target_schema,
                      target_table,
                      source_dynamo_partition_key,
                      source_dynamo_sort_key,
                      incremental_interval_delta
                  from 
                      dataeng.relations_extraction
                  where
                      source_engine = '{SOURCE_ENGINE}'
                      and database = '{database}'
                      and is_active is true
                      {clause}
              """
            )

            relations_extraction = cursor.fetchall()
            structs = []

            for r in relations_extraction:
                base_url = f"s3://{bucket}"
                prefix = f"raw/dynamo/full/{r[2]}/AWSDynamoDB/"
                s3_objects = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")

                if "CommonPrefixes" not in s3_objects:
                    raise ValueError(f"No data found in {prefix}")
                
                latest_folder = max(s3_objects["CommonPrefixes"], key=lambda x: x["Prefix"])
                s3_url = latest_folder["Prefix"]

                structs.append(
                    StructModel(
                        database=r[0],
                        source_schema=r[1],
                        source_table=r[2],
                        target_schema=r[3],
                        target_table=r[4],
                        partition_key=r[5],
                        sort_key=r[6],
                        incremental_interval_delta=r[7] or DEFAULT_INCREMENTAL_INTERVAL_DELTA,
                        s3_url=f"{base_url}/{s3_url}data"
                    )
                )

        return structs
    
    def __del__(self):
        self.conn.close()
