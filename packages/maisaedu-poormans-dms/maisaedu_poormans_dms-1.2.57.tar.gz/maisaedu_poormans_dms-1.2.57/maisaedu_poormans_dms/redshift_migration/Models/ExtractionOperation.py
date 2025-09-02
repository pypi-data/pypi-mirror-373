class ExtractionOperation:
    def __init__(
        self,
        target_schema=None,
        target_table=None,
        url=None,
        load_option=None,
        platform=None,
        status=None,
        received_at=None,
        created_at=None,
        updated_at=None,
    ):
        self.target_schema = target_schema
        self.target_table = target_table
        self.url = url
        self.load_option = load_option
        self.platform = platform
        self.status = status
        self.received_at = received_at
        self.created_at = created_at
        self.updated_at = updated_at