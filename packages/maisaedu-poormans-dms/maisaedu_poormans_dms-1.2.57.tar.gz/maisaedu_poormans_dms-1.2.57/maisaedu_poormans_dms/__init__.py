"""
A library for making database migration tasks. This library is intended to be used in situations
where AWS's DMS cannot be used, for any reason. 
"""

import aiopg
import psycopg2
import asyncio
import prefect

from aiopg import Pool
from aiochannel import Channel, ChannelClosed
from psycopg2.extensions import adapt
from dataclasses import dataclass
from typing import List, Callable, Dict, Any, Iterable, Iterator, Optional, Union
from enum import Enum

from maisaedu_poormans_dms.sql_server_migration import (
    build_create_query,
    get_table_info_query,
    extract_load_data,
    execute_sp,
    mark_tables_requiring_vacuum,
)


async def execute_once(pool: Pool, query: Union[str, bytes], args=()):
    """Executes a parametrized query in a pool once and streams the rows."""
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(query, args)

            async for row in cursor:
                yield row


async def execute_statement_once(pool: Pool, statement: Union[str, bytes]):
    """Executes a not parameterized statement in the pool once, expecting no results."""
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(statement)


def adapt_patched(thing: Any) -> bytes:
    """Transforms a thing into SQL code. This is a patch of `psycopg2.extensions.adapt`."""
    adaptor = adapt(thing)

    if hasattr(adaptor, "encoding"):
        adaptor.encoding = "utf8"

    return adaptor.getquoted()


def field_list(fields: Iterable[str]) -> str:
    """Gets a list of columns and joins them with commas in between."""
    return ", ".join(f'"{field}"' for field in fields)


def update_list(fields: Iterable[str]) -> str:
    """Renders the `DO UPDATE SET` clause of an `INSERT INTO` statement, setting all rows to be
    updated with new values."""
    return ", ".join(f'"{field}" = excluded."{field}"' for field in fields)


@dataclass
class Column(object):
    data_type: str
    is_not_null: bool
    character_maximum_length: int


def typed_field_list(fields: Dict[str, Column]):
    """Renders the field list of a `CREATE TABLE` statement."""
    return ", ".join(
        f'"{field}" {column.data_type}{"(" + str(column.character_maximum_length) + ")" if column.character_maximum_length else ""} {"not null" if column.is_not_null else ""} '
        for field, column in fields.items()
    )


IDENTITY = lambda x: x


class TaskStatus(Enum):
    OK = 1
    RETRY = 2
    ERROR = 3


