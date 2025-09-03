from maisaedu_poormans_dms.redshift_migration.Types import (
    FULL,
    check_if_env_is_valid,
    check_if_option_is_valid
)

from .Writer.WriterFull import WriterFull
from .Writer.WriterCDC import WriterCDC
from .Connector import Connector

class DynamoReplicator:
    def __init__(
        self,
        env=None,
        struct=None,
        logger=None
    ):
        check_if_env_is_valid(env)

        self.conn = Connector(env)
        self.env = env
        self.struct = struct
        self.logger = logger

    def __connect(self):
        if self.conn.redshift is None:
            self.conn.connect()
    
    def __run_full_flow(self, struct):
        writer = WriterFull(
            env=self.env,
            conn=self.conn,
            logger=self.logger,
            struct=struct
        )
        writer.save()

    def __run_incremental_flow(self, struct):
        writer = WriterCDC(
            env=self.env,
            conn=self.conn,
            logger=self.logger,
            struct=struct
        )
        writer.save()

    def process_records(self, load_option, struct):
        if struct is None:
            raise ValueError("struct must be provided")
        
        self.__connect()
        check_if_option_is_valid(load_option)

        self.logger.info(f"Processing records for {struct}")
        if load_option == FULL:
            self.__run_full_flow(struct)
        else:
            self.__run_incremental_flow(struct)

        self.conn.redshift.commit()

    def __del__(self):
        self.conn.close()