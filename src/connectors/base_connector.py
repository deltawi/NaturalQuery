from abc import ABC, abstractmethod
from typing import List
from models.schemas import Table

class DatabaseConnector(ABC):
    def __init__(self, credentials):
        self.credentials = credentials
        self.connection = None
        self.db_type = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

    @abstractmethod
    def get_schema(self, table):
        pass
    
    @abstractmethod
    def execute_select_query(self, query):
        pass

    @abstractmethod
    def get_tables(self):
        pass
    
    def query_to_dataframe(self, query):
        import pandas as pd
        return pd.read_sql(query, self.connection)

    def get_all_schemas_ddl(self):
        tables = self.get_tables()
        all_tables = [self.get_schema(table) for table in tables]
        return self.format_tables(all_tables)
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
    
    def map_data_type(self, data_type, character_maximum_length, default):
        """Map general data types to SQL data types."""
        if data_type == 'character varying':
            return f'VARCHAR({character_maximum_length})' if character_maximum_length else 'VARCHAR'
        elif data_type == 'timestamp without time zone':
            return 'TIMESTAMP'
        elif default and default.startswith('nextval'):
            data_type = 'SERIAL'  # or 'AUTO_INCREMENT' for MySQL
        # Add more mappings as needed
        return data_type
    
    def format_tables(self, tables: List[Table]) -> str:
        """
        Generates SQL statements to recreate a list of tables.

        This function takes a list of Table objects, each containing information about
        a database table (such as column definitions, primary key, and foreign key info),
        and formats them into CREATE TABLE SQL statements.

        Args:
            tables: A list of Table objects representing the database tables.

        Returns:
            A string containing the CREATE TABLE SQL statements for each table in the list,
            separated by a specified separator. Foreign key relationships are listed as comments.
        """
        tables_fmt = []  # List to store the formatted CREATE TABLE statements
        list_fks = []  # List to store comments about foreign keys
        table_sep = "\n\n"

        for table in tables:
            table_fmt = []  # List to store individual column definitions for the current table
            for col in table.columns or []:
                # Map the data type of the column to its SQL equivalent
                mapped_dtype = self.map_data_type(col.dtype, col.max_character_length, col.default_value)
                column_def = f"{col.name} {mapped_dtype}"
                
                # Append default value and NOT NULL constraint if applicable
                if col.default_value is not None and not col.default_value.startswith('nextval'):
                    column_def += f" DEFAULT {col.default_value}"
                if col.is_nullable == 'NO':
                    column_def += " NOT NULL"

                # Mark column as PRIMARY KEY if it is a primary key
                if col.is_primary:
                    column_def += " PRIMARY KEY"

                table_fmt.append(column_def)

                # Record foreign key relationships as comments for later addition
                if col.is_foreign:
                    list_fks.append(f"-- {table.name}.{col.name} can be joined with {col.foreign_table}.{col.foreign_column}")

            # Construct the CREATE TABLE statement
            if table_fmt:
                all_cols = ",\n".join(table_fmt)
                create_tbl = f"CREATE TABLE {table.name} (\n{all_cols}\n)"
            else:
                create_tbl = f"CREATE TABLE {table.name}"

            tables_fmt.append(create_tbl)

        # Combine all CREATE TABLE statements and foreign key comments
        tables_fmt.append("\n".join(fk for fk in list_fks))
        return table_sep.join(item for item in tables_fmt)