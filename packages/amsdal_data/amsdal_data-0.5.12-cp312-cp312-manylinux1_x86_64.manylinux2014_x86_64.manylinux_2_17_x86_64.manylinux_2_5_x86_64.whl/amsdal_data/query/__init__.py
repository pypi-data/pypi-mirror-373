from typing import Any

import amsdal_glue as glue
from amsdal_utils.classes.metadata_manager import MetadataInfoQueryBase
from amsdal_utils.models.data_models.metadata import Metadata
from amsdal_utils.models.data_models.reference import Reference
from amsdal_utils.models.enums import Versions

from amsdal_data.application import AsyncDataApplication
from amsdal_data.application import DataApplication
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.errors import MetadataInfoQueryError


class BaseMetadataInfoQuery:
    @classmethod
    def build_query_statement(cls, metadata: Metadata) -> glue.QueryStatement:
        return glue.QueryStatement(
            table=glue.SchemaReference(
                name=metadata.address.class_name,
                version=metadata.address.class_version,
            ),
            where=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field('object_id'),
                            table_name='t2',
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(metadata.address.object_id),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field('next_version'),
                            table_name='t2',
                        ),
                        output_type=str,
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(True),
                ),
            ),
        )

    @classmethod
    def build_query_statement_to_reference(
        cls,
        class_name: str,
        object_id: Any,
        object_version: Any,
        field_prefix: str = 'from_address',
        *,
        is_latest: bool | None = None,
    ) -> glue.QueryStatement:
        version_q = glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=cls._build_nested_field(f'{field_prefix}__object_version'),
                        table_name=REFERENCE_TABLE,
                    ),
                    output_type=str,
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(object_version),
            ),
        )

        if is_latest is True:
            version_q |= glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field(f'{field_prefix}__object_version'),
                            table_name=REFERENCE_TABLE,
                        ),
                        output_type=str,
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field(f'{field_prefix}__object_version'),
                            table_name=REFERENCE_TABLE,
                        ),
                        output_type=str,
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(Versions.LATEST.value),
                ),
                connector=glue.FilterConnector.OR,
            )

        return glue.QueryStatement(
            table=glue.SchemaReference(
                name=REFERENCE_TABLE,
                version=glue.Version.LATEST,
            ),
            where=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field(f'{field_prefix}__class_name'),
                            table_name=REFERENCE_TABLE,
                        ),
                        output_type=str,
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(class_name),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=cls._build_nested_field(f'{field_prefix}__object_id'),
                            table_name=REFERENCE_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(object_id, output_type=list),
                ),
                version_q,
            ),
        )

    @staticmethod
    def _build_nested_field(field: str) -> glue.Field:
        parts = field.split('__')
        root = glue.Field(name=parts[0])
        _parent = root

        for _part in parts[1:]:
            _child = glue.Field(name=_part, parent=_parent)
            _parent.child = _child
            _parent = _child

        return root


class MetadataInfoQuery(BaseMetadataInfoQuery, MetadataInfoQueryBase):
    @classmethod
    def get_reference_to(cls, metadata: Metadata) -> list[Reference]:
        object_version = metadata.address.object_version

        if object_version == Versions.LATEST:
            res = DataApplication().operation_manager.query_lakehouse(
                statement=cls.build_query_statement(metadata),
            )
            if not res.success or not res.data:
                msg = f'Failed to get references to: {res.message}'
                raise MetadataInfoQueryError(msg) from res.exception

            object_version = res.data[0].data[SECONDARY_PARTITION_KEY]

        _object_id = metadata.address.object_id

        if not isinstance(_object_id, list):
            _object_id = [_object_id]

        result = DataApplication().operation_manager.query_lakehouse(
            statement=cls.build_query_statement_to_reference(
                class_name=metadata.address.class_name,
                object_id=_object_id,
                object_version=object_version,
            ),
        )

        if not result.success:
            msg = f'Failed to get references to: {result.message}'
            raise MetadataInfoQueryError(msg) from result.exception

        return [Reference(**{'ref': item.data['to_address']}) for item in (result.data or [])]

    @classmethod
    def get_referenced_by(cls, metadata: Metadata) -> list[Reference]:
        _object_id = metadata.address.object_id

        if not isinstance(_object_id, list):
            _object_id = [_object_id]

        result = DataApplication().operation_manager.query_lakehouse(
            statement=cls.build_query_statement_to_reference(
                class_name=metadata.address.class_name,
                object_id=_object_id,
                object_version=metadata.address.object_version,
                field_prefix='to_address',
                is_latest=metadata.is_latest,
            ),
        )

        if not result.success:
            msg = f'Failed to get references to: {result.message}'
            raise MetadataInfoQueryError(msg) from result.exception

        return [Reference(**{'ref': item.data['from_address']}) for item in (result.data or [])]


class AsyncMetadataInfoQuery(BaseMetadataInfoQuery):
    @classmethod
    async def get_reference_to(cls, metadata: Metadata) -> list[Reference]:
        object_version = metadata.address.object_version

        if object_version == Versions.LATEST:
            res = await AsyncDataApplication().operation_manager.query_lakehouse(
                statement=cls.build_query_statement(metadata),
            )
            if not res.success or not res.data:
                msg = f'Failed to get references to: {res.message}'
                raise MetadataInfoQueryError(msg) from res.exception

            object_version = res.data[0].data[SECONDARY_PARTITION_KEY]

        _object_id = metadata.address.object_id

        if not isinstance(_object_id, list):
            _object_id = [_object_id]

        result = await AsyncDataApplication().operation_manager.query_lakehouse(
            statement=cls.build_query_statement_to_reference(
                class_name=metadata.address.class_name,
                object_id=_object_id,
                object_version=object_version,
            ),
        )

        if not result.success:
            msg = f'Failed to get references to: {result.message}'
            raise MetadataInfoQueryError(msg) from result.exception

        return [Reference(**{'ref': item.data['to_address']}) for item in (result.data or [])]

    @classmethod
    async def get_referenced_by(cls, metadata: Metadata) -> list[Reference]:
        _object_id = metadata.address.object_id

        if not isinstance(_object_id, list):
            _object_id = [_object_id]

        result = await AsyncDataApplication().operation_manager.query_lakehouse(
            statement=cls.build_query_statement_to_reference(
                class_name=metadata.address.class_name,
                object_id=_object_id,
                object_version=metadata.address.object_version,
                field_prefix='to_address',
                is_latest=metadata.is_latest,
            ),
        )

        if not result.success:
            msg = f'Failed to get references to: {result.message}'
            raise MetadataInfoQueryError(msg) from result.exception

        return [Reference(**{'ref': item.data['from_address']}) for item in (result.data or [])]
