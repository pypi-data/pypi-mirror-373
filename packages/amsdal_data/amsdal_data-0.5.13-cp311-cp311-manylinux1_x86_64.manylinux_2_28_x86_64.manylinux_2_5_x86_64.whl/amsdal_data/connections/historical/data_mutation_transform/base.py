from copy import copy
from copy import deepcopy
from typing import Any

import amsdal_glue as glue
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.utils.identifier import get_identifier

from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.historical.data_query_transform import META_FOREIGN_KEYS


class BaseDataMutationTransform:
    @staticmethod
    def _process_foreign_keys(
        data: list[glue.Data],
    ) -> None:
        for _data in data:
            foreign_keys = (_data.metadata or {}).get(META_FOREIGN_KEYS, {})

            for foreign_key, (reference, fields) in foreign_keys.items():
                if foreign_key in _data.data:
                    continue

                for _field in fields:
                    _data.data.pop(_field, None)

                _data.data[foreign_key] = reference.model_dump() if reference else None

    @classmethod
    def _process_foreign_keys_for_conditions(
        cls,
        metadata: dict[str, Any] | None,
        query: glue.Conditions | None,
    ) -> glue.Conditions | None:
        if query is None:
            return None

        _query = glue.Conditions(
            connector=query.connector,
            negated=query.negated,
        )
        fks = (metadata or {}).get(META_FOREIGN_KEYS, {})

        for child in query.children:
            if isinstance(child, glue.Conditions):
                if _processed_child := cls._process_foreign_keys_for_conditions(metadata, child):
                    _query.children.append(_processed_child)
                continue

            if not isinstance(child.left, glue.FieldReferenceExpression):
                _query.children.append(child)
                continue

            _field_name = child.left.field_reference.field.name
            _condition = copy(child)

            for _fk_field, (_ref, _fields) in fks.items():
                if _field_name in _fields:
                    _condition = glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(
                                    name=_fk_field,
                                ),
                                table_name=child.left.field_reference.table_name,
                                namespace=child.left.field_reference.namespace,
                            ),
                        ),
                        lookup=child.lookup,
                        negate=child.negate,
                        right=glue.Value(value=_ref.model_dump()),
                    )
                    break
            _query.children.append(_condition)

        return _query

    @classmethod
    def _generate_references(
        cls,
        address: Address,
        data: Any,
        reference_buffer: list[glue.Data],
    ) -> None:
        if cls._is_reference(data):
            reference_buffer.append(
                glue.Data(
                    data={
                        PRIMARY_PARTITION_KEY: get_identifier(),
                        'from_address': cls.address_to_db(address.model_dump()),
                        'to_address': cls.address_to_db(data['ref'].copy()),
                    },
                ),
            )
        elif isinstance(data, list):
            for data_value in data:
                cls._generate_references(address, data_value, reference_buffer)

        elif isinstance(data, dict):
            for data_value in data.values():
                cls._generate_references(address, data_value, reference_buffer)

    @staticmethod
    def _is_reference(data: Any) -> bool:
        return isinstance(data, dict) and ['ref'] == list(data.keys()) and isinstance(data['ref'], dict)

    @staticmethod
    def address_to_db(address: Address | dict[str, Any]) -> Address | dict[str, Any]:
        _address = address.model_copy(deep=True) if isinstance(address, Address) else deepcopy(address)

        if isinstance(_address, Address):
            if not isinstance(_address.object_id, list):
                _address.object_id = [_address.object_id]
            return _address.model_dump()

        if not isinstance(_address['object_id'], list):
            _address['object_id'] = [_address['object_id']]
        return _address
