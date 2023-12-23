from pydantic import BaseModel
from typing import Optional, List

class TableColumn(BaseModel):
    """Table column."""

    name: str
    dtype: str
    max_character_length: Optional[int] = None
    default_value: Optional[str] = None
    is_nullable: Optional[bool] = None
    is_primary: Optional[bool] = None
    is_foreign: Optional[bool] = None
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None

class ForeignKey(BaseModel):
    """Foreign key."""

    # Referenced column
    column: TableColumn
    # References table name
    references_name: str
    # References column
    references_column: TableColumn


class Table(BaseModel):
    """Table."""

    name: str
    columns: List[TableColumn]
    pks: Optional[list[TableColumn]] = None
    # FK from this table to another column in another table
    fks: Optional[list[ForeignKey]] = None

class SqlCoderFormatter:

    table_sep: str = "\n\n"

    def __init__(self, tables: list[Table]) -> None:
        self.tables = tables
        self.table_str = self.format_tables(tables)
    
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
        return self.table_sep.join(item for item in tables_fmt)


    def format_prompt(
        self,
        instruction: str,
        database: str = 'SQLite'
    ) -> str:
        """Get prompt format."""
        sql_prefix = "SELECT"
         
        prompt = """### Instructions:
Your task is convert a question into a SQL query, given a Postgres database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float

### Input:
Generate a SQL query that answers the questioq `{question}`.
This query will run on a database whose schema is represented in this string:
{table_str}

### Response:
Based on your instructions, here is the SQL query I have generated to answer the question `{question}`:
```sql
""".format(question=instruction, table_str = self.table_str)

        return prompt


class RajkumarFormatter:
    """RajkumarFormatter class.

    From https://arxiv.org/pdf/2204.00498.pdf.
    """

    table_sep: str = "\n\n"

    def __init__(self, tables: list[Table]) -> None:
        self.tables = tables
        self.table_str = self.format_tables(tables)

    def _format_table(self, table: Table) -> str:
        """Get table format."""
        table_fmt = []
        table_name = table.name
        for col in table.columns or []:
            # This is technically an incorrect type, but it should be a catchall word
            table_fmt.append(f"    {col.name} {col.dtype or 'any'}")
        if table.pks:
            table_fmt.append(
                f"    primary key ({', '.join(pk.name for pk in table.pks)})"
            )
        for fk in table.fks or []:
            table_fmt.append(
                f"    foreign key ({fk.column.name}) references {fk.references_name}({fk.references_column.name})"  # noqa: E501
            )
        if table_fmt:
            all_cols = ",\n".join(table_fmt)
            create_tbl = f"CREATE TABLE {table_name} (\n{all_cols}\n)"
        else:
            create_tbl = f"CREATE TABLE {table_name}"
        return create_tbl
    
    def format_table(self, table: Table) -> str:
        """Get table format."""
        table_fmt = []
        table_name = table.name
        for col in table.columns or []:
            # This is technically an incorrect type, but it should be a catchall word
            table_fmt.append(f"    {col.name} {col.dtype or 'any'} {' primary key' if col.is_primary else ''}")
        for col in table.columns or []:
            if col.is_foreign:
                table_fmt.append(
                    f"    foreign key ({col.name}) references {col.foreign_table}({col.foreign_column})"  # noqa: E501
                )
        if table_fmt:
            all_cols = ",\n".join(table_fmt)
            create_tbl = f"CREATE TABLE {table_name} (\n{all_cols}\n)"
        else:
            create_tbl = f"CREATE TABLE {table_name}"
        return create_tbl

    def format_tables(self, tables: list[Table]) -> str:
        """Get tables format."""
        return self.table_sep.join(self.format_table(table) for table in tables)

    def format_prompt(
        self,
        instruction: str,
        database: str = 'SQLite'
    ) -> str:
        """Get prompt format."""
        sql_prefix = "SELECT"
        return f"""{self.table_str}\n\n\n-- Using valid {database}, answer the following question for the tables provided above.\n\n-- {instruction}\n{sql_prefix}"""  # noqa: E501

    def format_model_output(self, output_sql: str) -> str:
        """Format model output.

        Our prompt ends with SELECT so we need to add it back.
        """
        if not output_sql.lower().startswith("select"):
            output_sql = "SELECT " + output_sql.strip()
        return output_sql
