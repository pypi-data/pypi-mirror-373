class Struct:
    def __init__(
        self,
        id,
        source_schema,
        source_table,
        source_engine,
        target_schema,
        target_table,
        source_incremental_column,
        target_incremental_column,
        read_batch_size,
        incremental_interval_delta,
        database,
        extraction_engine,
        is_active,
    ):
        self.id = id
        self.source_schema = source_schema
        self.source_table = source_table
        self.source_engine = source_engine
        self.target_schema = target_schema
        self.target_table = target_table
        self.source_incremental_column = source_incremental_column
        self.target_incremental_column = target_incremental_column
        self.read_batch_size = read_batch_size
        self.incremental_interval_delta = incremental_interval_delta
        self.database = database
        self.extraction_engine = extraction_engine
        self.is_active = is_active
        self.columns = []
        self.columns_upsert = []

    def add_column(
        self,
        source_name,
        target_name,
        source_type,
        target_type,
        is_upsert,
        is_active
    ):
        self.columns.append(
            {
                "source_name": source_name,
                "target_name": target_name,
                "source_type": source_type,
                "target_type": target_type,
                "is_active": is_active
            }
        )

        if is_upsert is True:
            self.columns_upsert.append(source_name)
