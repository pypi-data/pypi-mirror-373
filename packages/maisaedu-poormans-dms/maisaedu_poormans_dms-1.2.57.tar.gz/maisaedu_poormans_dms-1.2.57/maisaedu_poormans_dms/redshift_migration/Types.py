from maisaedu_utilities_prefect.constants.env import LOCAL, DEV, PROD
from maisaedu_utilities_prefect.constants.redshift import get_iam_role

LOGGER_PREFECT = "prefect"

FULL = "full"
INCREMENTAL = "incremental"

PREFECT_DMS = "prefect-dms"
PREFECT = "prefect"

SAVED_S3 = "saved-s3"
DELETED_S3 = "deleted-s3"
PRE_DELETED_S3 = "pre-deleted-s3"
SAVED_REDSHIFT = "saved-redshift"

S3 = "s3"
REDSHIFT = "redshift"
POSTGRES = "postgres"
SQLSERVER = "sqlserver"

MAX_VARCHAR_LENGTH = 60000

SUPER = "super"
INT = "int"
BIGINT = "bigint"
VARCHAR = "varchar"
TEXT = "text"
TIMESTAMP = "timestamp"
BOOLEAN = "boolean"
STR = "str"
BOOL = "bool"
DATETIME64 = "datetime64[ns]"
DATETIME64_TZ = "datetime64[ns, UTC]"
NUMERIC = "numeric"
FLOAT = "float"
DOUBLE = "double"
TIMESTAMPTZ = "timestamptz"
JSON = "json"
JSONB = "jsonb"
UUID = "uuid"

TEST_TENANT = 2456


def target_type_is_numeric(target_type):
    if (
        target_type == INT
        or target_type == BIGINT
        or target_type == NUMERIC
        or target_type == FLOAT
        or target_type == DOUBLE
    ):
        return True
    else:
        return False


def check_if_env_is_valid(env):
    if env not in [LOCAL, DEV, PROD]:
        raise ValueError("env must be 'local', 'dev' or 'prod'")


def check_if_option_is_valid(option):
    if option not in [FULL, INCREMENTAL, None]:
        raise ValueError("option must be 'full' or 'incremental'")
