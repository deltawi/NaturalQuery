from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Generator, List
import pandas as pd
import sqlalchemy

from .prompt_formatters import TableColumn, Table


@dataclass
class PostgresConnector:
    """Postgres connection."""

    user: str
    password: str
    dbname: str
    host: str
    port: int

    @cached_property
    def pg_uri(self) -> str:
        """Get Postgres URI."""
        uri = (
            f"postgresql://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        )
        # ensure we can actually connect to this postgres uri
        engine = sqlalchemy.create_engine(uri)
        conn = engine.connect()

        # assuming the above connection is successful, we can now close the connection
        conn.close()
        engine.dispose()

        return uri

    @contextmanager
    def connect(self) -> Generator[sqlalchemy.engine.base.Connection, None, None]:
        """Yield a connection to a Postgres db.

        Example:
        .. code-block:: python
            postgres = PostgresConnector(
                user=USER, password=PASSWORD, dbname=DBNAME, host=HOST, port=PORT
            )
            with postgres.connect() as conn:
                conn.execute(sql)
        """
        try:
            engine = sqlalchemy.create_engine(self.pg_uri)
            conn = engine.connect()
            yield conn
        finally:
            conn.close()
            engine.dispose()

    def run_sql_as_df(self, sql: str) -> pd.DataFrame:
        """Run SQL statement."""
        import sqlalchemy

        try:
            with self.connect() as conn:
                return pd.read_sql_query(sql, conn)
        except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
            # Extracting just the error message
            return 'Error occured while executing a query {}'.format(e.args)

    def get_tables(self) -> List[str]:
        """Get all tables in the database."""
        engine = sqlalchemy.create_engine(self.pg_uri)
        table_names = engine.table_names()
        engine.dispose()
        return table_names

    def _get_schema(self, table: str) -> Table:
        """Return Table."""
        with self.connect() as conn:
            columns = []
            sql = f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}';
            """
            schema = conn.execute(sql).fetchall()
            for col, type_ in schema:
                columns.append(TableColumn(name=str(col), dtype=str(type_)))
            return Table(name=table, columns=columns)
        


    def get_schema(self, table: str) -> Table:
        """Return Table with primary and foreign key information."""
        with self.connect() as conn:
            # Fetch columns and their data types
            column_sql = f"""
                SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table}';
            """
            columns_info = conn.execute(column_sql).fetchall()
            columns = [TableColumn(name=str(col), dtype=str(type_), max_character_length=max_char_len, is_nullable=is_null, default_value=col_default) 
                       for col, type_, max_char_len, col_default, is_null in columns_info]

            # Fetch primary key information
            pk_sql = f"""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = '{table}' AND tc.constraint_type = 'PRIMARY KEY';
            """
            pk_info = conn.execute(pk_sql).fetchall()
            primary_keys = [col[0] for col in pk_info]
            for col in columns:
                if col.name in primary_keys:
                    col.is_primary = True

            # Fetch foreign key information
            fk_sql = f"""
                SELECT kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = '{table}' AND tc.constraint_type = 'FOREIGN KEY';
            """
            fk_info = conn.execute(fk_sql).fetchall()
            foreign_keys = []
            for col_name, foreign_table, foreign_column in fk_info:
                foreign_keys.append((col_name, foreign_table, foreign_column))
                for col in columns:
                    if col.name == col_name:
                        col.is_foreign = True
                        col.foreign_table = foreign_table
                        col.foreign_column = foreign_column
            return Table(name=table, 
                         columns=columns)


@dataclass
class SQLiteConnector:
    """SQLite connection."""

    database_path: str

    @cached_property
    def sqlite_uri(self) -> str:
        """Get SQLite URI."""
        uri = f"sqlite:///{self.database_path}"
        # ensure we can actually connect to this SQLite uri
        engine = sqlalchemy.create_engine(uri)
        conn = engine.connect()

        # assuming the above connection is successful, we can now close the connection
        conn.close()
        engine.dispose()

        return uri

    @contextmanager
    def connect(self) -> Generator[sqlalchemy.engine.base.Connection, None, None]:
        """Yield a connection to a SQLite database.

        Example:
        .. code-block:: python
            sqlite = SQLiteConnector(database_path=DB_PATH)
            with sqlite.connect() as conn:
                conn.execute(sql)
        """
        try:
            engine = sqlalchemy.create_engine(self.sqlite_uri)
            conn = engine.connect()
            yield conn
        finally:
            conn.close()
            engine.dispose()

    def get_tables(self) -> List[str]:
        """Get all tables in the database."""
        engine = sqlalchemy.create_engine(self.sqlite_uri)
        table_names = engine.table_names()
        engine.dispose()
        return table_names

    def run_sql_as_df(self, sql: str) -> pd.DataFrame:
        """Run SQL statement."""
        with self.connect() as conn:
            return pd.read_sql(sql, conn)

    def get_schema(self, table: str) -> Table:
        """Return Table."""
        with self.connect() as conn:
            columns = []
            sql = f"PRAGMA table_info({table});"
            schema = conn.execute(sql).fetchall()
            for row in schema:
                col = row[1]
                type_ = row[2]
                columns.append(TableColumn(name=col, dtype=type_))
            return Table(name=table, columns=columns)
