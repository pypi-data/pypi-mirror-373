import amsdal_glue as glue
from amsdal_data.application import AsyncDataApplication as AsyncDataApplication, DataApplication as DataApplication
from amsdal_data.connections.constants import REFERENCE_TABLE as REFERENCE_TABLE, SECONDARY_PARTITION_KEY as SECONDARY_PARTITION_KEY
from amsdal_data.errors import MetadataInfoQueryError as MetadataInfoQueryError
from amsdal_utils.classes.metadata_manager import MetadataInfoQueryBase
from amsdal_utils.models.data_models.metadata import Metadata as Metadata
from amsdal_utils.models.data_models.reference import Reference
from typing import Any

class BaseMetadataInfoQuery:
    @classmethod
    def build_query_statement(cls, metadata: Metadata) -> glue.QueryStatement: ...
    @classmethod
    def build_query_statement_to_reference(cls, class_name: str, object_id: Any, object_version: Any, field_prefix: str = 'from_address', *, is_latest: bool | None = None) -> glue.QueryStatement: ...
    @staticmethod
    def _build_nested_field(field: str) -> glue.Field: ...

class MetadataInfoQuery(BaseMetadataInfoQuery, MetadataInfoQueryBase):
    @classmethod
    def get_reference_to(cls, metadata: Metadata) -> list[Reference]: ...
    @classmethod
    def get_referenced_by(cls, metadata: Metadata) -> list[Reference]: ...

class AsyncMetadataInfoQuery(BaseMetadataInfoQuery):
    @classmethod
    async def get_reference_to(cls, metadata: Metadata) -> list[Reference]: ...
    @classmethod
    async def get_referenced_by(cls, metadata: Metadata) -> list[Reference]: ...
