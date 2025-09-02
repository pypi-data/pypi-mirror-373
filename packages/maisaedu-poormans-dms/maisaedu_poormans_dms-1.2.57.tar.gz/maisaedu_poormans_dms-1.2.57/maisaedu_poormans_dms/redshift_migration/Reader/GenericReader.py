import io
import threading
import pandas as pd
from datetime import datetime
from ..Types import (
    target_type_is_numeric,
    LOCAL,
    FULL,
    PROD,
    INCREMENTAL,
    SAVED_S3,
    PREFECT,
    S3,
)
from ..Services.ExtractionOperation import ExtractionOperation
from ..Services.AdapterSourceTarget import AdapterSourceTarget
from ..Models.ExtractionOperation import ExtractionOperation as ExtractionOperationModel


class GenericReader:
    def __init__(self, s3_credentials, struct, migrator_redshift_connector):
        self.struct = struct
        self.s3_credentials = s3_credentials
        self.migrator_redshift_connector = migrator_redshift_connector

    def __save_on_bucket(self, df, path_file, format="parquet"):
        buffer = io.BytesIO()

        if format == "csv":
            df.to_csv(buffer, index=False)
        else:
            df.to_parquet(buffer, index=False, engine="pyarrow")
        self.migrator_redshift_connector.s3_session.Object(
            self.s3_credentials["bucket"],
            path_file,
        ).put(Body=buffer.getvalue())

        buffer.close()

    def __process_chunk(self, chunk_df, path_file, path_file_tmp):
        adapter = AdapterSourceTarget(self.struct)
        chunk_df_s3 = chunk_df.copy()

        chunk_df_s3 = adapter.transform_data(chunk_df_s3, target_save=S3)

        self.__save_on_bucket(chunk_df_s3, path_file)

        chunk_df = adapter.convert_types(chunk_df)
        chunk_df = adapter.transform_data(chunk_df)
        chunk_df = adapter.equalize_number_columns(chunk_df)

        self.__save_on_bucket(chunk_df, path_file_tmp, format="csv")

    def save_data_to_s3(self, load_option=None):
        self.load_option = load_option
        self.migrator_redshift_connector.connect_s3()
        self.migrator_redshift_connector.connect_source()

        sql = self.get_sql_statement()

        time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        idx = 1
        path_file = None
        threads = []

        for chunk_df in pd.read_sql(
            sql,
            self.migrator_redshift_connector.source_conn,
            chunksize=self.struct.read_batch_size,
        ):
            if len(chunk_df) != 0:
                path_file = f"raw/prefect/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/{idx}.parquet"
                path_file_tmp = f"raw/tmp/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/{idx}.csv"
                
                thread = threading.Thread(target=self.__process_chunk, args=(chunk_df, path_file, path_file_tmp))
                thread.start()
                threads.append(thread)
                
                idx = idx + 1
        
        for thread in threads:
            thread.join()

        self.migrator_redshift_connector.close_source()

        if path_file is None:
            return None
        else:
            url = f's3://{self.s3_credentials["bucket"]}/raw/prefect/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/'

            ExtractionOperation(
                conn=self.migrator_redshift_connector.target_conn,
            ).create(
                struct=self.struct,
                url=url,
                load_option=self.load_option,
                status=SAVED_S3,
                platform=self.struct.extraction_engine,
            )

            return ExtractionOperationModel(
                url=url,
                load_option=self.load_option,
            )
