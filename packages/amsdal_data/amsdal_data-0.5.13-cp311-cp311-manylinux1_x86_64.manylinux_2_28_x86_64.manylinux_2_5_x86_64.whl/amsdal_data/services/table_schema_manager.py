import logging
import os
from collections.abc import AsyncGenerator
from collections.abc import Generator
from copy import deepcopy
from typing import Any

import amsdal_glue as glue
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE
from amsdal_utils.utils.decorators import async_mode_only
from amsdal_utils.utils.decorators import sync_mode_only
from amsdal_utils.utils.singleton import Singleton

from amsdal_data.aliases.using import LAKEHOUSE_DB_ALIAS
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import SCHEMA_TABLE_NAME_FIELD
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME
from amsdal_data.connections.historical.data_query_transform import META_NEW_CLASS_VERSION
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS
from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD
from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata
from amsdal_data.errors import CommandError
from amsdal_data.errors import QueryError
from amsdal_data.errors import RegisterTableError
from amsdal_data.transactions.manager import AmsdalAsyncTransactionManager
from amsdal_data.transactions.manager import AmsdalTransactionManager
from amsdal_data.utils import FOREIGN_KEYS_PROPERTY

MIGRATION_BATCH_SIZE = int(os.getenv('AMSDAL_MIGRATION_BATCH_SIZE', 1000))  # noqa: PLW1508
logger = logging.getLogger(__name__)


class BaseTableSchemasManager:
    @classmethod
    def enrich_schema_metadata(cls, schema: glue.Schema) -> glue.Schema:
        metadata = deepcopy(schema.metadata or {})

        pk_constraint = next(
            iter(
                constraint
                for constraint in (schema.constraints or [])
                if isinstance(constraint, glue.PrimaryKeyConstraint)
            ),
            None,
        )

        if pk_constraint:
            if META_PRIMARY_KEY not in metadata:
                metadata[META_PRIMARY_KEY] = [
                    cls.process_fk_field(_field, schema=schema)
                    for _field in pk_constraint.fields
                    if _field != SECONDARY_PARTITION_KEY
                ]

            if META_PRIMARY_KEY_FIELDS not in metadata:
                metadata[META_PRIMARY_KEY_FIELDS] = {
                    cls.process_fk_field(_field, schema=schema): next(
                        _prop.type for _prop in schema.properties if _prop.name == _field
                    )
                    for _field in pk_constraint.fields
                    if _field != SECONDARY_PARTITION_KEY
                }

        schema.metadata = metadata

        return schema

    @staticmethod
    def process_fk_field(field: str, schema: glue.Schema) -> str:
        for constraint in schema.constraints or []:
            if not isinstance(constraint, glue.ForeignKeyConstraint):
                continue

            _fk_field = constraint.fields[0]

            if field != _fk_field:
                continue

            metadata = schema.metadata or {}
            fks_names = metadata.get(FOREIGN_KEYS_PROPERTY)

            if fks_names:
                fk_field = fks_names.get(constraint.name)

                if not fk_field:
                    logger.warning(
                        'ForeignKey field "%s" is not found in the schema\'s metadata by FK name "%s"',
                        field,
                        constraint.name,
                    )
                else:
                    return fk_field
            else:
                logger.warning(
                    'Error processing FKs for schema: %s. Missing "FOREIGN_KEYS_PROPERTY" metadata.',
                    schema.name,
                )

            break

        return field


