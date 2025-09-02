import os
from copy import copy
from typing import Any

import amsdal_glue as glue
import amsdal_glue_connections.sql.connections.postgres_connection as glue_connections
from amsdal_glue_connections.sql.connections.postgres_connection import get_pg_transform
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE
from amsdal_glue_connections.sql.sql_builders.query_builder import build_from
from amsdal_glue_connections.sql.sql_builders.query_builder import build_where
from amsdal_glue_core.commands.lock_command_node import ExecutionLockCommand
from amsdal_glue_core.common.operations.mutations.data import DataMutation
from amsdal_utils.models.enums import Versions

from amsdal_data.connections.common import get_class_name
from amsdal_data.connections.common import get_table_version
from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import OBJECT_TABLE
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.constants import TABLE_SCHEMA_TABLE
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.data_mutation_transform import AsyncDataMutationTransform
from amsdal_data.connections.historical.data_mutation_transform import DataMutationTransform
from amsdal_data.connections.historical.data_mutation_transform.base import BaseDataMutationTransform
from amsdal_data.connections.historical.data_query_transform import PG_METADATA_SELECT_EXPRESSION
from amsdal_data.connections.historical.data_query_transform import DataQueryTransform
from amsdal_data.connections.historical.query_builder import pull_out_filter_from_query
from amsdal_data.connections.historical.query_builder import sort_items
from amsdal_data.connections.historical.query_builder import split_conditions
from amsdal_data.connections.historical.schema_command_transform import AsyncSchemaCommandExecutor
from amsdal_data.connections.historical.schema_command_transform import SchemaCommandExecutor
from amsdal_data.connections.historical.schema_query_filters_transform import AsyncSchemaQueryFiltersTransform
from amsdal_data.connections.historical.schema_query_filters_transform import SchemaQueryFiltersTransform
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_data.connections.historical.table_name_transform import AsyncTableNameTransform
from amsdal_data.connections.historical.table_name_transform import TableNameTransform
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema
from amsdal_data.services.historical_table_schema import HistoricalTableSchema


class _BasePostgresHistoricalConnection:
    TABLE_SQL = f"""
    SELECT
        {SCHEMA_REGISTRY_TABLE}.table_name AS table_name,
        {SCHEMA_REGISTRY_TABLE}.name AS name,
        {SCHEMA_REGISTRY_TABLE}.version AS version
    FROM (
        SELECT
            table_name,
            CASE WHEN position('{TABLE_NAME_VERSION_SEPARATOR}' in table_name) > 0
                 THEN substring(table_name from 1 for position('{TABLE_NAME_VERSION_SEPARATOR}' in table_name) - 1)
                 ELSE table_name
            END as name,
            CASE WHEN position('{TABLE_NAME_VERSION_SEPARATOR}' in table_name) > 0
                 THEN substring(table_name from position('{TABLE_NAME_VERSION_SEPARATOR}' in table_name) + 5)
                 ELSE ''
            END as version
        FROM information_schema.tables
        WHERE table_schema = 'public'
     ) AS {SCHEMA_REGISTRY_TABLE}
    """  # noqa: S608

    @staticmethod
    def _apply_pagination(items: list[glue.Data], limit: glue.LimitQuery | None) -> list[glue.Data]:
        if limit is None or not limit.limit:
            return items

        return items[slice(limit.offset, limit.offset + limit.limit)]

    def _transform_schema_to_historical(self, schema: glue.Schema) -> None:
        if schema.name in (
            TRANSACTION_TABLE,
            METADATA_TABLE,
            REFERENCE_TABLE,
        ):
            return

        if next((True for _property in schema.properties if _property.name == SECONDARY_PARTITION_KEY), False):
            return

        schema.properties.append(
            glue.PropertySchema(
                name=SECONDARY_PARTITION_KEY,
                type=str,
                required=True,
            ),
        )

        pk = glue.PrimaryKeyConstraint(
            name=f'pk_{schema.name.lower()}',
            fields=[PRIMARY_PARTITION_KEY, SECONDARY_PARTITION_KEY],
        )
        schema.constraints = [
            _constraint
            for _constraint in (schema.constraints or [])
            if not isinstance(_constraint, glue.PrimaryKeyConstraint)
        ]
        schema.constraints.append(pk)

    def _default_envs(self) -> dict[str, Any]:
        envs = {}

        if os.getenv('POSTGRES_HOST'):
            envs['host'] = os.getenv('POSTGRES_HOST')

        if os.getenv('POSTGRES_PORT'):
            envs['port'] = os.getenv('POSTGRES_PORT')

        if os.getenv('POSTGRES_USER'):
            envs['user'] = os.getenv('POSTGRES_USER')

        if os.getenv('POSTGRES_PASSWORD'):
            envs['password'] = os.getenv('POSTGRES_PASSWORD')

        if os.getenv('POSTGRES_DATABASE'):
            envs['dbname'] = os.getenv('POSTGRES_DATABASE')

        return envs


