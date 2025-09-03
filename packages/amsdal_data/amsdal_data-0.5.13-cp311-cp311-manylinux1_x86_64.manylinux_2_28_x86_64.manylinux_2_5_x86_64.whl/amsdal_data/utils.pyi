import amsdal_glue as glue
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY, SECONDARY_PARTITION_KEY as SECONDARY_PARTITION_KEY
from amsdal_data.connections.db_alias_map import CONNECTION_BACKEND_ALIASES as CONNECTION_BACKEND_ALIASES
from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME as META_CLASS_NAME, META_PRIMARY_KEY_FIELDS as META_PRIMARY_KEY_FIELDS
from amsdal_glue_core.common.data_models.schema import FIELD_TYPE as FIELD_TYPE
from amsdal_glue_core.common.interfaces.connection import AsyncConnectionBase as AsyncConnectionBase, ConnectionBase as ConnectionBase
from amsdal_utils.config.data_models.repository_config import RepositoryConfig as RepositoryConfig
from amsdal_utils.schemas.schema import ObjectSchema as ObjectSchema, StorageMetadata
from amsdal_utils.utils.singleton import Singleton
from typing import Any

TABLE_NAME_PROPERTY: str
PRIMARY_KEY_PROPERTY: str
FOREIGN_KEYS_PROPERTY: str
UNIQUE_PROPERTY: str
INDEXED_PROPERTY: str

class SchemaManagerBase: ...

class SchemaManagerHandler(metaclass=Singleton):
    _schema_manager: SchemaManagerBase | None
    def __init__(self) -> None: ...
    def set_schema_manager(self, schema_manager: SchemaManagerBase) -> None: ...
    def get_schema_manager(self) -> SchemaManagerBase: ...

def resolve_backend_class(backend: str) -> type[ConnectionBase | AsyncConnectionBase]: ...
def get_schemas_for_connection_name(connection_name: str, repository_config: RepositoryConfig) -> list[str | None]: ...
def object_schema_to_glue_schema(object_schema: ObjectSchema, *, is_lakehouse_only: bool = False, use_foreign_keys: bool = False, schema_names: list[str] | None = None) -> glue.Schema: ...
def object_schema_type_to_glue_type(property_type: str | glue.Schema | glue.SchemaReference | FIELD_TYPE) -> glue.Schema | glue.SchemaReference | FIELD_TYPE: ...
def is_reference_type(property_type: str) -> bool: ...
def _list_normalize(storage_metadata: StorageMetadata, pk: str) -> list[str]: ...
def validate_data_by_schema(data: dict[str, Any], schema: glue.Schema) -> dict[str, Any]:
    """
    Validates the data against the schema and returns the validated data.
    Arguments:
        data (dict[str, Any]): The data to validate.
        schema (glue.Schema): The schema to validate against.
    Returns:
        dict[str, Any]: The validated data.
    Raises:
        ValueError: If the data is not valid according to the schema.
    """
