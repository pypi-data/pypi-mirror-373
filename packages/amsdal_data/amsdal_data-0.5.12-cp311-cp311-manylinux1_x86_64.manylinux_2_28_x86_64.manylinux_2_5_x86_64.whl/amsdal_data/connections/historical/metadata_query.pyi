import amsdal_glue as glue
from amsdal_data.connections.constants import METADATA_TABLE as METADATA_TABLE
from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD as NEXT_VERSION_FIELD
from typing import Any

def build_metadata_query(object_id: list[Any], class_name: str) -> glue.QueryStatement: ...