class TableSchemasManager(BaseTableSchemasManager, metaclass=Singleton):
    @sync_mode_only
    def __init__(self) -> None:
        from amsdal_data.application import DataApplication
        from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager

        self._operation_manager = DataApplication().operation_manager
        self.schema_version_manager = HistoricalSchemaVersionManager()

    def register_table(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> tuple[bool, bool]:
        """
        Creates a new table in the database through connection.
        """
        schema = self.enrich_schema_metadata(schema)
        existing_schema = self.get_existing_schema(schema, using=using)

        if existing_schema:
            _class_name = (schema.metadata or {}).get(META_CLASS_NAME, schema.name)
            # Set actual last version of the schema, it was returned as LATEST
            existing_schema.version = self.schema_version_manager.get_latest_schema_version(_class_name)
            _is_updated = self._update_table(schema, existing_schema, using=using)

            return False, _is_updated
        else:
            self._create_table(schema, using=using)
            return True, False

    def unregister_table(
        self,
        schema_reference: glue.SchemaReference,
        *,
        using: str | None = None,
    ) -> None:
        if using == LAKEHOUSE_DB_ALIAS:
            result = self._operation_manager.perform_schema_command_lakehouse(
                command=glue.SchemaCommand(
                    mutations=[glue.DeleteSchema(schema_reference=schema_reference)],
                    root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalTransactionManager().transaction_id,
                ),
            )
        else:
            result = self._operation_manager.perform_schema_command(
                command=glue.SchemaCommand(
                    mutations=[glue.DeleteSchema(schema_reference=schema_reference)],
                    root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalTransactionManager().transaction_id,
                ),
            )

        if not result.success:
            msg = f'Failed to unregister schema: {result.message}'
            raise RegisterTableError(msg) from result.exception

    def get_existing_schema(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> glue.Schema | None:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                        table_name=SCHEMA_REGISTRY_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(schema.name),
            ),
        ]

        if using == LAKEHOUSE_DB_ALIAS:
            _query = self._operation_manager.schema_query_lakehouse

            if schema.version:
                # Find schema by full table name, coz we need to find the latest schema version
                _conditions = [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(f'{schema.name}{TABLE_NAME_VERSION_SEPARATOR}{glue.Version.LATEST.value}'),
                    ),
                ]
        else:
            _query = self._operation_manager.schema_query

        result = _query(filters=glue.Conditions(*_conditions))

        if result.success:
            if result.schemas:
                _schema_existing = result.schemas[0]
                if not _schema_existing:
                    msg = 'Schema not found'
                    raise ValueError(msg)

                _metadata = _schema_existing.metadata or {}
                _metadata.update(schema.metadata or {})
                _schema_existing.metadata = _metadata

                # normalize PK
                for constraint in _schema_existing.constraints or []:
                    if not isinstance(constraint, glue.PrimaryKeyConstraint):
                        continue

                    if '_x_' in constraint.name:
                        constraint.name = constraint.name.split('_x_', 1)[0]

                return self.enrich_schema_metadata(_schema_existing)
            else:
                return None

        msg = f'Error while getting schema {schema.name}: {result.message}'
        raise RegisterTableError(msg) from result.exception

    def _create_table(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> None:
        if using == LAKEHOUSE_DB_ALIAS:
            _command = self._operation_manager.perform_schema_command_lakehouse
        else:
            _command = self._operation_manager.perform_schema_command

        result = _command(
            glue.SchemaCommand(
                root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalTransactionManager().transaction_id,
                mutations=[
                    glue.RegisterSchema(schema=schema),
                ],
            ),
        )

        if not result.success:
            msg = f'Error while creating schema {schema.name}: {result.message}'
            raise RegisterTableError(msg) from result.exception

    def _update_table(
        self,
        schema: glue.Schema,
        existing_schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> bool:
        schema_reference = glue.SchemaReference(
            name=existing_schema.name,
            version=existing_schema.version,
            metadata={
                META_NEW_CLASS_VERSION: schema.version,
                **(existing_schema.metadata or {}),
            },
        )

        mutations: list[glue.SchemaMutation] = []
        new_property_names = [_prop.name for _prop in schema.properties]
        existing_property_names = [existing_prop.name for existing_prop in existing_schema.properties]

        for existing_prop in existing_schema.properties:
            if existing_prop.name not in new_property_names:
                mutations.append(
                    glue.DeleteProperty(schema_reference=schema_reference, property_name=existing_prop.name)
                )
                continue

            new_prop = schema.properties[new_property_names.index(existing_prop.name)]

            # it's all the JSON field
            if existing_prop.type is list:
                existing_prop.type = dict

            if new_prop.type is list:
                new_prop.type = dict

            if existing_prop != new_prop:
                mutations.append(glue.UpdateProperty(schema_reference=schema_reference, property=new_prop))

        for new_prop in schema.properties:
            if new_prop.name not in existing_property_names:
                mutations.append(glue.AddProperty(schema_reference=schema_reference, property=new_prop))

        new_index_names = [index.name for index in schema.indexes or []]
        existing_index_names = [existing_index.name for existing_index in existing_schema.indexes or []]

        for existing_index in existing_schema.indexes or []:
            if existing_index.name not in new_index_names:
                mutations.append(glue.DeleteIndex(schema_reference=schema_reference, index_name=existing_index.name))
                continue

            new_index = (schema.indexes or [])[new_index_names.index(existing_index.name)]

            if existing_index != new_index:
                mutations.append(glue.DeleteIndex(schema_reference=schema_reference, index_name=existing_index.name))
                mutations.append(glue.AddIndex(schema_reference=schema_reference, index=new_index))

        for new_index in schema.indexes or []:
            if new_index.name not in existing_index_names:
                mutations.append(glue.AddIndex(schema_reference=schema_reference, index=new_index))

        new_constraint_names = [constraint.name for constraint in schema.constraints or []]
        existing_constraint_names = [
            existing_constraint.name for existing_constraint in existing_schema.constraints or []
        ]

        for existing_constraint in existing_schema.constraints or []:
            if existing_constraint.name not in new_constraint_names:
                mutations.append(
                    glue.DeleteConstraint(schema_reference=schema_reference, constraint_name=existing_constraint.name)
                )
                continue

            new_constraint = (schema.constraints or [])[new_constraint_names.index(existing_constraint.name)]

            if existing_constraint != new_constraint:
                mutations.append(
                    glue.DeleteConstraint(
                        schema_reference=schema_reference,
                        constraint_name=existing_constraint.name,
                    ),
                )
                mutations.append(glue.AddConstraint(schema_reference=schema_reference, constraint=new_constraint))

        for new_constraint in schema.constraints or []:
            if new_constraint.name not in existing_constraint_names:
                mutations.append(glue.AddConstraint(schema_reference=schema_reference, constraint=new_constraint))

        if not mutations:
            return False

        if using == LAKEHOUSE_DB_ALIAS:
            _command = self._operation_manager.perform_schema_command_lakehouse
        else:
            _command = self._operation_manager.perform_schema_command

        result = _command(
            glue.SchemaCommand(
                mutations=mutations,
                root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalTransactionManager().transaction_id,
            ),
        )

        if not result.success:
            msg = f'Error while updating schema {schema.name}: {result.message}'
            raise RegisterTableError(msg) from result.exception

        return True

    def fetch_historical_data(
        self,
        schema_reference: glue.SchemaReference,
        batch_size: int = MIGRATION_BATCH_SIZE,
        offset: int = 0,
        extra_conditions: glue.Conditions | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name='is_deleted'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=False),
            ),
            glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(value=True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=''),
                ),
                connector=glue.FilterConnector.OR,
            ),
        ]

        if extra_conditions:
            _conditions.append(extra_conditions)

        query = build_simple_query_statement_with_metadata(
            table=schema_reference,
            where=glue.Conditions(*_conditions),
            order_by=[
                glue.OrderByQuery(
                    field=glue.FieldReference(
                        field=glue.Field(name='updated_at'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                    direction=glue.OrderDirection.ASC,
                ),
            ],
            limit=glue.LimitQuery(limit=batch_size, offset=offset),
        )

        result = self._operation_manager.query_lakehouse(statement=query)

        if not result.success:
            msg = f'Error while fetching historical data: {result.message}'
            raise QueryError(msg) from result.exception

        for data in result.data or []:
            yield data.data

        if len(result.data or []) == batch_size:
            yield from self.fetch_historical_data(schema_reference, batch_size, offset + batch_size)

    def search_latest_class_object(
        self,
        schema_reference: glue.SchemaReference,
        class_object_name: str,
    ) -> dict[str, Any] | None:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=PRIMARY_PARTITION_KEY),
                        table_name=schema_reference.name,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(class_object_name),
            ),
            glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(value=True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=''),
                ),
                connector=glue.FilterConnector.OR,
            ),
        ]
        query = build_simple_query_statement_with_metadata(
            table=schema_reference,
            where=glue.Conditions(*_conditions),
            limit=glue.LimitQuery(limit=1),
        )

        result = self._operation_manager.query_lakehouse(query)

        if not result.success:
            msg = f'Error while searching latest class object version in lakehouse: {result.message}'
            raise QueryError(msg) from result.exception

        if result.data:
            return result.data[0].data
        return None

    def insert_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_data: glue.Data,
    ) -> dict[str, Any]:
        mutation = glue.InsertData(
            schema=schema_reference,
            data=[class_object_data],
        )

        return self._mutate_class_object_schema(mutation)

    def update_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_data: glue.Data,
    ) -> dict[str, Any]:
        next_version_field = glue.FieldReference(
            field=glue.Field(name=NEXT_VERSION_FIELD),
            table_name=METADATA_TABLE_ALIAS,
        )
        mutation = glue.UpdateData(
            schema=schema_reference,
            data=class_object_data,
            query=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=PRIMARY_PARTITION_KEY),
                            table_name=schema_reference.name,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=class_object_data.data[PRIMARY_PARTITION_KEY]),
                ),
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.ISNULL,
                        right=glue.Value(value=True),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(value=''),
                    ),
                    connector=glue.FilterConnector.OR,
                ),
            ),
        )

        return self._mutate_class_object_schema(mutation)

    def delete_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_id: str,
    ) -> dict[str, Any]:
        next_version_field = glue.FieldReference(
            field=glue.Field(name=NEXT_VERSION_FIELD),
            table_name=METADATA_TABLE_ALIAS,
        )
        mutation = glue.DeleteData(
            schema=schema_reference,
            query=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=PRIMARY_PARTITION_KEY),
                            table_name=schema_reference.name,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=class_object_id),
                ),
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.ISNULL,
                        right=glue.Value(value=True),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(value=''),
                    ),
                    connector=glue.FilterConnector.OR,
                ),
            ),
        )

        return self._mutate_class_object_schema(mutation)

    def _mutate_class_object_schema(
        self,
        mutation: glue.InsertData | glue.UpdateData | glue.DeleteData,
    ) -> dict[str, Any]:
        result = self._operation_manager.perform_data_command_lakehouse(
            command=glue.DataCommand(
                mutations=[mutation],
                root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalTransactionManager().transaction_id,
            ),
        )

        if not result.success:
            msg = f'Error while {mutation.__class__} class object schema in lakehouse: {result.message}'
            raise CommandError(msg) from result.exception

        # the first index 0 represents index of mutation, the second index - index of data
        # TODO: review types here
        return result.data[0][0].data  # type: ignore[index]