class PostgresHistoricalConnection(_BasePostgresHistoricalConnection, glue.PostgresConnection):
    def __init__(self) -> None:
        super().__init__()
        self.schema_version_manager = HistoricalSchemaVersionManager()
        self.table_schema = HistoricalTableSchema()

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

        self.table_schema.setup_for_connection(connection=self)

    def query(self, query: glue.QueryStatement) -> list[glue.Data]:
        _transform = DataQueryTransform(query)
        _query = _transform.transform(PG_METADATA_SELECT_EXPRESSION)

        _table_transform = TableNameTransform(_query, self.table_schema)

        if _table_transform.table_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            TABLE_SCHEMA_TABLE,
        ):
            return super().query(_table_transform.transform())

        items: list[glue.Data] = []
        queries = self._build_queries_by_version(_query)
        _processed_table_versions = set()

        for _query_version in queries:
            # Historical table name
            _table_transform = TableNameTransform(_query_version, self.table_schema)
            _query = _table_transform.transform()

            if _table_transform.table_name not in _processed_table_versions:
                _processed_table_versions.add(_table_transform.table_name)
                _items = super().query(_query)
                _items = self.table_schema.enrich_data_with_compatible_class_versions(
                    _table_transform.table_name,
                    _items,
                )
                items.extend(_items)

        if len(queries) > 1:
            items = sort_items(items, _query.order_by)
            items = self._apply_pagination(items, _query.limit)

        return items

    def query_schema(self, filters: glue.Conditions | None = None) -> list[glue.Schema]:
        _transform = SchemaQueryFiltersTransform(filters, historical_table_schema=self.table_schema)
        _conditions = _transform.transform()

        data = super().query_schema(_conditions)

        return _transform.process_data(data)

    def _run_mutation(self, mutation: DataMutation) -> list[glue.Data] | None:
        _transform = DataMutationTransform(self, mutation, historical_table_schema=self.table_schema)
        _mutations = _transform.transform()

        for _mutation in _mutations:
            super()._run_mutation(_mutation)

        return _transform.data

    def run_schema_command(self, command: glue.SchemaCommand) -> list[glue.Schema | None]:
        _executor = SchemaCommandExecutor(self, command, historical_table_schema=self.table_schema)

        return _executor.execute()

    def run_schema_mutation(self, mutation: glue.SchemaMutation) -> glue.Schema | None:
        return super()._run_schema_mutation(mutation)

    def _build_queries_by_version(self, query: glue.QueryStatement) -> list[glue.QueryStatement]:
        if not query.where:
            return self._to_queries_by_version(
                get_table_version(query.table),  # type: ignore[arg-type]
                query,
            )

        class_name = get_class_name(query.table)
        queries_by_version: dict[str, glue.QueryStatement] = {}
        field = glue.Field(name='_address', child=glue.Field(name='class_version'))
        field.child.parent = field  # type: ignore[union-attr]

        for _conditions in split_conditions(query.where):
            _class_versions, _query = pull_out_filter_from_query(_conditions, field)

            if not _class_versions:
                _class_versions = {query.table.version}  # type: ignore[union-attr]

            if _query is None:
                _query = ~glue.Conditions(
                    # TODO: It should use actual primary keys instead if PRIMARY_PARTITION_KEY
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                table_name=query.table.name,  # type: ignore[union-attr]
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value('_empty-'),
                    ),
                )

            for _class_version in _class_versions:
                if _class_version in (glue.Version.ALL, Versions.ALL):
                    _versions = set()
                    for _item_version in self.schema_version_manager.get_all_schema_versions(
                        class_name,
                    ):
                        if _item_version or query.table.name in {  # type: ignore[union-attr]
                            TRANSACTION_TABLE,
                            METADATA_TABLE,
                            REFERENCE_TABLE,
                            OBJECT_TABLE,
                        }:
                            _versions.add(_item_version)
                elif _class_version in (glue.Version.LATEST, Versions.LATEST):
                    _versions = {self.schema_version_manager.get_latest_schema_version(class_name)}
                else:
                    _versions = {_class_version}

                for _specific_current_version in _versions:
                    _query_version = copy(query)
                    _query_version.table = copy(query.table)
                    _query_version.table.version = _specific_current_version  # type: ignore[union-attr]
                    _query_version.where = _query

                    if _specific_current_version not in queries_by_version:
                        queries_by_version[_specific_current_version] = _query_version
                    else:
                        _q_version = queries_by_version[_specific_current_version]

                        if _q_version.where is not None:
                            _q_version.where |= _query

        return list(queries_by_version.values())

    def _to_queries_by_version(
        self,
        version: glue.Version | Versions,
        query: glue.QueryStatement,
    ) -> list[glue.QueryStatement]:
        queries = []

        _table = query.table
        _class_name = get_class_name(_table)

        if isinstance(_table, glue.SubQueryStatement):
            return [query]

        if version in (glue.Version.ALL, Versions.ALL):
            for _class_version in self.schema_version_manager.get_all_schema_versions(_class_name):
                _query = copy(query)
                _query.table = copy(_table)
                _query.table.version = _class_version
                queries.append(_query)
        elif version in (glue.Version.LATEST, Versions.LATEST):
            _latest_class_version = self.schema_version_manager.get_latest_schema_version(_class_name)
            _table.version = _latest_class_version
            queries.append(query)
        else:
            queries.append(query)

        return queries


