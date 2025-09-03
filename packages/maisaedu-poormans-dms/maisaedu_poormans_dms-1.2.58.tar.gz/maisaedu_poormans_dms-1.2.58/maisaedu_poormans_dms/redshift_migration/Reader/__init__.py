from .PostgresReader import PostgresReader
from .SQLServerReader import SQLServerReader
from ..Types import POSTGRES, SQLSERVER


def factory(s3_credentials, struct, migrator_redshift_connector):
    if migrator_redshift_connector.source_conn_type == POSTGRES:
      return PostgresReader(s3_credentials, struct, migrator_redshift_connector)
    elif migrator_redshift_connector.source_conn_type == SQLSERVER:
      return SQLServerReader(s3_credentials, struct, migrator_redshift_connector)