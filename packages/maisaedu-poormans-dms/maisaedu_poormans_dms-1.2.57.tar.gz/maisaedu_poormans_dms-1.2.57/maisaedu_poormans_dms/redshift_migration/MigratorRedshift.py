import os
import subprocess

from .Connector import Connector
from .Reader import factory as reader_factory
from .Logger import Logger
from .Writer import factory as writer_factory
from .Services.Struct import Struct
from .Services.ExtractionOperation import ExtractionOperation
from .Services.RelationExtraction import RelationExtraction
from .Types import (
    check_if_env_is_valid,
    check_if_option_is_valid,
    FULL,
    PREFECT,
    PREFECT_DMS,
    SAVED_REDSHIFT,
    SQLSERVER,
    LOCAL,
    TEST_TENANT
)


class MigratorRedshift:
    def __init__(
        self,
        env=None,
        s3_credentials=None,
        struct=None,
        source_credentials=None,
        target_credentials=None,
        dms_read_batch_size=50,
        logger=None,
        overwrite_read_batch_size=None
    ):
        check_if_env_is_valid(env)

        self.migrator_redshift_connector = Connector(
            env=env,
            s3_credentials=s3_credentials,
            source_credentials=source_credentials,
            target_credentials=target_credentials,
        )

        self.migrator_redshift_connector.connect_target()

        self.migrator_redshift_reader = reader_factory(
            s3_credentials=s3_credentials,
            struct=struct,
            migrator_redshift_connector=self.migrator_redshift_connector,
        )

        self.source_credentials = source_credentials
        self.struct = struct
        self.s3_credentials = s3_credentials
        self.env = env
        self.dms_read_batch_size = dms_read_batch_size
        self.logger = Logger(logger=logger)
        self.target_table_has_data = False

        if overwrite_read_batch_size is not None:
            self.struct.read_batch_size = overwrite_read_batch_size

    def __check_target_table_has_data(self):
        sql = f"""
            select count(*) from "{self.struct.target_schema}"."{self.struct.target_table}" limit 1
        """
        cursor = self.migrator_redshift_connector.target_conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        if result[0][0] == 0:
            self.target_table_has_data = False
        else:
            self.target_table_has_data = True

    def __check_table_will_be_updated_by_cdc(self, load_option):
        if (
            load_option == FULL
            or self.struct.extraction_engine == PREFECT
            or (
                self.struct.extraction_engine == PREFECT_DMS
                and self.target_table_has_data is False
            )
        ):
            return False
        else:
            return True
        
    def __run_incremental_cdc_flow(self):
        perfomed_operations = False
        has_more = True
        extraction_operation_service = ExtractionOperation(
            conn=self.migrator_redshift_connector.target_conn
        )
        while has_more:
            operations = extraction_operation_service.get(
                struct=self.struct, limit=self.dms_read_batch_size
            )

            if len(operations) == 0:
                has_more = False
            else:
                self.migrator_redshift_writer.save_to_redshift(operations)

                extraction_operation_service.update_batch(
                    operations=operations,
                    status=SAVED_REDSHIFT,
                )

                perfomed_operations = True
        
        return perfomed_operations

    def __run_non_cdc_flow(self, load_option):
        perfomed_operations = False

        operation = self.migrator_redshift_reader.save_data_to_s3(load_option)
        self.logger.info(f"Finished saving data to S3")
        if operation is not None:
            self.migrator_redshift_writer.save_to_redshift([operation])
            perfomed_operations = True

            ExtractionOperation(
                conn=self.migrator_redshift_connector.target_conn
            ).update(
                url=operation.url,
                status=SAVED_REDSHIFT,
            )

            if load_option == FULL:
                ExtractionOperation(
                    conn=self.migrator_redshift_connector.target_conn
                ).mark_as_deleted_s3_old_full_operations(
                    struct=self.struct,
                    url=operation.url,
                )

        return perfomed_operations

    def extract_to_redshift(self, load_option=None):
        check_if_option_is_valid(load_option)
        self.__check_target_table_has_data()
        update_by_cdc = self.__check_table_will_be_updated_by_cdc(load_option)

        self.migrator_redshift_writer = writer_factory(
            env=self.env,
            update_by_cdc=update_by_cdc,
            struct=self.struct,
            migrator_redshift_connector=self.migrator_redshift_connector,
            logger=self.logger,
        )

        if update_by_cdc is True:
            perfomed_operations = self.__run_incremental_cdc_flow()
        else:
            perfomed_operations = self.__run_non_cdc_flow(load_option)

        if perfomed_operations is True:
            self.migrator_redshift_writer.clean_duplicate_inconsistencies()

        if update_by_cdc is False:
            self.__delete_test_tenant_rows()

        self.migrator_redshift_connector.close_target()


    def get_structs_source_to_target(self, database, tables="all"):
        structs = Struct(conn=self.migrator_redshift_connector.target_conn).get(
            database=database,
            tables=tables,
        )

        return structs
    
    def __delete_test_tenant_rows(self):
        cursor = self.migrator_redshift_connector.target_conn.cursor()
        cursor.execute(
            f"""
                CALL dataeng.delete_tenant_rows({TEST_TENANT}, '{self.struct.target_schema}', '{self.struct.target_table}');
            """
        )
        self.migrator_redshift_connector.target_conn.commit()
        cursor.close()

    def install_db_driver(self):
        if self.migrator_redshift_connector.source_conn_type == SQLSERVER and self.env != LOCAL:
            result = subprocess.run(['apt-get', 'update'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run(['apt-get', 'install', 'curl', '-y'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run(['apt-get', 'install', 'gnupg', '-y'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run('curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg', shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run('curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list', shell=True, capture_output=True, text=True)  
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run(['apt-get', 'update'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)

            env = os.environ.copy()
            env["ACCEPT_EULA"] = "Y"

            result = subprocess.run(["apt-get", "install", "unixodbc", "unixodbc-dev", "msodbcsql17", "-y"], capture_output=True, text=True, env=env)
            if result.returncode != 0:
                self.logger.error(f"Error installing packages: {result.stderr}")
            else:
                self.logger.info(f"Installing unixodbc-dev and msodbcsql17: {result.stdout}")

            result = subprocess.run(['apt-get', 'install', '-y', 'unixodbc-dev'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout)
            result = subprocess.run(['odbcinst', '-q', '-d', '-n', '"ODBC Driver 17 for SQL Server"'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info(result.stderr)
            else:
                self.logger.info(result.stdout) 