class AsyncPostgresHistoricalConnection(_BasePostgresHistoricalConnection, glue_connections.AsyncPostgresConnection):
    def __init__(self) -> None:
        super().__init__()
        self.schema_version_manager = AsyncHistoricalSchemaVersionManager()
        self.table_schema = AsyncHistoricalTableSchema()

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

        await self.table_schema.setup_for_connection(connection=self)

    async def query(self, query: glue.QueryStatement) -> list[glue.Data]:
        _transform = DataQueryTransform(query)
        _query = _transform.transform(PG_METADATA_SELECT_EXPRESSION)

        _table_transform = AsyncTableNameTransform(_query, self.table_schema)

        if _table_transform.table_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            TABLE_SCHEMA_TABLE,
        ):
            return await super().query(await _table_transform.transform())

        items: list[glue.Data] = []
        queries = await self._build_queries_by_version(_query)
        _processed_table_versions = set()

        for _query_version in queries:
            # Historical table name
            _table_transform = AsyncTableNameTransform(_query_version, self.table_schema)
            _query = await _table_transform.transform()

            if _table_transform.table_name not in _processed_table_versions:
                _processed_table_versions.add(_table_transform.table_name)
                _items = await super().query(_query)
                _items = await self.table_schema.enrich_data_with_compatible_class_versions(
                    _table_transform.table_name,
                    _items,
                )
                items.extend(_items)

        if len(queries) > 1:
            items = sort_items(items, _query.order_by)
            items = self._apply_pagination(items, _query.limit)

        return items

    async def acquire_lock(self, lock: ExecutionLockCommand) -> bool:
        locked_object = copy(lock.locked_object)
        lock = copy(lock)
        lock.locked_object = locked_object
        query = glue.QueryStatement(
            table=copy(lock.locked_object.schema),
            where=copy(lock.locked_object.query),
        )

        query.where = BaseDataMutationTransform._process_foreign_keys_for_conditions(
            query.table.metadata,  # type: ignore[union-attr]
            query.where,
        )

        queries = await self._build_queries_by_version(query)

        for _query_version in queries:
            _table_transform = await AsyncTableNameTransform(_query_version, self.table_schema).transform()

            lock.locked_object.schema = _table_transform.table  # type: ignore[assignment]
            lock.locked_object.query = _table_transform.where

            if lock.locked_object.query:
                locked_object = lock.locked_object
                _stmt = 'SELECT * FROM '
                _from, _from_params = build_from(locked_object.schema, get_pg_transform())
                _where, _params = build_where(
                    locked_object.query,
                    transform=get_pg_transform(),
                )
                _stmt += _from
                if _where:
                    _stmt += f' WHERE {_where}'

                _stmt += ' FOR UPDATE'
                await self.execute(_stmt, *(*_from_params, *_params))

        return True

    async def query_schema(self, filters: glue.Conditions | None = None) -> list[glue.Schema]:
        _transform = AsyncSchemaQueryFiltersTransform(filters, historical_table_schema=self.table_schema)
        _conditions = await _transform.transform()

        data = await super().query_schema(_conditions)

        return await _transform.process_data(data)

    async def _run_mutation(self, mutation: DataMutation) -> list[glue.Data] | None:
        _transform = AsyncDataMutationTransform(self, mutation, historical_table_schema=self.table_schema)
        _mutations = await _transform.transform()

        for _mutation in _mutations:
            await super()._run_mutation(_mutation)

        return _transform.data

    async def run_schema_command(self, command: glue.SchemaCommand) -> list[glue.Schema | None]:
        _executor = AsyncSchemaCommandExecutor(self, command, historical_table_schema=self.table_schema)

        return await _executor.execute()

    async def run_schema_mutation(self, mutation: glue.SchemaMutation) -> glue.Schema | None:
        return await super()._run_schema_mutation(mutation)

    async def _build_queries_by_version(self, query: glue.QueryStatement) -> list[glue.QueryStatement]:
        if not query.where:
            return await self._to_queries_by_version(get_table_version(query.table), query)  # type: ignore[arg-type]

        class_name = get_class_name(query.table)
        queries_by_version: dict[str, glue.QueryStatement] = {}
        field = glue.Field(name='_address', child=glue.Field(name='class_version'))
        field.child.parent = field  # type: ignore[union-attr]

        for _conditions in split_conditions(query.where):
            _class_versions, _query = pull_out_filter_from_query(_conditions, field)

            if not _class_versions:
                _class_versions = {query.table.version}  # type: ignore[union-attr]

            if _query is None:
                _query = ~glue.Conditions(
                    # TODO: It should use actual primary keys instead if PRIMARY_PARTITION_KEY
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                table_name=query.table.name,  # type: ignore[union-attr]
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value('_empty-'),
                    ),
                )

            for _class_version in _class_versions:
                if _class_version in (glue.Version.ALL, Versions.ALL):
                    _versions = set()
                    for _item_version in await self.schema_version_manager.get_all_schema_versions(
                        class_name,
                    ):
                        if _item_version or query.table.name in {  # type: ignore[union-attr]
                            TRANSACTION_TABLE,
                            METADATA_TABLE,
                            REFERENCE_TABLE,
                            OBJECT_TABLE,
                        }:
                            _versions.add(_item_version)
                elif _class_version in (glue.Version.LATEST, Versions.LATEST):
                    _versions = {await self.schema_version_manager.get_latest_schema_version(class_name)}
                else:
                    _versions = {_class_version}

                for _specific_current_version in _versions:
                    _query_version = copy(query)
                    _query_version.table = copy(query.table)
                    _query_version.table.version = _specific_current_version  # type: ignore[union-attr]
                    _query_version.where = _query

                    if _specific_current_version not in queries_by_version:
                        queries_by_version[_specific_current_version] = _query_version
                    else:
                        _q_version = queries_by_version[_specific_current_version]

                        if _q_version.where is not None:
                            _q_version.where |= _query

        return list(queries_by_version.values())

    async def _to_queries_by_version(
        self,
        version: glue.Version | Versions,
        query: glue.QueryStatement,
    ) -> list[glue.QueryStatement]:
        queries = []

        _table = query.table
        _class_name = get_class_name(_table)

        if isinstance(_table, glue.SubQueryStatement):
            return [query]

        if version in (glue.Version.ALL, Versions.ALL):
            for _class_version in await self.schema_version_manager.get_all_schema_versions(_class_name):
                _query = copy(query)
                _query.table = copy(_table)
                _query.table.version = _class_version
                queries.append(_query)
        elif version in (glue.Version.LATEST, Versions.LATEST):
            _latest_class_version = await self.schema_version_manager.get_latest_schema_version(_class_name)
            _table.version = _latest_class_version
            queries.append(query)
        else:
            queries.append(query)

        return queries
