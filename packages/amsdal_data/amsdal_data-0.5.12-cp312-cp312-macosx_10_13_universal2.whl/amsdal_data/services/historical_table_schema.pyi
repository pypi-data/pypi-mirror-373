import amsdal_glue as glue
from _typeshed import Incomplete
from amsdal_data.connections.constants import SCHEMA_NAME_FIELD as SCHEMA_NAME_FIELD, SCHEMA_VERSION_FIELD as SCHEMA_VERSION_FIELD, TABLE_SCHEMA as TABLE_SCHEMA, TABLE_SCHEMA_TABLE as TABLE_SCHEMA_TABLE, TABLE_SCHEMA__CREATED_AT as TABLE_SCHEMA__CREATED_AT, TABLE_SCHEMA__TABLE_NAME as TABLE_SCHEMA__TABLE_NAME, TABLE_SCHEMA__TABLE_VERSION as TABLE_SCHEMA__TABLE_VERSION
from amsdal_glue_core.common.interfaces.connection import AsyncConnectionBase, ConnectionBase
from typing import Generic, TypeVar

C = TypeVar('C', bound=ConnectionBase | AsyncConnectionBase)
R = TypeVar('R')
COMPATIBLE_CLASS_VERSIONS: str

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
    TABLE_SCHEMA_REFERENCE: Incomplete
    def _build_find_class_version_query(self, table_version: str, *, is_latest: bool = True) -> glue.QueryStatement:
        """Build a query to find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.
            is_latest: Whether to return the latest class version or all class versions.

        Returns:
            A query statement to find the class version.
        """
    def _build_find_table_version_conditions(self, class_version: str | None = None, class_name: str | None = None, table_name: str | None = None, table_version: str | None = None) -> glue.Conditions:
        """Build conditions to find the table version for a given class version and table name.

        Args:
            class_version: Optional class version to find the table version for.
            class_name: Optional class name to filter by.
            table_name: Optional table name to filter by.
            table_version: Optional table version to filter by.

        Returns:
            Conditions to find the table version.
        """
    def _build_query_table_schemas(self, filters: glue.Conditions | None) -> glue.QueryStatement:
        """Build a query to get table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A query statement to get table schemas.
        """
    def _build_schema_query(self) -> glue.Conditions:
        """Build conditions to query the schema table.

        Returns:
            Conditions to query the schema table.
        """
    def _build_table_schema_data(self, table_name: str, table_version: str, schema_name: str, schema_version: str) -> glue.Data:
        """Build data for a table schema.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.

        Returns:
            Data for a table schema.
        """
    def _build_class_version_exists_query(self, class_version: str) -> glue.Conditions:
        """Build conditions to check if a class version exists.

        Args:
            class_version: The class version to check.

        Returns:
            Conditions to check if a class version exists.
        """
    def _build_save_table_schema_mutation(self, data: glue.Data) -> list[glue.InsertData]:
        """Build a mutation to save a table schema.

        Args:
            data: The data to save.

        Returns:
            A list containing the insert mutation.
        """

class HistoricalTableSchema(BaseHistoricalTableSchema[ConnectionBase, list[glue.Data]]):
    """Synchronous implementation of historical table schema operations."""
    connection: ConnectionBase
    def setup_for_connection(self, connection: glue.interfaces.ConnectionBase) -> None: ...
    def find_class_version(self, table_version: str) -> str:
        """Find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The class version for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
    def find_all_class_versions(self, table_version: str) -> list[str]:
        """Find the list of class versions for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The list of class versions for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
    def find_class_name(self, table_name: str, table_version: str | None = None, class_version: str | None = None) -> str: ...
    def find_table_version(self, class_version: str, class_name: str | None = None, table_name: str | None = None) -> str:
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
    def enrich_data_with_compatible_class_versions(self, table_name: str, items: list[glue.Data]) -> list[glue.Data]: ...
    def register_table_schema_version(self, table_name: str, table_version: str, schema_name: str, schema_version: str) -> None:
        """Register a table schema version.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.
        """
    def copy_table_schema_from_prior_class_version(self, prior_class_version: str, new_class_version: str) -> None:
        """Copy a table schema from a prior class version to a new one.

        Args:
            prior_class_version: The prior class version to copy from.
            new_class_version: The new class version to copy to.

        Raises:
            ValueError: If prior_class_version is empty, if no schema is found for prior_class_version,
                or if multiple schemas are found for prior_class_version.
        """
    def get_schema(self) -> glue.Schema | None:
        """Get the schema for the table schema table.

        Returns:
            The schema for the table schema table, or None if it doesn't exist.
        """
    def create_schema_table(self) -> None: ...
    def _get_table_schema(self, filters: glue.Conditions | None) -> glue.Data: ...
    def _query_table_schemas(self, filters: glue.Conditions | None) -> list[glue.Data]:
        """Query table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A list of table schemas matching the filters.
        """
    def _save_table_schema(self, data: glue.Data) -> None:
        """Save a table schema.

        Args:
            data: The data to save.
        """

class AsyncHistoricalTableSchema(BaseHistoricalTableSchema[AsyncConnectionBase, list[glue.Data]]):
    """Asynchronous implementation of historical table schema operations."""
    connection: AsyncConnectionBase
    async def setup_for_connection(self, connection: AsyncConnectionBase) -> None: ...
    async def find_class_version(self, table_version: str) -> str:
        """Find the class version for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The class version for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
    async def find_all_class_versions(self, table_version: str) -> list[str]:
        """Find the list of class versions for a given table version.

        Args:
            table_version: The table version to find the class version for.

        Returns:
            The list of class versions for the given table version.

        Raises:
            ValueError: If no schema is found for the given table version.
        """
    async def find_class_name(self, table_name: str, table_version: str | None = None, class_version: str | None = None) -> str: ...
    async def find_table_version(self, class_version: str, class_name: str | None = None, table_name: str | None = None) -> str:
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
    async def enrich_data_with_compatible_class_versions(self, table_name: str, items: list[glue.Data]) -> list[glue.Data]: ...
    async def register_table_schema_version(self, table_name: str, table_version: str, schema_name: str, schema_version: str) -> None:
        """Register a table schema version.

        Args:
            table_name: The name of the table.
            table_version: The version of the table.
            schema_name: The name of the schema.
            schema_version: The version of the schema.
        """
    async def copy_table_schema_from_prior_class_version(self, prior_class_version: str, new_class_version: str) -> None:
        """Copy a table schema from a prior class version to a new one.

        Args:
            prior_class_version: The prior class version to copy from.
            new_class_version: The new class version to copy to.

        Raises:
            ValueError: If prior_class_version is empty, if no schema is found for prior_class_version,
                or if multiple schemas are found for prior_class_version.
        """
    async def get_schema(self) -> glue.Schema | None:
        """Get the schema for the table schema table.

        Returns:
            The schema for the table schema table, or None if it doesn't exist.
        """
    async def create_schema_table(self) -> None: ...
    async def _get_table_schema(self, filters: glue.Conditions | None) -> glue.Data: ...
    async def _query_table_schemas(self, filters: glue.Conditions | None) -> list[glue.Data]:
        """Query table schemas with the given filters.

        Args:
            filters: Conditions to filter the table schemas.

        Returns:
            A list of table schemas matching the filters.
        """
    async def _save_table_schema(self, data: glue.Data) -> None:
        """Save a table schema.

        Args:
            data: The data to save.
        """
