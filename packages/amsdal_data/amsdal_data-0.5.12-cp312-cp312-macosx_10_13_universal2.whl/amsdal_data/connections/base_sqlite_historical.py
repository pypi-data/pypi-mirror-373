import amsdal_glue as glue
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE

from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY


class BaseSqliteHistoricalConnection:
    TABLE_SQL = f"""
    SELECT
        {SCHEMA_REGISTRY_TABLE}.table_name AS table_name,
        {SCHEMA_REGISTRY_TABLE}.name AS name,
        {SCHEMA_REGISTRY_TABLE}.version AS version
    FROM (
        SELECT
            name AS table_name,
            CASE WHEN instr(name, '{TABLE_NAME_VERSION_SEPARATOR}') > 0
                 THEN substr(name, 1, instr(name, '{TABLE_NAME_VERSION_SEPARATOR}') - 1)
                 ELSE name
            END as name,
            CASE WHEN instr(name, '{TABLE_NAME_VERSION_SEPARATOR}') > 0
                 THEN substr(name, instr(name, '{TABLE_NAME_VERSION_SEPARATOR}') + 5)
                 ELSE ''
            END as version
        FROM sqlite_master
        WHERE type="table"
     ) AS {SCHEMA_REGISTRY_TABLE}
    """  # noqa: S608

    def _process_group_by(self, query: glue.QueryStatement) -> glue.QueryStatement:
        if ((query.only and not query.aggregations) or query.order_by) and query.table.name not in (  # type: ignore[union-attr]
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
        ):
            group_by = []

            if query.only and not query.aggregations:
                for _field in query.only:
                    if isinstance(_field, glue.FieldReferenceAliased):
                        _field_reference = glue.FieldReference(
                            field=_field.field,
                            table_name=_field.table_name,
                            namespace=_field.namespace,
                        )
                    else:
                        _field_reference = _field

                    group_by.append(glue.GroupByQuery(field=_field_reference))

            if len(group_by) == 1 and group_by[0].field.field.name == '*':
                _metadata = getattr(query.table, 'metadata', {}) or {}
                _pks = _metadata.get(META_PRIMARY_KEY) or [PRIMARY_PARTITION_KEY]
                group_by = [
                    glue.GroupByQuery(
                        field=glue.FieldReference(
                            field=glue.Field(name=_pk),
                            table_name=query.table.alias or query.table.name,  # type: ignore[union-attr]
                        ),
                    )
                    for _pk in _pks
                ]
                group_by.append(
                    glue.GroupByQuery(
                        field=glue.FieldReference(
                            field=glue.Field(name=SECONDARY_PARTITION_KEY),
                            table_name=query.table.alias or query.table.name,  # type: ignore[union-attr]
                        ),
                    ),
                )

            if query.order_by:
                for order_field in query.order_by:
                    group_by.append(glue.GroupByQuery(field=order_field.field))

            query.group_by = group_by

        if query.joins:
            for _join in query.joins:
                _table = _join.table

                if isinstance(_table, glue.SubQueryStatement):
                    _table.query = self._process_group_by(_table.query)

        return query

    @staticmethod
    def _apply_pagination(items: list[glue.Data], limit: glue.LimitQuery | None) -> list[glue.Data]:
        if limit is None or not limit.limit:
            return items

        return items[slice(limit.offset, limit.offset + limit.limit)]
