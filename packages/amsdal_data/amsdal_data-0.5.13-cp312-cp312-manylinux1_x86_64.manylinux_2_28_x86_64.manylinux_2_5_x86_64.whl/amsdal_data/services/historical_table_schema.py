from datetime import UTC
from datetime import datetime
from typing import Generic
from typing import TypeVar

import amsdal_glue as glue
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE
from amsdal_glue_core.common.interfaces.connection import AsyncConnectionBase
from amsdal_glue_core.common.interfaces.connection import ConnectionBase

from amsdal_data.connections.constants import SCHEMA_NAME_FIELD
from amsdal_data.connections.constants import SCHEMA_VERSION_FIELD
from amsdal_data.connections.constants import TABLE_SCHEMA
from amsdal_data.connections.constants import TABLE_SCHEMA__CREATED_AT
from amsdal_data.connections.constants import TABLE_SCHEMA__TABLE_NAME
from amsdal_data.connections.constants import TABLE_SCHEMA__TABLE_VERSION
from amsdal_data.connections.constants import TABLE_SCHEMA_TABLE

# Type variables for connection types
C = TypeVar('C', bound=ConnectionBase | AsyncConnectionBase)
R = TypeVar('R')
COMPATIBLE_CLASS_VERSIONS = 'compatible_class_versions'


class BaseHistoricalTableSchema(Generic[C, R]):
    """Base class for historical table schema operations.

    This class provides the common structure, constants, and query building logic for both
    synchronous and asynchronous implementations of the historical table schema operations.

    The class uses generic type parameters to handle different connection types:
    - C: The connection type (ConnectionBase for sync, AsyncConnectionBase for async)
    - R: The return type of query operations

    This design follows the DRY (Don't Repeat Yourself) principle by centralizing the common
    query building logic in the base class, while the derived classes implement the specific
    sync or async methods for executing these queries.
    """

    connection: C
    TABLE_SCHEMA_REFERENCE = glue.SchemaReference(
        name=TABLE_SCHEMA_TABLE,
        version='',
    )

    def _build_find_class_version_query(
        self,
        table_version: str,
        *,
        is_latest: bool = True,
    ) -> glue.QueryStatement:
        """Build a query to find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.
            is_latest: Whether to return the latest class version or all class versions.

        Returns:
            A query statement to find the class version.
        """
        query = glue.QueryStatement(
            table=self.TABLE_SCHEMA_REFERENCE,
            where=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=TABLE_SCHEMA__TABLE_VERSION),
                            table_name=TABLE_SCHEMA_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=table_version),
                ),
            ),
            order_by=[
                glue.OrderByQuery(
                    field=glue.FieldReference(
                        field=glue.Field(name=TABLE_SCHEMA__CREATED_AT),
                        table_name=TABLE_SCHEMA_TABLE,
                    ),
                    direction=glue.OrderDirection.DESC,
                ),
            ],
        )

        if is_latest:
            query.limit = glue.LimitQuery(limit=1)

        return query

    def _build_find_table_version_conditions(
        self,
        class_version: str | None = None,
        class_name: str | None = None,
        table_name: str | None = None,
        table_version: str | None = None,
    ) -> glue.Conditions:
        """Build conditions to find the table version for a given class version and table name.

        Args:
            class_version: Optional class version to find the table version for.
            class_name: Optional class name to filter by.
            table_name: Optional table name to filter by.
            table_version: Optional table version to filter by.

        Returns:
            Conditions to find the table version.
        """
        _conditions = []
        conditions_map = {
            SCHEMA_VERSION_FIELD: class_version,
            SCHEMA_NAME_FIELD: class_name,
            TABLE_SCHEMA__TABLE_NAME: table_name,
            TABLE_SCHEMA__TABLE_VERSION: table_version,
        }

        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=field_name),
                        table_name=TABLE_SCHEMA_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=value),
            )
            for field_name, value in conditions_map.items()
            if value is not None
        ]

        if not _conditions:
            msg = 'At least one of class_version, class_name, table_name, or table_version must be provided.'
            raise ValueError(msg)

        return glue.Conditions(*_conditions)

    def _build_query_table_schemas(self, filters: glue.Conditions | None) -> glue.QueryStatement:
        """Build a query to get table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A query statement to get table schemas.
        """
        return glue.QueryStatement(
            table=self.TABLE_SCHEMA_REFERENCE,
            where=filters,
        )

    def _build_schema_query(self) -> glue.Conditions:
        """Build conditions to query the schema table.

        Returns:
            Conditions to query the schema table.
        """
        return glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_NAME_FIELD),
                        table_name=SCHEMA_REGISTRY_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=TABLE_SCHEMA_TABLE),
            ),
        )

    def _build_table_schema_data(
        self,
        table_name: str,
        table_version: str,
        schema_name: str,
        schema_version: str,
    ) -> glue.Data:
        """Build data for a table schema.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.

        Returns:
            Data for a table schema.
        """
        return glue.Data(
            data={
                SCHEMA_NAME_FIELD: schema_name,
                SCHEMA_VERSION_FIELD: schema_version,
                TABLE_SCHEMA__TABLE_NAME: table_name,
                TABLE_SCHEMA__TABLE_VERSION: table_version,
                TABLE_SCHEMA__CREATED_AT: datetime.now(tz=UTC),
            },
        )

    def _build_class_version_exists_query(self, class_version: str) -> glue.Conditions:
        """Build conditions to check if a class version exists.

        Args:
            class_version: The class version to check.

        Returns:
            Conditions to check if a class version exists.
        """
        return glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_VERSION_FIELD),
                        table_name=TABLE_SCHEMA_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=class_version),
            ),
        )

    def _build_save_table_schema_mutation(self, data: glue.Data) -> list[glue.InsertData]:
        """Build a mutation to save a table schema.

        Args:
            data: The data to save.

        Returns:
            A list containing the insert mutation.
        """
        return [
            glue.InsertData(
                schema=self.TABLE_SCHEMA_REFERENCE,
                data=[data],
            ),
        ]