class AsyncTableSchemasManager(BaseTableSchemasManager, metaclass=Singleton):
    @async_mode_only
    def __init__(self) -> None:
        from amsdal_data.application import AsyncDataApplication
        from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager

        self._operation_manager = AsyncDataApplication().operation_manager
        self.schema_version_manager = AsyncHistoricalSchemaVersionManager()

    async def register_table(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> tuple[bool, bool]:
        """
        Creates a new table in the database through connection.
        """
        schema = self.enrich_schema_metadata(schema)
        existing_schema = await self.get_existing_schema(schema, using=using)

        if existing_schema:
            _class_name = (schema.metadata or {}).get(META_CLASS_NAME, schema.name)
            # Set actual last version of the schema, it was returned as LATEST
            existing_schema.version = await self.schema_version_manager.get_latest_schema_version(_class_name)
            _is_updated = await self._update_table(schema, existing_schema, using=using)

            return False, _is_updated
        else:
            await self._create_table(schema, using=using)
            return True, False

    async def unregister_table(
        self,
        schema_reference: glue.SchemaReference,
        *,
        using: str | None = None,
    ) -> None:
        if using == LAKEHOUSE_DB_ALIAS:
            result = await self._operation_manager.perform_schema_command_lakehouse(
                command=glue.SchemaCommand(
                    mutations=[glue.DeleteSchema(schema_reference=schema_reference)],
                    root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalAsyncTransactionManager().transaction_id,
                ),
            )
        else:
            result = await self._operation_manager.perform_schema_command(
                command=glue.SchemaCommand(
                    mutations=[glue.DeleteSchema(schema_reference=schema_reference)],
                    root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalAsyncTransactionManager().transaction_id,
                ),
            )

        if not result.success:
            msg = f'Failed to unregister schema: {result.message}'
            raise RegisterTableError(msg) from result.exception

    async def get_existing_schema(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> glue.Schema | None:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                        table_name=SCHEMA_REGISTRY_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(schema.name),
            ),
        ]

        if using == LAKEHOUSE_DB_ALIAS:
            _query = self._operation_manager.schema_query_lakehouse

            if schema.version:
                # Find schema by full table name, coz we need to find the latest schema version
                _conditions = [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(f'{schema.name}{TABLE_NAME_VERSION_SEPARATOR}{glue.Version.LATEST.value}'),
                    ),
                ]
        else:
            _query = self._operation_manager.schema_query

        result = await _query(filters=glue.Conditions(*_conditions))

        if result.success:
            if result.schemas:
                _schema_existing = result.schemas[0]
                if not _schema_existing:
                    msg = 'Schema not found'
                    raise ValueError(msg)

                _metadata = _schema_existing.metadata or {}
                _metadata.update(schema.metadata or {})
                _schema_existing.metadata = _metadata

                # normalize PK
                for constraint in _schema_existing.constraints or []:
                    if not isinstance(constraint, glue.PrimaryKeyConstraint):
                        continue

                    if '_x_' in constraint.name:
                        constraint.name = constraint.name.split('_x_', 1)[0]

                return self.enrich_schema_metadata(_schema_existing)
            else:
                return None

        msg = f'Error while getting schema {schema.name}: {result.message}'
        raise RegisterTableError(msg) from result.exception

    async def _create_table(
        self,
        schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> None:
        if using == LAKEHOUSE_DB_ALIAS:
            _command = self._operation_manager.perform_schema_command_lakehouse
        else:
            _command = self._operation_manager.perform_schema_command

        result = await _command(
            glue.SchemaCommand(
                root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalAsyncTransactionManager().transaction_id,
                mutations=[
                    glue.RegisterSchema(schema=schema),
                ],
            ),
        )

        if not result.success:
            msg = f'Error while creating schema {schema.name}: {result.message}'
            raise RegisterTableError(msg) from result.exception

    async def _update_table(
        self,
        schema: glue.Schema,
        existing_schema: glue.Schema,
        *,
        using: str | None = None,
    ) -> bool:
        schema_reference = glue.SchemaReference(
            name=existing_schema.name,
            version=existing_schema.version,
            metadata={
                META_NEW_CLASS_VERSION: schema.version,
                **(existing_schema.metadata or {}),
            },
        )

        mutations: list[glue.SchemaMutation] = []
        new_property_names = [_prop.name for _prop in schema.properties]
        existing_property_names = [existing_prop.name for existing_prop in existing_schema.properties]

        for existing_prop in existing_schema.properties:
            if existing_prop.name not in new_property_names:
                mutations.append(
                    glue.DeleteProperty(schema_reference=schema_reference, property_name=existing_prop.name)
                )
                continue

            new_prop = schema.properties[new_property_names.index(existing_prop.name)]

            # it's all the JSON field
            if existing_prop.type is list:
                existing_prop.type = dict

            if new_prop.type is list:
                new_prop.type = dict

            if existing_prop != new_prop:
                mutations.append(glue.UpdateProperty(schema_reference=schema_reference, property=new_prop))

        for new_prop in schema.properties:
            if new_prop.name not in existing_property_names:
                mutations.append(glue.AddProperty(schema_reference=schema_reference, property=new_prop))

        new_index_names = [index.name for index in schema.indexes or []]
        existing_index_names = [existing_index.name for existing_index in existing_schema.indexes or []]

        for existing_index in existing_schema.indexes or []:
            if existing_index.name not in new_index_names:
                mutations.append(glue.DeleteIndex(schema_reference=schema_reference, index_name=existing_index.name))
                continue

            new_index = (schema.indexes or [])[new_index_names.index(existing_index.name)]

            if existing_index != new_index:
                mutations.append(glue.DeleteIndex(schema_reference=schema_reference, index_name=existing_index.name))
                mutations.append(glue.AddIndex(schema_reference=schema_reference, index=new_index))

        for new_index in schema.indexes or []:
            if new_index.name not in existing_index_names:
                mutations.append(glue.AddIndex(schema_reference=schema_reference, index=new_index))

        new_constraint_names = [constraint.name for constraint in schema.constraints or []]
        existing_constraint_names = [
            existing_constraint.name for existing_constraint in existing_schema.constraints or []
        ]

        for existing_constraint in existing_schema.constraints or []:
            if existing_constraint.name not in new_constraint_names:
                mutations.append(
                    glue.DeleteConstraint(schema_reference=schema_reference, constraint_name=existing_constraint.name)
                )
                continue

            new_constraint = (schema.constraints or [])[new_constraint_names.index(existing_constraint.name)]

            if existing_constraint != new_constraint:
                mutations.append(
                    glue.DeleteConstraint(
                        schema_reference=schema_reference,
                        constraint_name=existing_constraint.name,
                    ),
                )
                mutations.append(glue.AddConstraint(schema_reference=schema_reference, constraint=new_constraint))

        for new_constraint in schema.constraints or []:
            if new_constraint.name not in existing_constraint_names:
                mutations.append(glue.AddConstraint(schema_reference=schema_reference, constraint=new_constraint))

        if not mutations:
            return False

        if using == LAKEHOUSE_DB_ALIAS:
            _command = self._operation_manager.perform_schema_command_lakehouse
        else:
            _command = self._operation_manager.perform_schema_command

        result = await _command(
            glue.SchemaCommand(
                mutations=mutations,
                root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalAsyncTransactionManager().transaction_id,
            ),
        )

        if not result.success:
            msg = f'Error while updating schema {schema.name}: {result.message}'
            raise RegisterTableError(msg) from result.exception

        return True

    async def fetch_historical_data(
        self,
        schema_reference: glue.SchemaReference,
        batch_size: int = MIGRATION_BATCH_SIZE,
        offset: int = 0,
        extra_conditions: glue.Conditions | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name='is_deleted'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=False),
            ),
            glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(value=True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=''),
                ),
                connector=glue.FilterConnector.OR,
            ),
        ]

        if extra_conditions:
            _conditions.append(extra_conditions)

        query = build_simple_query_statement_with_metadata(
            table=schema_reference,
            where=glue.Conditions(*_conditions),
            order_by=[
                glue.OrderByQuery(
                    field=glue.FieldReference(
                        field=glue.Field(name='updated_at'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                    direction=glue.OrderDirection.ASC,
                ),
            ],
            limit=glue.LimitQuery(limit=batch_size, offset=offset),
        )

        result = await self._operation_manager.query_lakehouse(statement=query)

        if not result.success:
            msg = f'Error while fetching historical data: {result.message}'
            raise QueryError(msg) from result.exception

        for data in result.data or []:
            yield data.data

        if len(result.data or []) == batch_size:
            async for h_data in self.fetch_historical_data(schema_reference, batch_size, offset + batch_size):
                yield h_data

    async def search_latest_class_object(
        self,
        schema_reference: glue.SchemaReference,
        class_object_name: str,
    ) -> dict[str, Any] | None:
        _conditions = [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=PRIMARY_PARTITION_KEY),
                        table_name=schema_reference.name,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(class_object_name),
            ),
            glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(value=True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=NEXT_VERSION_FIELD),
                            table_name=METADATA_TABLE_ALIAS,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=''),
                ),
                connector=glue.FilterConnector.OR,
            ),
        ]

        query = build_simple_query_statement_with_metadata(
            table=schema_reference,
            where=glue.Conditions(*_conditions),
            limit=glue.LimitQuery(limit=1),
        )

        result = await self._operation_manager.query_lakehouse(query)

        if not result.success:
            msg = f'Error while searching latest class object version in lakehouse: {result.message}'
            raise QueryError(msg) from result.exception

        if result.data:
            return result.data[0].data
        return None

    async def insert_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_data: glue.Data,
    ) -> dict[str, Any]:
        mutation = glue.InsertData(
            schema=schema_reference,
            data=[class_object_data],
        )

        return await self._mutate_class_object_schema(mutation)

    async def update_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_data: glue.Data,
    ) -> dict[str, Any]:
        next_version_field = glue.FieldReference(
            field=glue.Field(name=NEXT_VERSION_FIELD),
            table_name=METADATA_TABLE_ALIAS,
        )
        mutation = glue.UpdateData(
            schema=schema_reference,
            data=class_object_data,
            query=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=PRIMARY_PARTITION_KEY),
                            table_name=schema_reference.name,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=class_object_data.data[PRIMARY_PARTITION_KEY]),
                ),
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.ISNULL,
                        right=glue.Value(value=True),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(value=''),
                    ),
                    connector=glue.FilterConnector.OR,
                ),
            ),
        )

        return await self._mutate_class_object_schema(mutation)

    async def delete_class_object_schema(
        self,
        schema_reference: glue.SchemaReference,
        class_object_id: str,
    ) -> dict[str, Any]:
        next_version_field = glue.FieldReference(
            field=glue.Field(name=NEXT_VERSION_FIELD),
            table_name=METADATA_TABLE_ALIAS,
        )
        mutation = glue.DeleteData(
            schema=schema_reference,
            query=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=PRIMARY_PARTITION_KEY),
                            table_name=schema_reference.name,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(value=class_object_id),
                ),
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.ISNULL,
                        right=glue.Value(value=True),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(field_reference=next_version_field),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(value=''),
                    ),
                    connector=glue.FilterConnector.OR,
                ),
            ),
        )

        return await self._mutate_class_object_schema(mutation)

    async def _mutate_class_object_schema(
        self,
        mutation: glue.InsertData | glue.UpdateData | glue.DeleteData,
    ) -> dict[str, Any]:
        result = await self._operation_manager.perform_data_command_lakehouse(
            command=glue.DataCommand(
                mutations=[mutation],
                root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalAsyncTransactionManager().transaction_id,
            ),
        )

        if not result.success:
            msg = f'Error while {mutation.__class__} class object schema in lakehouse: {result.message}'
            raise CommandError(msg) from result.exception

        # the first index 0 represents index of mutation, the second index - index of data
        # TODO: review types here
        return result.data[0][0].data  # type: ignore[index]
