class RelationExtraction:
    def __init__(self, conn=None):
        self.conn = conn

    def set_is_active(self, struct, is_active):
        cursor = self.conn.cursor()

        sql = f"""
            update dataeng.relations_extraction
            set is_active = {is_active}
            where id = {struct.id}
        """

        cursor.execute(sql)
        cursor.close()