class HistoricalTableSchema(BaseHistoricalTableSchema[ConnectionBase, list[glue.Data]]):
    """Synchronous implementation of historical table schema operations."""

    connection: ConnectionBase

    def setup_for_connection(self, connection: glue.interfaces.ConnectionBase) -> None:
        self.connection = connection
        _schema = self.get_schema()

        if not _schema:
            self.create_schema_table()
            return

        _schema.version = ''

        if _schema != TABLE_SCHEMA:
            msg = 'Update SchemaTable is not supported yet.'
            raise NotImplementedError(msg)

    def find_class_version(self, table_version: str) -> str:
        """Find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The class version for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
        query = self._build_find_class_version_query(table_version)
        items = self.connection.query(query)

        if not items:
            msg = f'No schema found for version {table_version}.'
            raise ValueError(msg)

        return items[0].data[SCHEMA_VERSION_FIELD]

    def find_all_class_versions(self, table_version: str) -> list[str]:
        """Find the list of class versions for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The list of class versions for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
        query = self._build_find_class_version_query(table_version, is_latest=False)
        items = self.connection.query(query)

        if not items:
            msg = f'No schema found for version {table_version}.'
            raise ValueError(msg)

        return [item.data[SCHEMA_VERSION_FIELD] for item in items]

    def find_class_name(
        self,
        table_name: str,
        table_version: str | None = None,
        class_version: str | None = None,
    ) -> str:
        if not table_name:
            msg = 'Table name must be provided.'
            raise ValueError(msg)

        conditions = self._build_find_table_version_conditions(
            table_name=table_name,
            table_version=table_version,
            class_version=class_version,
        )
        items = self._query_table_schemas(filters=conditions)

        if not items:
            msg = f'No schema found for table {table_name}.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = f'Multiple schemas found for {table_name} with version {class_version}.'
            raise ValueError(msg)

        return items[0].data[SCHEMA_NAME_FIELD]

    def find_table_version(
        self,
        class_version: str,
        class_name: str | None = None,
        table_name: str | None = None,
    ) -> str:
        """Find the table version for a given class version and table name.

        Args:
            class_version: The class version to find the table version for.
            class_name: Optional class name to filter by.
            table_name: Optional table name to filter by.

        Returns:
            The table version for the given class version and table name.

        Raises:
            ValueError: If class_version is empty or if multiple schemas are found.
        """
        if not class_version:
            msg = 'Class version must be provided.'
            raise ValueError(msg)

        conditions = self._build_find_table_version_conditions(
            class_version=class_version,
            class_name=class_name,
            table_name=table_name,
        )
        items = self._query_table_schemas(filters=conditions)

        if not items:
            return ''

        if len(items) > 1:
            msg = f'Multiple schemas found for {table_name} with version {class_version}.'
            raise ValueError(msg)

        return items[0].data[TABLE_SCHEMA__TABLE_VERSION]

    def enrich_data_with_compatible_class_versions(
        self,
        table_name: str,
        items: list[glue.Data],
    ) -> list[glue.Data]:
        from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR

        table_name, _, table_version = table_name.rpartition(TABLE_NAME_VERSION_SEPARATOR)

        if not table_name:
            return items

        compatible_class_versions = self.find_all_class_versions(table_version)

        for item in items:
            metadata = item.metadata or {}
            metadata[COMPATIBLE_CLASS_VERSIONS] = compatible_class_versions
            item.metadata = metadata

        return items

    def register_table_schema_version(
        self,
        table_name: str,
        table_version: str,
        schema_name: str,
        schema_version: str,
    ) -> None:
        """Register a table schema version.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.
        """
        data = self._build_table_schema_data(
            table_name=table_name,
            table_version=table_version,
            schema_name=schema_name,
            schema_version=schema_version,
        )
        self._save_table_schema(data)

    def copy_table_schema_from_prior_class_version(
        self,
        prior_class_version: str,
        new_class_version: str,
    ) -> None:
        """Copy a table schema from a prior class version to a new one.

        Args:
            prior_class_version: The prior class version to copy from.
            new_class_version: The new class version to copy to.

        Raises:
            ValueError: If prior_class_version is empty, if no schema is found for prior_class_version,
                or if multiple schemas are found for prior_class_version.
        """
        if not prior_class_version:
            msg = 'Prior class version must be provided.'
            raise ValueError(msg)

        exists_new_version = self._query_table_schemas(
            filters=self._build_class_version_exists_query(new_class_version),
        )

        if exists_new_version:
            return

        items = self._query_table_schemas(
            filters=self._build_class_version_exists_query(prior_class_version),
        )

        if not items:
            msg = f'No schema found for version {prior_class_version}.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = f'Multiple schemas found for version {prior_class_version}.'
            raise ValueError(msg)

        data = items[0]
        data.data[SCHEMA_VERSION_FIELD] = new_class_version
        data.data[TABLE_SCHEMA__CREATED_AT] = datetime.now(tz=UTC)
        self._save_table_schema(data)

    def get_schema(self) -> glue.Schema | None:
        """Get the schema for the table schema table.

        Returns:
            The schema for the table schema table, or None if it doesn't exist.
        """
        _existing_schema = self.connection.query_schema(
            filters=self._build_schema_query(),
        )

        if _existing_schema:
            return _existing_schema[0]
        return None

    def create_schema_table(self) -> None:
        self.connection.run_schema_mutation(  # type: ignore[attr-defined]
            glue.RegisterSchema(
                schema=TABLE_SCHEMA,
            ),
        )

    def _get_table_schema(self, filters: glue.Conditions | None) -> glue.Data:
        items = self._query_table_schemas(filters)

        if not items:
            msg = 'No schema found.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = 'Multiple schemas found.'
            raise ValueError(msg)

        return items[0]

    def _query_table_schemas(self, filters: glue.Conditions | None) -> list[glue.Data]:
        """Query table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A list of table schemas matching the filters.
        """
        query = self._build_query_table_schemas(filters)
        items = self.connection.query(query)

        if not items:
            return []

        return items

    def _save_table_schema(self, data: glue.Data) -> None:
        """Save a table schema.

        Args:
            data: The data to save.
        """
        mutations = self._build_save_table_schema_mutation(data)
        self.connection.run_mutations(mutations)  # type: ignore[arg-type]


