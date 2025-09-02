import amsdal_glue as glue
from _typeshed import Incomplete
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE, PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY, REFERENCE_TABLE as REFERENCE_TABLE, SECONDARY_PARTITION_KEY as SECONDARY_PARTITION_KEY, TRANSACTION_TABLE as TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR as TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY as META_PRIMARY_KEY

class BaseSqliteHistoricalConnection:
    TABLE_SQL: Incomplete
    def _process_group_by(self, query: glue.QueryStatement) -> glue.QueryStatement: ...
    @staticmethod
    def _apply_pagination(items: list[glue.Data], limit: glue.LimitQuery | None) -> list[glue.Data]: ...
