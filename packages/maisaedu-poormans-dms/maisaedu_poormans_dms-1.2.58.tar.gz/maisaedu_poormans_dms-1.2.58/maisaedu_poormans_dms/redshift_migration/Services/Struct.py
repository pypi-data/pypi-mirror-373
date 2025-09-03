from ..Models.Struct import Struct as StructModel


class Struct:
    def __init__(self, conn=None):
        self.conn = conn

    def get(self, database, tables="all"):
        cursor = self.conn.cursor()

        statement = f" and database = '{database}'"

        if tables != "all":
            statement = f"""
          {statement} and target_table in ({tables})
          """
        else:
            statement = f" {statement} and is_active is true"

        cursor.execute(
            f"""
              select 
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
                  is_active
              from 
                  dataeng.relations_extraction
              where
                  1=1 
                  {statement};
          """
        )

        structs = []

        relations_extraction = cursor.fetchall()
        for r in relations_extraction:
            struct_model = StructModel(
                id=r[0],
                source_schema=r[1],
                source_table=r[2],
                source_engine=r[3],
                target_schema=r[4],
                target_table=r[5],
                source_incremental_column=r[6],
                target_incremental_column=r[7],
                read_batch_size=r[8],
                incremental_interval_delta=r[9],
                database=r[10],
                extraction_engine=r[11],
                is_active=r[12],
            )
            cursor.execute(
                f"""
                    select 
                        source_name, 
                        target_name, 
                        source_type, 
                        target_type,
                        is_upsert,
                        is_active
                    from
                        dataeng.relations_columns_extraction
                    where
                        relation_id = {r[0]}
                    order by 
                        id;
              """
            )
            columns = cursor.fetchall()
            for c in columns:
                struct_model.add_column(
                    source_name=c[0],
                    target_name=c[1],
                    source_type=c[2],
                    target_type=c[3],
                    is_upsert=c[4],
                    is_active=c[5]
                )

            structs.append(struct_model)

        cursor.close()

        return structs
