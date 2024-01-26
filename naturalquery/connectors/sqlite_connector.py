from ..models.schemas import Table, TableColumn
from ..models.credentials import SQLiteCredentials
from .base_connector import DatabaseConnector

class SQLiteConnector(DatabaseConnector):
    def __init__(self, credentials: SQLiteCredentials):
        super().__init__(credentials)
        self.db_type = 'SQLite'

    def connect(self):
        import sqlite3
        self.connection = sqlite3.connect(self.credentials['database'])

    @DatabaseConnector.with_connection
    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        if query.lower().startswith("select"):
            return cursor.fetchall()
        else:
            self.connection.commit()
            return cursor.rowcount

    @DatabaseConnector.with_connection
    def execute_select_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    @DatabaseConnector.with_connection
    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    
    @DatabaseConnector.with_connection
    def get_schema(self, table):
        cursor = self.connection.cursor()

        # Get column information
        cursor.execute(f"PRAGMA table_info({table});")
        columns_info = cursor.fetchall()

        # Process columns
        columns = []
        for col_info in columns_info:
            col_id, col_name, col_type, col_notnull, col_default, col_pk = col_info
            col_obj = TableColumn(name=col_name, dtype=col_type, is_nullable=(col_notnull == 0), default_value=col_default, is_primary=(col_pk != 0))
            columns.append(col_obj)

        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fk_info = cursor.fetchall()

        for fk in fk_info:
            id_, seq, table, from_, to_, on_update, on_delete, match = fk
            for col in columns:
                if col.name == from_:
                    col.is_foreign = True
                    col.foreign_table = table
                    col.foreign_column = to_

        return Table(name=table, columns=columns)
