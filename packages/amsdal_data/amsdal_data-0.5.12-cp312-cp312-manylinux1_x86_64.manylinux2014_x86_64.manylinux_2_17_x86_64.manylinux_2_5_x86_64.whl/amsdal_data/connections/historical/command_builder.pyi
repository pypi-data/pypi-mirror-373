import amsdal_glue as glue
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE, OBJECT_TABLE as OBJECT_TABLE, REFERENCE_TABLE as REFERENCE_TABLE, TABLE_SCHEMA_TABLE as TABLE_SCHEMA_TABLE, TRANSACTION_TABLE as TRANSACTION_TABLE
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager as AsyncHistoricalSchemaVersionManager, HistoricalSchemaVersionManager as HistoricalSchemaVersionManager
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema as AsyncHistoricalTableSchema, HistoricalTableSchema as HistoricalTableSchema

TABLE_NAME_VERSION_SEPARATOR: str

def build_historical_table_name(schema_reference: glue.SchemaReference, table_schema: HistoricalTableSchema) -> str: ...
async def async_build_historical_table_name(schema_reference: glue.SchemaReference, table_schema: AsyncHistoricalTableSchema) -> str: ...
def format_historical_table_name(name: str, version: str) -> str: ...
