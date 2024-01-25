from .postgres_connector import PostgresSQLConnector
from .sqlite_connector import SQLiteConnector
from .sqlserver_connector import SqlServerConnector
from .base_connector import DatabaseConnector

# Factory class
class ConnectorFactory:
    @staticmethod
    def get_connector(db_type, credentials):
        connectors = {
            'postgres': PostgresSQLConnector,
            'sqlite': SQLiteConnector,
            'sqlserver': SqlServerConnector
        }
        connector_class = connectors.get(db_type, DatabaseConnector)
        return connector_class(credentials)
