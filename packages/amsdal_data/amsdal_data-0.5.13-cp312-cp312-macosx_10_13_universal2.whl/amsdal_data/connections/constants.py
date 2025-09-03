from datetime import datetime

import amsdal_glue as glue

PRIMARY_PARTITION_KEY = 'partition_key'
SECONDARY_PARTITION_KEY = 'range_key'

METADATA_TABLE = 'Metadata'
REFERENCE_TABLE = 'Reference'
TRANSACTION_TABLE = 'Transaction'
OBJECT_TABLE = 'Object'
TABLE_SCHEMA_TABLE = 'TableSchema'

METADATA_KEY = '_metadata'

SCHEMA_TABLE_NAME_FIELD = 'table_name'
SCHEMA_NAME_FIELD = 'name'
SCHEMA_VERSION_FIELD = 'version'

CLASS_OBJECT = 'ClassObject'
CLASS_OBJECT_META = 'ClassObjectMeta'
OBJECT_ID = 'object_id'
OBJECT_VERSION = 'object_version'

TABLE_SCHEMA__TABLE_NAME = 'table_name'
TABLE_SCHEMA__TABLE_VERSION = 'table_version'
TABLE_SCHEMA__CREATED_AT = 'created_at'

TABLE_SCHEMA = glue.Schema(
    name=TABLE_SCHEMA_TABLE,
    version='',
    properties=[
        glue.PropertySchema(
            name=SCHEMA_NAME_FIELD,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name=SCHEMA_VERSION_FIELD,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name=TABLE_SCHEMA__TABLE_NAME,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name=TABLE_SCHEMA__TABLE_VERSION,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name=TABLE_SCHEMA__CREATED_AT,
            type=datetime,
            required=True,
        ),
    ],
    constraints=[],
    indexes=[
        glue.IndexSchema(
            name='idx_table_schema__version',
            fields=[SCHEMA_VERSION_FIELD],
        ),
        glue.IndexSchema(
            name='idx_table_schema__version_table_name',
            fields=[SCHEMA_VERSION_FIELD, TABLE_SCHEMA__TABLE_NAME],
        ),
        glue.IndexSchema(
            name='idx_table_schema__table_version',
            fields=[TABLE_SCHEMA__TABLE_VERSION],
        ),
    ],
)
