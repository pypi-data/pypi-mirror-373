from typing import Optional
from dataclasses import dataclass

@dataclass
class Struct:
    s3_url: str # S3 URL for the full load
    database: str # Database name, used to build the table names in the queries
    source_schema: str # Schema where the MVW is
    source_table: str # DynamoDB table name

    target_schema: str
    target_table: str
    
    partition_key: str
    sort_key: Optional[str]

    incremental_interval_delta: int # Interval in seconds to consider for incremental loads