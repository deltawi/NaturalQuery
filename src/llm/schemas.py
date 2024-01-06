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