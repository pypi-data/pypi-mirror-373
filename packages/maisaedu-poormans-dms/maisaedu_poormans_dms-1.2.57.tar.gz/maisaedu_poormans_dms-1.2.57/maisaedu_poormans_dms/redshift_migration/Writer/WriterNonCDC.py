from ..Types import FULL
from .GenericWriter import GenericWriter
from ..Contracts.WriterInterface import WriterInterface


class WriterNonCDC(GenericWriter, WriterInterface):
    def delete_on_tmp_s3(self, url):
        bucket = url.split("/")[2]
        path_file = "/".join(url.split("/")[3:-1])

        bucket_client = self.migrator_redshift_connector.s3_session.Bucket(bucket)
        bucket_client.objects.filter(Prefix=f"{path_file}").delete()

    def save_data(self, operations):
        operation = operations[0]
        url = operation.url.replace("prefect", "tmp")
        url = url.replace(".parquet", ".csv")
        load_option = operation.load_option

        try:
            self.create_table_temp_target_relation()
            self.copy_data_to_target(url, self.temp_target_relation)

            self.migrator_redshift_connector.target_conn.autocommit = False

            if self.is_upsert is True and load_option != FULL:
                self.delete_using_temp_target_from_target()
            else:
                self.delete_all_data_from_target()

            self.insert_data_from_temp_to_target()

            self.migrator_redshift_connector.target_conn.commit()
            self.migrator_redshift_connector.target_conn.autocommit = True

            self.drop_table_temp_target_relation()

            self.delete_on_tmp_s3(url)
        except Exception as e:
            self.delete_on_tmp_s3(url)
            raise e
