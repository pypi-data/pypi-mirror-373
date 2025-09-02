import os
from typing import Any

import amsdal_glue as glue
import amsdal_glue_connections.sql.connections.postgres_connection as glue_connections


class PostgresStateConnection(glue.PostgresConnection):

    def _default_envs(self) -> dict[str, Any]:
        envs = {}

        if os.getenv('POSTGRES_STATE_HOST'):
            envs['host'] = os.getenv('POSTGRES_STATE_HOST')

        if os.getenv('POSTGRES_STATE_PORT'):
            envs['port'] = os.getenv('POSTGRES_STATE_PORT')

        if os.getenv('POSTGRES_STATE_USER'):
            envs['user'] = os.getenv('POSTGRES_STATE_USER')

        if os.getenv('POSTGRES_STATE_PASSWORD'):
            envs['password'] = os.getenv('POSTGRES_STATE_PASSWORD')

        if os.getenv('POSTGRES_STATE_DATABASE'):
            envs['dbname'] = os.getenv('POSTGRES_STATE_DATABASE')

        return envs

    def connect(
        self,
        dsn: str = '',
        schema: str | None = None,
        timezone: str = 'UTC',
        *,
        autocommit: bool = True,
        **kwargs: Any,
    ) -> None:
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
        try:
            import psycopg
        except ImportError:
            _msg = (
                '"psycopg" package is required for PostgresConnection. '
                'Use "pip install amsdal-glue-connections[postgres]" to install it.'
            )
            raise ImportError(_msg) from None

        if self._connection is not None:
            msg = 'Connection already established'
            raise ConnectionError(msg)

        if not dsn:
            default_kwargs = self._default_envs()
            default_kwargs.update(kwargs)
            kwargs = default_kwargs

            self._connection = psycopg.connect(autocommit=autocommit, **kwargs)
        else:
            self._connection = psycopg.connect(dsn, autocommit=autocommit, **kwargs)

        self._connection.execute("SELECT set_config('TimeZone', %s, false)", [timezone])

        if schema:
            self._connection.execute(f'SET search_path TO {schema}')


class AsyncPostgresStateConnection(glue_connections.AsyncPostgresConnection):

    def _default_envs(self) -> dict[str, Any]:
        envs = {}

        if os.getenv('POSTGRES_STATE_HOST'):
            envs['host'] = os.getenv('POSTGRES_STATE_HOST')

        if os.getenv('POSTGRES_STATE_PORT'):
            envs['port'] = os.getenv('POSTGRES_STATE_PORT')

        if os.getenv('POSTGRES_STATE_USER'):
            envs['user'] = os.getenv('POSTGRES_STATE_USER')

        if os.getenv('POSTGRES_STATE_PASSWORD'):
            envs['password'] = os.getenv('POSTGRES_STATE_PASSWORD')

        if os.getenv('POSTGRES_STATE_DATABASE'):
            envs['dbname'] = os.getenv('POSTGRES_STATE_DATABASE')

        return envs

    async def connect(
        self,
        dsn: str = '',
        schema: str | None = None,
        timezone: str = 'UTC',
        *,
        autocommit: bool = True,
        **kwargs: Any,
    ) -> None:
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
        try:
            import psycopg
        except ImportError:
            _msg = (
                '"psycopg" package is required for PostgresConnection. '
                'Use "pip install amsdal-glue-connections[postgres]" to install it.'
            )
            raise ImportError(_msg) from None

        if self._connection is not None:
            msg = 'Connection already established'
            raise ConnectionError(msg)

        if not dsn:
            default_kwargs = self._default_envs()
            default_kwargs.update(kwargs)
            kwargs = default_kwargs

            self._connection = await psycopg.AsyncConnection.connect(autocommit=autocommit, **kwargs)
        else:
            self._connection = await psycopg.AsyncConnection.connect(dsn, autocommit=autocommit, **kwargs)

        await self._connection.execute("SELECT set_config('TimeZone', %s, false)", [timezone])

        if schema:
            await self._connection.execute(f'SET search_path TO {schema}')
