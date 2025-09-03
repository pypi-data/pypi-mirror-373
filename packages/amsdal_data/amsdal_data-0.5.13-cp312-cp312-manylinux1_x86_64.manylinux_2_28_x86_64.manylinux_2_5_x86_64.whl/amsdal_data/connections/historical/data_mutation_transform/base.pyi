import amsdal_glue as glue
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY
from amsdal_data.connections.historical.data_query_transform import META_FOREIGN_KEYS as META_FOREIGN_KEYS
from amsdal_utils.models.data_models.address import Address
from typing import Any

class BaseDataMutationTransform:
    @staticmethod
    def _process_foreign_keys(data: list[glue.Data]) -> None: ...
    @classmethod
    def _process_foreign_keys_for_conditions(cls, metadata: dict[str, Any] | None, query: glue.Conditions | None) -> glue.Conditions | None: ...
    @classmethod
    def _generate_references(cls, address: Address, data: Any, reference_buffer: list[glue.Data]) -> None: ...
    @staticmethod
    def _is_reference(data: Any) -> bool: ...
    @staticmethod
    def address_to_db(address: Address | dict[str, Any]) -> Address | dict[str, Any]: ...
