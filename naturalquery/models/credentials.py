from pydantic import BaseModel, Field, FilePath

class PostgresCredentials(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int = Field(default=5432, gt=0, lt=65536)

class SQLiteCredentials(BaseModel):
    database: FilePath

class SQLServerCredentials(BaseModel):
    driver: str
    server: str
    database: str
    username: str
    password: str