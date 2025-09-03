import amsdal_glue as glue
import amsdal_glue_connections.sql.connections.postgres_connection as glue_connections
from _typeshed import Incomplete
from typing import Any

class PostgresStateConnection(glue.PostgresConnection):
    def _default_envs(self) -> dict[str, Any]: ...
    _connection: Incomplete
    def connect(self, dsn: str = '', schema: str | None = None, timezone: str = 'UTC', *, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Establishes a connection to the PostgreSQL database.

        Args:
            dsn (str): The Data Source Name for the connection.
            schema (str | None): The default schema to be used for the connection. If None,
                                 the default schema usually is 'public'.
            timezone (str): The timezone to be used for the connection.
            autocommit (bool): Whether to enable autocommit mode.
            **kwargs: Additional connection parameters.

        Raises:
            ConnectionError: If the connection is already established.
            ImportError: If the 'psycopg' package is not installed.
        """

class AsyncPostgresStateConnection(glue_connections.AsyncPostgresConnection):
    def _default_envs(self) -> dict[str, Any]: ...
    _connection: Incomplete
    async def connect(self, dsn: str = '', schema: str | None = None, timezone: str = 'UTC', *, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Establishes a connection to the PostgreSQL database.

        Args:
            dsn (str): The Data Source Name for the connection.
            schema (str | None): The default schema to be used for the connection. If None,
                                 the default schema usually is 'public'.
            timezone (str): The timezone to be used for the connection.
            autocommit (bool): Whether to enable autocommit mode.
            **kwargs: Additional connection parameters.

        Raises:
            ConnectionError: If the connection is already established.
            ImportError: If the 'psycopg' package is not installed.
        """
