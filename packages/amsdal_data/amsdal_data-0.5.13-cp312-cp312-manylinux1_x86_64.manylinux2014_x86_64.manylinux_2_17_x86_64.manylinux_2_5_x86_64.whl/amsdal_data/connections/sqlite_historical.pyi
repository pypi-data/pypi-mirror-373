import amsdal_glue as glue
from _typeshed import Incomplete
from amsdal_data.connections.base_sqlite_historical import BaseSqliteHistoricalConnection as BaseSqliteHistoricalConnection
from amsdal_data.connections.common import get_class_name as get_class_name, get_table_version as get_table_version
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE, OBJECT_TABLE as OBJECT_TABLE, PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY, REFERENCE_TABLE as REFERENCE_TABLE, TABLE_SCHEMA_TABLE as TABLE_SCHEMA_TABLE, TRANSACTION_TABLE as TRANSACTION_TABLE
from amsdal_data.connections.historical.data_mutation_transform import DataMutationTransform as DataMutationTransform
from amsdal_data.connections.historical.data_query_transform import DataQueryTransform as DataQueryTransform
from amsdal_data.connections.historical.query_builder import pull_out_filter_from_query as pull_out_filter_from_query, sort_items as sort_items, split_conditions as split_conditions
from amsdal_data.connections.historical.schema_command_transform import SchemaCommandExecutor as SchemaCommandExecutor
from amsdal_data.connections.historical.schema_query_filters_transform import SchemaQueryFiltersTransform as SchemaQueryFiltersTransform
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager as HistoricalSchemaVersionManager
from amsdal_data.connections.historical.table_name_transform import TableNameTransform as TableNameTransform
from amsdal_data.errors import AmsdalConnectionError as AmsdalConnectionError
from amsdal_data.services.historical_table_schema import HistoricalTableSchema as HistoricalTableSchema
from amsdal_glue_core.common.operations.mutations.data import DataMutation as DataMutation
from amsdal_utils.models.enums import Versions
from pathlib import Path
from typing import Any

class SqliteHistoricalConnection(BaseSqliteHistoricalConnection, glue.SqliteConnection):
    table_schema: HistoricalTableSchema
    schema_version_manager: Incomplete
    def __init__(self) -> None: ...
    def connect(self, db_path: Path, *, check_same_thread: bool = False, **kwargs: Any) -> None: ...
    def query(self, query: glue.QueryStatement) -> list[glue.Data]: ...
    def query_schema(self, filters: glue.Conditions | None = None) -> list[glue.Schema]: ...
    def _run_mutation(self, mutation: DataMutation) -> list[glue.Data] | None: ...
    def run_schema_command(self, command: glue.SchemaCommand) -> list[glue.Schema | None]: ...
    def run_schema_mutation(self, mutation: glue.SchemaMutation) -> glue.Schema | None: ...
    def _build_queries_by_version(self, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...
    def _to_queries_by_version(self, version: glue.Version | Versions, query: glue.QueryStatement) -> list[glue.QueryStatement]: ...
