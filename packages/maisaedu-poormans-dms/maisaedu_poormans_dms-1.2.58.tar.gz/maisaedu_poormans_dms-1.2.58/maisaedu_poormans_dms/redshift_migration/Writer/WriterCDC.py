import io
import pandas as pd
from datetime import datetime
from .GenericWriter import GenericWriter
from ..Contracts.WriterInterface import WriterInterface
from ..Services.AdapterSourceTarget import AdapterSourceTarget


class WriterCDC(GenericWriter, WriterInterface):
    def get_op_rows(self, df, op="I"):
        df = df[df["Op"] == op]
        df = df.drop(columns=["Op"])
        return df

    def save_data_on_tmp_s3(self, bucket, df, path_file, file_name):
        def save_data_on_tmp(op, df, path_file):
            df = self.get_op_rows(df, op=op)
            adapter = AdapterSourceTarget(self.struct)
            df = adapter.convert_types(df)
            df = adapter.order_by_cdc(op, df)
            df = adapter.transform_data(df)
            df = adapter.equalize_number_columns(df)

            if df.empty is False:
                if op == "U":
                    df = df.drop_duplicates(subset=self.struct.columns_upsert, keep="last")

                buffer = io.BytesIO()
                df.to_csv(buffer, index=False)
                self.migrator_redshift_connector.s3_session.Object(
                    bucket,
                    path_file,
                ).put(Body=buffer.getvalue())
                buffer.close()

        save_data_on_tmp("I", df, f"{path_file}/insert/{file_name}")
        save_data_on_tmp("U", df, f"{path_file}/update/{file_name}")
        save_data_on_tmp("D", df, f"{path_file}/delete/{file_name}")

    def check_s3_path_exists(self, bucket, key):
        if bucket is None:
            return False

        bucket_client = self.migrator_redshift_connector.s3_session.Bucket(bucket)
        for object_summary in bucket_client.objects.filter(Prefix=key):
            return True
        return False

    def delete_from_redshift(self, path_file, bucket):
        if self.check_s3_path_exists(bucket, path_file) is True:
            self.create_table_temp_target_relation()
            self.copy_data_to_target(
                f"s3://{bucket}/{path_file}", self.temp_target_relation
            )

            self.delete_using_temp_target_from_target()

            self.drop_table_temp_target_relation()

    def save_to_redshift_from_s3(self, path_file, bucket):
        if self.check_s3_path_exists(bucket, path_file) is True:
            self.create_table_temp_target_relation()
            self.copy_data_to_target(
                f"s3://{bucket}/{path_file}", self.temp_target_relation
            )

            self.migrator_redshift_connector.target_conn.autocommit = False

            self.delete_using_temp_target_from_target()
            self.insert_data_from_temp_to_target()

            self.migrator_redshift_connector.target_conn.commit()
            self.migrator_redshift_connector.target_conn.autocommit = True

            self.drop_table_temp_target_relation()

    def delete_on_tmp_s3(self, bucket, path_file):
        if self.check_s3_path_exists(bucket, path_file) is True:
            bucket_client = self.migrator_redshift_connector.s3_session.Bucket(bucket)
            bucket_client.objects.filter(Prefix=f"{path_file}/insert/").delete()
            bucket_client.objects.filter(Prefix=f"{path_file}/update/").delete()
            bucket_client.objects.filter(Prefix=f"{path_file}/delete/").delete()

    def save_data(self, operations):
        self.migrator_redshift_connector.connect_s3()
        time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        path_file = f"raw/tmp/{self.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}"
        bucket = None

        main_df = pd.DataFrame()

        urls = [operation.url for operation in operations]

        try:
            for operation in operations:
                url = operation.url

                splitted_url = url.split("/")
                bucket = splitted_url[2]
                key = "/".join(splitted_url[3:])

                obj = self.migrator_redshift_connector.s3_session.Object(bucket, key)
                file_content = obj.get()["Body"].read()

                df = pd.read_parquet(io.BytesIO(file_content))

                self.logger.info(
                    f"""
                        Saving data on redshift
                        Operation url: {url}
                        df bytes size: {df.memory_usage(deep=True).sum()}
                    """
                )

                main_df = pd.concat([main_df, df], ignore_index=True)

                self.logger.info(
                    f"""
                        Saving data on redshift
                        main_df bytes size: {main_df.memory_usage(deep=True).sum()}
                    """
                )

            self.save_data_on_tmp_s3(bucket, main_df, path_file, "tmp.csv")

            self.save_to_redshift_from_s3(f"{path_file}/insert/", bucket)
            self.save_to_redshift_from_s3(f"{path_file}/update/", bucket)
            self.delete_from_redshift(f"{path_file}/delete/", bucket)

            self.delete_on_tmp_s3(bucket, path_file)

        except Exception as e:
            self.delete_on_tmp_s3(bucket, path_file)
            raise Exception(
                f"""
                    Error on save data on redshift 
                    Cause of error: {e}
                    Operations urls: {urls}
                    You can download/check the file on s3, if the error was not direct in redshift
                """
            )
