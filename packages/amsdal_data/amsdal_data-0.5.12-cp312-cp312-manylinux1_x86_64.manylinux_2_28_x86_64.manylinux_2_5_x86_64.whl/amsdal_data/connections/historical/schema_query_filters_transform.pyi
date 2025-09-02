import amsdal_glue as glue
from _typeshed import Incomplete
from amsdal_data.connections.constants import SCHEMA_TABLE_NAME_FIELD as SCHEMA_TABLE_NAME_FIELD, SCHEMA_VERSION_FIELD as SCHEMA_VERSION_FIELD
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR as TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager as AsyncHistoricalSchemaVersionManager, HistoricalSchemaVersionManager as HistoricalSchemaVersionManager
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema as AsyncHistoricalTableSchema, HistoricalTableSchema as HistoricalTableSchema

class BaseQueryFiltersTransform:
    schema_query_filters: Incomplete
    def __init__(self, schema_query_filters: glue.Conditions | None) -> None: ...

class SchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    schema_version_manager: Incomplete
    historical_table_schema: Incomplete
    def __init__(self, schema_query_filters: glue.Conditions | None, historical_table_schema: HistoricalTableSchema) -> None: ...
    def transform(self) -> glue.Conditions | None: ...
    def process_data(self, data: list[glue.Schema]) -> list[glue.Schema]:
        """
        We need to extract table version from the full table name and translate it to the class version.
        """
    def _transform(self, item: glue.Conditions) -> glue.Conditions:
        """
        AMSDAL operates always with class versions, but in Lakehouse we have table_version.
        So we need to replace class version with table version in the query.
        Also, we need to replace table name with full table name in the query, e.g. users__v__LATEST to
        specific version.
        """
    def _replace_class_version(self, condition: glue.Condition) -> glue.Condition: ...
    def _normalize_full_table_name(self, condition: glue.Condition) -> glue.Condition: ...

class AsyncSchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    schema_version_manager: Incomplete
    historical_table_schema: Incomplete
    def __init__(self, schema_query_filters: glue.Conditions | None, historical_table_schema: AsyncHistoricalTableSchema) -> None: ...
    async def transform(self) -> glue.Conditions | None: ...
    async def process_data(self, data: list[glue.Schema]) -> list[glue.Schema]:
        """
        We need to extract table version from the full table name and translate it to the class version.
        """
    async def _transform(self, item: glue.Conditions) -> glue.Conditions:
        """
        AMSDAL operates always with class versions, but in Lakehouse we have table_version.
        So we need to replace class version with table version in the query.
        Also, we need to replace table name with full table name in the query, e.g. users__v__LATEST to
        specific version.
        """
    async def _replace_class_version(self, condition: glue.Condition) -> glue.Condition: ...
    async def _normalize_full_table_name(self, condition: glue.Condition) -> glue.Condition: ...
