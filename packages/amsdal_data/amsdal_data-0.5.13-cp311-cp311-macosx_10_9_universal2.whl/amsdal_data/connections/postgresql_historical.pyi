import amsdal_glue as glue
import amsdal_glue_connections.sql.connections.postgres_connection as glue_connections
from _typeshed import Incomplete
from amsdal_data.connections.common import get_class_name as get_class_name, get_table_version as get_table_version
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE, OBJECT_TABLE as OBJECT_TABLE, PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY, REFERENCE_TABLE as REFERENCE_TABLE, SECONDARY_PARTITION_KEY as SECONDARY_PARTITION_KEY, TABLE_SCHEMA_TABLE as TABLE_SCHEMA_TABLE, TRANSACTION_TABLE as TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR as TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.data_mutation_transform import AsyncDataMutationTransform as AsyncDataMutationTransform, DataMutationTransform as DataMutationTransform
from amsdal_data.connections.historical.data_mutation_transform.base import BaseDataMutationTransform as BaseDataMutationTransform
from amsdal_data.connections.historical.data_query_transform import DataQueryTransform as DataQueryTransform, PG_METADATA_SELECT_EXPRESSION as PG_METADATA_SELECT_EXPRESSION
from amsdal_data.connections.historical.query_builder import pull_out_filter_from_query as pull_out_filter_from_query, sort_items as sort_items, split_conditions as split_conditions
from amsdal_data.connections.historical.schema_command_transform import AsyncSchemaCommandExecutor as AsyncSchemaCommandExecutor, SchemaCommandExecutor as SchemaCommandExecutor
from amsdal_data.connections.historical.schema_query_filters_transform import AsyncSchemaQueryFiltersTransform as AsyncSchemaQueryFiltersTransform, SchemaQueryFiltersTransform as SchemaQueryFiltersTransform
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager as AsyncHistoricalSchemaVersionManager, HistoricalSchemaVersionManager as HistoricalSchemaVersionManager
from amsdal_data.connections.historical.table_name_transform import AsyncTableNameTransform as AsyncTableNameTransform, TableNameTransform as TableNameTransform
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema as AsyncHistoricalTableSchema, HistoricalTableSchema as HistoricalTableSchema
from amsdal_glue_core.commands.lock_command_node import ExecutionLockCommand as ExecutionLockCommand
from amsdal_glue_core.common.operations.mutations.data import DataMutation as DataMutation
from amsdal_utils.models.enums import Versions
from typing import Any

class _BasePostgresHistoricalConnection:
    TABLE_SQL: Incomplete
    @staticmethod
    def _apply_pagination(items: list[glue.Data], limit: glue.LimitQuery | None) -> list[glue.Data]: ...
    def _transform_schema_to_historical(self, schema: glue.Schema) -> None: ...
    def _default_envs(self) -> dict[str, Any]: ...

class PostgresHistoricalConnection(_BasePostgresHistoricalConnection, glue.PostgresConnection):
    schema_version_manager: Incomplete
    table_schema: Incomplete
    def __init__(self) -> None: ...
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
    def query(self, query: glue.QueryStatement) -> list[glue.Data]: ...
    def query_schema(self, filters: glue.Conditions | None = None) -> list[glue.Schema]: ...
    def _run_mutation(self, mutation: DataMutation) -> list[glue.Data] | None: ...
    def run_schema_command(self, command: glue.SchemaCommand) -> list[glue.Schema | None]: ...
    def run_schema_mutation(self, mutation: glue.SchemaMutation) -> glue.Schema | None: ...
    def _build_queries_by_version(self, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...
    def _to_queries_by_version(self, version: glue.Version | Versions, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...

class AsyncPostgresHistoricalConnection(_BasePostgresHistoricalConnection, glue_connections.AsyncPostgresConnection):
    schema_version_manager: Incomplete
    table_schema: Incomplete
    def __init__(self) -> None: ...
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
    async def query(self, query: glue.QueryStatement) -> list[glue.Data]: ...
    async def acquire_lock(self, lock: ExecutionLockCommand) -> bool: ...
    async def query_schema(self, filters: glue.Conditions | None = None) -> list[glue.Schema]: ...
    async def _run_mutation(self, mutation: DataMutation) -> list[glue.Data] | None: ...
    async def run_schema_command(self, command: glue.SchemaCommand) -> list[glue.Schema | None]: ...
    async def run_schema_mutation(self, mutation: glue.SchemaMutation) -> glue.Schema | None: ...
    async def _build_queries_by_version(self, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...
    async def _to_queries_by_version(self, version: glue.Version | Versions, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...
