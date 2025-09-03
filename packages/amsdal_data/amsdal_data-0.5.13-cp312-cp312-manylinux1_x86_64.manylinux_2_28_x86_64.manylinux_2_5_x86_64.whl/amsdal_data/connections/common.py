import amsdal_glue as glue

from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME


def get_table_version(table: glue.SchemaReference | glue.SubQueryStatement) -> str | glue.Version:
    if isinstance(table, glue.SubQueryStatement):
        return get_table_version(table.query.table)
    return table.version


def get_class_name(table: glue.SchemaReference | glue.SubQueryStatement) -> str:
    if isinstance(table, glue.SubQueryStatement):
        return get_class_name(table.query.table)
    return (table.metadata or {}).get(META_CLASS_NAME, table.name)
