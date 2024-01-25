from .base_connector import DatabaseConnector
from models.schemas import Table, TableColumn
from models.credentials import PostgresCredentials

class PostgresSQLConnector(DatabaseConnector):
    def __init__(self, credentials: PostgresCredentials):
        super().__init__(credentials)
        self.db_type = 'postgres'

    def connect(self):
        import psycopg2
        self.connection = psycopg2.connect(**self.credentials)

    @DatabaseConnector.with_connection
    def execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if query.lower().startswith("select"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
            
    @DatabaseConnector.with_connection
    def execute_select_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    
    @DatabaseConnector.with_connection
    def get_tables(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    
    @DatabaseConnector.with_connection
    def get_schema(self, table):
        column_query = f"""
            SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table}';
        """
        pk_query = f"""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = '{table}' AND tc.constraint_type = 'PRIMARY KEY';
        """
        fk_query = f"""
            SELECT kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = '{table}' AND tc.constraint_type = 'FOREIGN KEY';
        """

        with self.connection.cursor() as cursor:
            cursor.execute(column_query)
            columns_info = cursor.fetchall()

            cursor.execute(pk_query)
            pk_info = cursor.fetchall()

            cursor.execute(fk_query)
            fk_info = cursor.fetchall()

        # Process columns, primary keys, and foreign keys
        # Assuming you have defined the TableColumn and Table classes
        # Modify this part according to your Table and TableColumn class definitions
        columns = []
        for col, dtype, max_len, default, is_nullable in columns_info:
            col_obj = TableColumn(name=col, dtype=dtype, max_len=max_len, default=default, is_nullable=is_nullable)
            if col in (pk[0] for pk in pk_info):
                col_obj.is_primary = True
            for fk in fk_info:
                if col == fk[0]:
                    col_obj.is_foreign = True
                    col_obj.foreign_table = fk[1]
                    col_obj.foreign_column = fk[2]
            columns.append(col_obj)

        return Table(name=table, columns=columns)
