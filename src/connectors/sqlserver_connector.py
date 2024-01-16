
from base_connector import DatabaseConnector
from models.schemas import Table, TableColumn
from models.credentials import SQLServerCredentials

class SqlServerConnector(DatabaseConnector):
    def __init__(self, credentials: SQLServerCredentials):
        super().__init__(credentials)
        self.db_type = 'SQLServer'

    def connect(self):
        import pyodbc
        conn_str = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(
            self.credentials['driver'],
            self.credentials['server'],
            self.credentials['database'],
            self.credentials['username'],
            self.credentials['password']
        )
        self.connection = pyodbc.connect(conn_str)

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        if query.lower().startswith("select"):
            return cursor.fetchall()
        else:
            self.connection.commit()
            return cursor.rowcount

    def execute_select_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    
    def get_tables(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    
    def get_schema(self, table):
        cursor = self.connection.cursor()

        # Get column information
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, COLUMN_DEFAULT, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table}'
        """)
        columns_info = cursor.fetchall()

        # Process columns
        columns = []
        for col_name, data_type, char_max_length, col_default, is_nullable in columns_info:
            col_obj = TableColumn(name=col_name, dtype=data_type, max_len=char_max_length, default_value=col_default, is_nullable=is_nullable == 'YES')
            columns.append(col_obj)

        # Get primary key information
        cursor.execute(f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME), 'IsPrimaryKey') = 1
            AND TABLE_NAME = '{table}'
        """)
        pk_info = cursor.fetchall()
        primary_keys = [row[0] for row in pk_info]

        # Mark primary key columns
        for col in columns:
            if col.name in primary_keys:
                col.is_primary = True

        # Get foreign key information
        cursor.execute(f"""
            SELECT
                fk.name AS FK_name,
                tp.name AS parent_table,
                cp.name AS parent_column,
                tr.name AS referenced_table,
                cr.name AS referenced_column
            FROM 
                sys.foreign_keys AS fk
            INNER JOIN 
                sys.tables AS tp ON fk.parent_object_id = tp.object_id
            INNER JOIN 
                sys.tables AS tr ON fk.referenced_object_id = tr.object_id
            INNER JOIN 
                sys.foreign_key_columns AS fkc ON fkc.constraint_object_id = fk.object_id
            INNER JOIN 
                sys.columns AS cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
            INNER JOIN 
                sys.columns AS cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
            WHERE 
                tp.name = '{table}'
        """)
        fk_info = cursor.fetchall()

        # Mark foreign key columns
        for fk in fk_info:
            for col in columns:
                if col.name == fk[2]:  # parent_column
                    col.is_foreign = True
                    col.foreign_table = fk[3]  # referenced_table
                    col.foreign_column = fk[4]  # referenced_column

        return Table(name=table, columns=columns)