class Migration(object):
    """
    Does the migration of a single table from one database to the other.

    Parameters:
        table_name: the name of the table to be migrated.
        batch_size (=1_000): the size of each migration batch.
        queue_max_size (=1_000): the size of the migration queue.
        schema (="public"): the schema of the table to be migrated.
        where (="true"): WHERE-clause to filter the rows to be migrated.
        period_column (=None): a column to be used as "time" in order to make incremental loads.
        primary_key (=None): PK column. As a fallback, load_table_info will use a query to
            retrieve the PK column.
        table_name_transform (=IDENTITY): a function transforming the name of the table in the
            source database to the name of the table in the target database.
        column_name_transform (=IDENTITY): a function transforming the name of each column in the
            source database to the name of each column in the target database.
        schema_name_transform (=IDENTITY): a function transforming the name of the schema in the
            source database to the name of the schema in the target database.
    """

    def __init__(
        self,
        table_name: str,
        batch_size: int = 1_000,
        queue_max_size: int = 1_000,
        *,
        schema: str = "public",
        where: str = "true",
        period_column: Optional[str] = None,
        primary_key: Optional[List[str]] = None,
        table_name_transform: Callable[[str], str] = IDENTITY,
        column_name_transform: Callable[[str], str] = IDENTITY,
        schema_name_transform: Callable[[str], str] = IDENTITY,
    ) -> None:
        # Schema in the source database
        self.schema = schema
        # Table name in the source database.
        self.table_name = table_name
        # Primary key in the source database (to be filled by `get_table_info`).
        self.primary_key: Optional[List[str]] = primary_key
        # Columns in the source database (to be filled by `get_table_info`).
        self.fields: Optional[Dict[str, Column]] = None
        # Period column (when table is append-only and is a timeseries).
        self.period_column: Optional[str] = period_column
        self.last_point: Optional[Any] = None
        # Schema in the destination database.
        self.dest_schema = schema_name_transform(schema)
        # Table name in the destination database.
        self.dest_table_name = table_name_transform(table_name)
        # Function transforming column names between source and destination databases.
        self.column_name_transform = column_name_transform
        # Columns in the destination database (to be filled by `get_table_info`).
        self.dest_fields: Optional[Dict[str, Column]] = None
        # Columns in the destinaton database (to be filled by `get_table_info`).
        self.dest_primary_key: Optional[List[str]] = None
        # Row filter in the source database.
        self.where = where
        # The size of the batch to be inserted in the target database.
        self.batch_size = batch_size
        # The queue that stores rows waiting to be written.
        self.channel: Channel = Channel(queue_max_size)

    async def load_table_info(self, pool: Pool) -> None:
        """Loads table info from the source database."""
        # The field `fields` marks whether this operation was run before.
        if self.fields is not None:
            return

        # Let's get all columns and info on each of them:
        columns = execute_once(
            pool,
            """
                select
                    column_name,
                    data_type,
                    case is_nullable
                        when 'NO' then true
                        when 'YES' then false
                    end as is_not_null,
                    character_maximum_length
                from
                    information_schema.columns
                where
                    table_schema = %s and table_name = %s
            """,
            (
                self.schema,
                self.table_name,
            ),
        )

        print(f'Loaded fields for "{self.table_name}"')

        fields = {
            column: Column(data_type, is_not_null, character_maximum_length)
            async for column, data_type, is_not_null, character_maximum_length in columns
        }

        if self.primary_key is None or len(self.primary_key) == 0:
            # Now, let's load the primary key:
            primary_key_columns = execute_once(
                pool,
                """
                    select
                        column_name
                    from
                        information_schema.table_constraints
                            join information_schema.key_column_usage
                                using (constraint_name, table_name, table_schema, constraint_schema)
                    where
                        constraint_type = 'PRIMARY KEY'
                            and table_schema = %s
                            and table_name = %s
                    order by
                        ordinal_position;

                """,
                (
                    self.schema,
                    self.table_name,
                ),
            )

            print(f'Loaded primary key for "{self.table_name}"')

            primary_key = [column async for column, in primary_key_columns]

            # If no primary key, complain:
            if len(primary_key) == 0:
                raise Exception("Table has no primary key", self.table_name)
            elif self.period_column is not None and self.period_column not in fields:
                raise Exception("Period column not a column", self.period_column)

            self.primary_key = primary_key

        self.fields = fields

        # Finally, transform names for the destination database:
        self.dest_fields = {
            self.column_name_transform(column_name): column
            for column_name, column in self.fields.items()
        }
        self.dest_primary_key = [
            self.column_name_transform(column) for column in self.primary_key
        ]

    async def load_last_point(self, pool: Pool) -> None:
        """
        Loads the last point where the migration ended, according to this `Migration`'s
        `period_column`. This method raises an assertion error if `period_column` is not set.
        """
        assert self.period_column is not None

        row = execute_once(
            pool,
            f"""
                select
                    max("{self.column_name_transform(self.period_column)}")
                from
                    "{self.dest_schema}"."{self.table_name}"
            """,
        )

        row = [row async for row in row]

        self.last_point = row[0][0]

    async def create_table(self, pool: Pool, drop_if_exists=False) -> None:
        """Creates the table in the destination database, if it not exists."""
        assert self.dest_fields is not None
        assert self.dest_primary_key is not None

        # # Create schema if not exists
        # try:
        #     await execute_statement_once(
        #         pool, f'create schema if not exists "{self.dest_schema}"'
        #     )
        # except psycopg2.errors.UniqueViolation as _:
        #     # Looks like a Postgres bug, of all the things...
        #     pass

        create_query = f"""
            create table if not exists "{self.dest_schema}"."{self.dest_table_name}" (
                {typed_field_list(self.dest_fields)},
                primary key ({field_list(self.dest_primary_key)})
            )
        """
        print(f'Created replicated table for "{self.table_name}"')

        await execute_statement_once(pool, create_query)

    async def drop_table_if_exists(self, pool: Pool) -> None:
        """Drops the table in the destination database, if it exists."""
        drop_query = (
            f'drop table if exists "{self.dest_schema}"."{self.dest_table_name}"'
        )
        await execute_statement_once(pool, drop_query)
        prefect.context.get("logger").info(
            f'Dropped replicated table for "{self.table_name}"'
        )

    async def source(self, pool: Pool) -> TaskStatus:
        """The task responsible for getting rows from the source database."""
        assert self.fields is not None
        assert self.primary_key is not None

        if self.last_point is not None:
            period_clause = f"""
                "{self.period_column}" >= {adapt_patched(self.last_point).decode("utf8")}
            """
        else:
            period_clause = "true"

        source_query = f"""
            select
                {field_list(self.fields.keys())}
            from
                "{self.schema}"."{self.table_name}"
            where
                {period_clause} and {self.where}
            -- order by {field_list(self.primary_key)}
        """

        print(f'Starting streaming rows for "{self.table_name}"')

        try:
            async for row in execute_once(pool, source_query):
                await self.channel.put(row)

            await self.channel.put(None)
            print(f'Finished streaming rows for "{self.table_name}"')
        except psycopg2.Error as e:
            print(f'FAILED streaming rows for "{self.table_name}": \n{e.pgerror}')
            return TaskStatus.ERROR
        except ChannelClosed:
            print(f'Sink for "{self.table_name}" closed')

        return TaskStatus.OK

    async def sink(self, pool: Pool) -> None:
        """The task responsible for putting rows in the destination database."""
        assert self.dest_fields is not None
        assert self.dest_primary_key is not None

        sink_query_header = f"""
            insert into
                "{self.dest_schema}"."{self.dest_table_name}" (
                    {field_list(self.dest_fields.keys())}
                )
            values
        """.encode(
            "utf8"
        )
        sink_query_footer = f"""
            on conflict ({field_list(self.dest_primary_key)}) do update set
                {update_list(self.dest_fields.keys())}
        """.encode(
            "utf8"
        )

        def format_values(values: Iterable[bytes]) -> bytes:
            return b"(" + b", ".join(adapt_patched(value) for value in values) + b")"

        def format_batch(batch: Iterable[Iterable[bytes]]) -> bytes:
            values_clause = b", ".join(format_values(values) for values in batch)
            return sink_query_header + values_clause + sink_query_footer

        batch = []
        row = await self.channel.get()

        print(f'Started writting rows for "{self.table_name}"')

        try:
            while row is not None:
                batch.append(row)

                if len(batch) == self.batch_size:
                    await execute_statement_once(pool, format_batch(batch))
                    batch = []

                row = await self.channel.get()

            await execute_statement_once(pool, format_batch(batch))
            print(f'Finished writting rows for "{self.table_name}"')
        except psycopg2.errors.UndefinedColumn:
            print("Looks like schema has changed! Let's drop and try again!")
            await self.drop_table_if_exists(pool)
            return TaskStatus.RETRY
        except psycopg2.Error as e:
            print(f'FAILED writting rows for "{self.table_name}": \n{e.pgerror}')
            return TaskStatus.ERROR
        finally:
            self.channel.close()

        return TaskStatus.OK

    async def startup(self, from_pool: Pool, to_pool: Pool) -> None:
        """Does migration setup"""
        await self.load_table_info(from_pool)

        if self.period_column is not None:
            await self.load_last_point(to_pool)

        await self.create_table(to_pool)

    async def migrate(self, from_pool: Pool, to_pool: Pool) -> bool:
        """Runs migration _after_ setup."""
        source_status, sink_status = await asyncio.gather(
            self.source(from_pool), self.sink(to_pool)
        )

        if source_status == TaskStatus.ERROR or sink_status == TaskStatus.ERROR:
            print(f'Migrate task for "{self.table_name}" failed')
            return False
        elif source_status == TaskStatus.RETRY or source_status == TaskStatus.RETRY:
            await self.startup(from_pool, to_pool)
            return await self.migrate(from_pool, to_pool)
        else:
            return True


class Migrator(object):
    """Manages the overall migrations from a source database to a destination database."""

    def __init__(self, from_connect_str: str, to_connect_str: str) -> None:
        self.from_connect_str = from_connect_str
        self.to_connect_str = to_connect_str

    async def migrate(self, migrations: List[Migration]) -> List[bool]:
        """Runs a list of migrations."""
        print(f"Creating source pool")
        from_pool = await aiopg.create_pool(self.from_connect_str)
        print(f"Creating destination pool")
        to_pool = await aiopg.create_pool(self.to_connect_str)

        print("Starting migrations up")
        await asyncio.gather(
            *[migration.startup(from_pool, to_pool) for migration in migrations]
        )

        print("Running migrations...")
        return await asyncio.gather(
            *[migration.migrate(from_pool, to_pool) for migration in migrations]
        )