class AsyncHistoricalTableSchema(BaseHistoricalTableSchema[AsyncConnectionBase, list[glue.Data]]):
    """Asynchronous implementation of historical table schema operations."""

    connection: AsyncConnectionBase

    async def setup_for_connection(self, connection: AsyncConnectionBase) -> None:
        self.connection = connection
        _schema = await self.get_schema()

        if not _schema:
            await self.create_schema_table()
            return

        _schema.version = ''

        if _schema != TABLE_SCHEMA:
            msg = 'Update SchemaTable is not supported yet.'
            raise NotImplementedError(msg)

    async def find_class_version(self, table_version: str) -> str:
        """Find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The class version for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
        query = self._build_find_class_version_query(table_version)
        items = await self.connection.query(query)

        if not items:
            msg = f'No schema found for version {table_version}.'
            raise ValueError(msg)

        return items[0].data[SCHEMA_VERSION_FIELD]

    async def find_all_class_versions(self, table_version: str) -> list[str]:
        """Find the list of class versions for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The list of class versions for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
        query = self._build_find_class_version_query(table_version, is_latest=False)
        items = await self.connection.query(query)

        if not items:
            msg = f'No schema found for version {table_version}.'
            raise ValueError(msg)

        return [item.data[SCHEMA_VERSION_FIELD] for item in items]

    async def find_class_name(
        self,
        table_name: str,
        table_version: str | None = None,
        class_version: str | None = None,
    ) -> str:
        if not table_name:
            msg = 'Table name must be provided.'
            raise ValueError(msg)

        conditions = self._build_find_table_version_conditions(
            table_name=table_name,
            table_version=table_version,
            class_version=class_version,
        )
        items = await self._query_table_schemas(filters=conditions)

        if not items:
            msg = f'No schema found for table {table_name}.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = f'Multiple schemas found for {table_name} with version {class_version}.'
            raise ValueError(msg)

        return items[0].data[SCHEMA_NAME_FIELD]

    async def find_table_version(
        self,
        class_version: str,
        class_name: str | None = None,
        table_name: str | None = None,
    ) -> str:
        """Find the table version for a given class version and table name.

        Args:
            class_version: The class version to find the table version for.
            class_name: Optional class name to filter by.
            table_name: Optional table name to filter by.

        Returns:
            The table version for the given class version and table name.

        Raises:
            ValueError: If class_version is empty or if multiple schemas are found.
        """
        if not class_version:
            msg = 'Class version must be provided.'
            raise ValueError(msg)

        conditions = self._build_find_table_version_conditions(
            class_version=class_version,
            class_name=class_name,
            table_name=table_name,
        )
        items = await self._query_table_schemas(filters=conditions)

        if not items:
            return ''

        if len(items) > 1:
            msg = f'Multiple schemas found for {table_name} with version {class_version}.'
            raise ValueError(msg)

        return items[0].data[TABLE_SCHEMA__TABLE_VERSION]

    async def enrich_data_with_compatible_class_versions(
        self,
        table_name: str,
        items: list[glue.Data],
    ) -> list[glue.Data]:
        from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR

        table_name, _, table_version = table_name.rpartition(TABLE_NAME_VERSION_SEPARATOR)

        if not table_name:
            return items

        compatible_class_versions = await self.find_all_class_versions(table_version)

        for item in items:
            metadata = item.metadata or {}
            metadata[COMPATIBLE_CLASS_VERSIONS] = compatible_class_versions
            item.metadata = metadata

        return items

    async def register_table_schema_version(
        self,
        table_name: str,
        table_version: str,
        schema_name: str,
        schema_version: str,
    ) -> None:
        """Register a table schema version.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.
        """
        data = self._build_table_schema_data(
            table_name=table_name,
            table_version=table_version,
            schema_name=schema_name,
            schema_version=schema_version,
        )
        await self._save_table_schema(data)

    async def copy_table_schema_from_prior_class_version(
        self,
        prior_class_version: str,
        new_class_version: str,
    ) -> None:
        """Copy a table schema from a prior class version to a new one.

        Args:
            prior_class_version: The prior class version to copy from.
            new_class_version: The new class version to copy to.

        Raises:
            ValueError: If prior_class_version is empty, if no schema is found for prior_class_version,
                or if multiple schemas are found for prior_class_version.
        """
        if not prior_class_version:
            msg = 'Prior class version must be provided.'
            raise ValueError(msg)

        exists_new_version = await self._query_table_schemas(
            filters=self._build_class_version_exists_query(new_class_version),
        )

        if exists_new_version:
            return

        items = await self._query_table_schemas(
            filters=self._build_class_version_exists_query(prior_class_version),
        )

        if not items:
            msg = f'No schema found for version {prior_class_version}.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = f'Multiple schemas found for version {prior_class_version}.'
            raise ValueError(msg)

        data = items[0]
        data.data[SCHEMA_VERSION_FIELD] = new_class_version
        data.data[TABLE_SCHEMA__CREATED_AT] = datetime.now(tz=UTC)
        await self._save_table_schema(data)

    async def get_schema(self) -> glue.Schema | None:
        """Get the schema for the table schema table.

        Returns:
            The schema for the table schema table, or None if it doesn't exist.
        """
        _existing_schema = await self.connection.query_schema(
            filters=self._build_schema_query(),
        )

        if _existing_schema:
            return _existing_schema[0]
        return None

    async def create_schema_table(self) -> None:
        await self.connection.run_schema_mutation(  # type: ignore[attr-defined]
            glue.RegisterSchema(
                schema=TABLE_SCHEMA,
            ),
        )

    async def _get_table_schema(self, filters: glue.Conditions | None) -> glue.Data:
        items = await self._query_table_schemas(filters)

        if not items:
            msg = 'No schema found.'
            raise ValueError(msg)

        if len(items) > 1:
            msg = 'Multiple schemas found.'
            raise ValueError(msg)

        return items[0]

    async def _query_table_schemas(self, filters: glue.Conditions | None) -> list[glue.Data]:
        """Query table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A list of table schemas matching the filters.
        """
        query = self._build_query_table_schemas(filters)
        items = await self.connection.query(query)

        if not items:
            return []

        return items

    async def _save_table_schema(self, data: glue.Data) -> None:
        """Save a table schema.

        Args:
            data: The data to save.
        """
        mutations = self._build_save_table_schema_mutation(data)
        await self.connection.run_mutations(mutations)  # type: ignore[arg-type]
