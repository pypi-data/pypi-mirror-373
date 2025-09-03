import amsdal_glue as glue
from _typeshed import Incomplete
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE, PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY, SECONDARY_PARTITION_KEY as SECONDARY_PARTITION_KEY
from amsdal_glue_core.common.expressions.expression import Expression as Expression
from typing import Any

OBJECT_ID_FIELD: str
OBJECT_VERSION_FIELD: str
METADATA_FIELD: str
NEXT_VERSION_FIELD: str
PK_FIELD_ALIAS_FOR_METADATA: str
MODEL_TABLE_ALIAS: str
METADATA_TABLE_ALIAS: str
METADATA_SELECT_EXPRESSION: Incomplete
PG_METADATA_SELECT_EXPRESSION: Incomplete
DEFAULT_PKS: Incomplete
META_PRIMARY_KEY_FIELDS: str
META_PRIMARY_KEY: str
META_FOREIGN_KEYS: str
META_CLASS_NAME: str
META_NEW_CLASS_VERSION: str

class MetadataExpression(glue.RawExpression):
    def __init__(self, output_type: type[Any] | None = None) -> None: ...

def build_metadata_join_query(table_name: str, metadata: dict[str, Any] | None) -> glue.JoinQuery: ...
def build_simple_query_statement_with_metadata(table: glue.SchemaReference, only: list[glue.FieldReference | glue.FieldReferenceAliased] | None = None, annotations: list[glue.AnnotationQuery] | None = None, joins: list[glue.JoinQuery] | None = None, where: glue.Conditions | None = None, order_by: list[glue.OrderByQuery] | None = None, limit: glue.LimitQuery | None = None) -> glue.QueryStatement: ...

class DataQueryTransform:
    query: Incomplete
    def __init__(self, query: glue.QueryStatement) -> None: ...
    def transform(self, metadata_select_expression: str = ...) -> glue.QueryStatement: ...
    def _transform_query(self, query: glue.QueryStatement, metadata_select_expression: str = ...) -> glue.QueryStatement: ...
