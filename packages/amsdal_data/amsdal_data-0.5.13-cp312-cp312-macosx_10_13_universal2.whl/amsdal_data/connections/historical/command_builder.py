import amsdal_glue as glue
from amsdal_utils.models.enums import Versions

from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import OBJECT_TABLE
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import TABLE_SCHEMA_TABLE
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema
from amsdal_data.services.historical_table_schema import HistoricalTableSchema

TABLE_NAME_VERSION_SEPARATOR = '__v__'


def build_historical_table_name(
    schema_reference: glue.SchemaReference,
    table_schema: HistoricalTableSchema,
) -> str:
    if schema_reference.name in (
        TRANSACTION_TABLE,
        METADATA_TABLE,
        REFERENCE_TABLE,
        OBJECT_TABLE,
        TABLE_SCHEMA_TABLE,
    ):
        return schema_reference.name

    # Table name already transformed to historical
    if TABLE_NAME_VERSION_SEPARATOR in schema_reference.name:
        return schema_reference.name

    class_version_manager = HistoricalSchemaVersionManager()
    _version = schema_reference.version

    if _version in (glue.Version.LATEST, Versions.LATEST):
        _version = class_version_manager.get_latest_schema_version(schema_reference.name)

    if _version in (glue.Version.LATEST, Versions.LATEST) or not _version:
        # Still latest version means that there is no historical table
        return schema_reference.name

    table_version = table_schema.find_table_version(
        class_version=_version,
        table_name=schema_reference.name,
    )

    return format_historical_table_name(schema_reference.name, table_version)


async def async_build_historical_table_name(
    schema_reference: glue.SchemaReference,
    table_schema: AsyncHistoricalTableSchema,
) -> str:
    if schema_reference.name in (
        TRANSACTION_TABLE,
        METADATA_TABLE,
        REFERENCE_TABLE,
        OBJECT_TABLE,
        TABLE_SCHEMA_TABLE,
    ):
        return schema_reference.name

    class_version_manager = AsyncHistoricalSchemaVersionManager()
    _version = schema_reference.version

    if _version in (glue.Version.LATEST, Versions.LATEST):
        _version = await class_version_manager.get_latest_schema_version(schema_reference.name)

    if _version in (glue.Version.LATEST, Versions.LATEST) or not _version:
        # Still latest version means that there is no historical table
        return schema_reference.name

    table_version = await table_schema.find_table_version(
        class_version=_version,
        table_name=schema_reference.name,
    )

    return format_historical_table_name(schema_reference.name, table_version)


def format_historical_table_name(
    name: str,
    version: str,
) -> str:
    if not version:
        return name

    return f'{name}{TABLE_NAME_VERSION_SEPARATOR}{version}'
