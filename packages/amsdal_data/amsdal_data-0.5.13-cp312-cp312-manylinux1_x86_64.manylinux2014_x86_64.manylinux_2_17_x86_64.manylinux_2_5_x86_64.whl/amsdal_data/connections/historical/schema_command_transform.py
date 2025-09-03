import json
import uuid
from collections import defaultdict
from copy import copy
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar
from typing import Union

import amsdal_glue as glue
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE
from amsdal_glue_core.common.data_models.constraints import BaseConstraint
from amsdal_glue_core.common.operations.mutations.data import DataMutation
from amsdal_utils.errors import AmsdalError
from amsdal_utils.models.data_models.metadata import Metadata
from amsdal_utils.models.enums import Versions
from amsdal_utils.utils.identifier import get_identifier
from pydantic import ValidationError

from amsdal_data.connections.constants import METADATA_KEY
from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SCHEMA_TABLE_NAME_FIELD
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.command_builder import format_historical_table_name
from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME
from amsdal_data.connections.historical.data_query_transform import META_NEW_CLASS_VERSION
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS
from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD
from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_data.query import AsyncMetadataInfoQuery
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema
from amsdal_data.services.historical_table_schema import HistoricalTableSchema
from amsdal_data.services.table_schema_manager import BaseTableSchemasManager
from amsdal_data.utils import FOREIGN_KEYS_PROPERTY
from amsdal_data.utils import validate_data_by_schema

if TYPE_CHECKING:
    from amsdal_data.connections.async_sqlite_historical import AsyncSqliteHistoricalConnection
    from amsdal_data.connections.postgresql_historical import AsyncPostgresHistoricalConnection
    from amsdal_data.connections.postgresql_historical import PostgresHistoricalConnection
    from amsdal_data.connections.sqlite_historical import SqliteHistoricalConnection

SchemaT = TypeVar('SchemaT', bound=glue.RegisterSchema | glue.DeleteSchema)


class _BaseSchemaCommandExecutor:
    DATA_TRANSFORM_BATCH_SIZE = 1000

    def __init__(self) -> None:
        self._schemas_cache: dict[tuple[str, str], glue.Schema] = {}

    @staticmethod
    def _check_single_mutation(mutations: list[glue.SchemaMutation]) -> None:
        if len(mutations) != 1:
            msg = f'SchemaCommandExecutor._check_single_mutation failed: Expected 1 mutation, got {len(mutations)}'
            raise ValueError(msg)

    @staticmethod
    def _adjust_to_historical_properties(mutation: glue.RegisterSchema) -> glue.RegisterSchema:
        if mutation.schema.name in (
            TRANSACTION_TABLE,
            METADATA_TABLE,
            REFERENCE_TABLE,
        ):
            return mutation

        for idx, _property in enumerate(mutation.schema.properties):
            if _property.name == METADATA_KEY:
                del mutation.schema.properties[idx]
                break

        if not any(_property.name == SECONDARY_PARTITION_KEY for _property in mutation.schema.properties):
            mutation.schema.properties.append(
                glue.PropertySchema(
                    name=SECONDARY_PARTITION_KEY,
                    type=str,
                    required=True,
                ),
            )

        for constraint in mutation.schema.constraints or []:
            if isinstance(constraint, glue.PrimaryKeyConstraint):
                if SECONDARY_PARTITION_KEY not in constraint.fields:
                    constraint.fields.append(SECONDARY_PARTITION_KEY)
                break
        return mutation

    @classmethod
    def adjust_references_in_data(
        cls,
        data: Any,
        target_class_name: str,
        target_object_id: Any,
        target_object_version: str,
        replace_object_version: str,
        replace_class_version: str,
    ) -> bool:
        _found = False

        for value in data.values():
            if isinstance(value, list):
                for _item in value:
                    _found |= cls.adjust_references_in_data(
                        {'': _item},
                        target_class_name=target_class_name,
                        target_object_id=target_object_id,
                        target_object_version=target_object_version,
                        replace_object_version=replace_object_version,
                        replace_class_version=replace_class_version,
                    )

                    if _found:
                        break
            elif isinstance(value, dict):
                if 'ref' not in value:
                    continue

                if value['ref']['class_name'] != target_class_name:
                    continue

                if value['ref']['object_id'] != target_object_id:
                    continue

                if value['ref']['object_version'] != target_object_version:
                    continue

                # Found! Update object_version to the latest one.
                value['ref']['object_version'] = replace_object_version
                # And update class version to actual one
                value['ref']['class_version'] = replace_class_version
                _found |= True
                break

        return _found

    def _set_schema_version(
        self,
        mutation: SchemaT,
        *,
        force_new_version: bool = False,
    ) -> SchemaT:
        schema_reference = mutation.get_schema_reference()
        schema_version = schema_reference.version

        if not schema_version:
            return mutation

        if schema_version == glue.Version.LATEST or force_new_version:
            schema_version = get_identifier()

        if isinstance(mutation, glue.DeleteSchema):
            mutation.schema_reference.version = schema_version
        elif isinstance(mutation, glue.RegisterSchema):
            mutation.schema.version = schema_version

        return mutation

    @staticmethod
    def _exclude_unique_constraints(mutation: glue.RegisterSchema) -> glue.RegisterSchema:
        _schema = copy(mutation.schema)
        _schema.constraints = [
            _constraint
            for _constraint in (_schema.constraints or [])
            if not isinstance(_constraint, glue.UniqueConstraint)
        ]
        return glue.RegisterSchema(schema=_schema)

    @classmethod
    def _adjust_pk_constraints(cls, mutation: glue.RegisterSchema) -> glue.RegisterSchema:
        _schema = copy(mutation.schema)
        _pk_constraint = None

        for _constraint in _schema.constraints or []:
            cls._adjust_pk_constraint(_constraint)

            if isinstance(_constraint, glue.PrimaryKeyConstraint):
                _pk_constraint = _constraint

        if _pk_constraint:
            if _schema.metadata and META_PRIMARY_KEY_FIELDS in _schema.metadata:
                _pk_constraint.fields = list(_schema.metadata[META_PRIMARY_KEY_FIELDS].keys())

        return glue.RegisterSchema(schema=_schema)

    @classmethod
    def _adjust_fk_constraints(cls, mutation: glue.RegisterSchema) -> glue.RegisterSchema:
        _schema = copy(mutation.schema)
        _constraints = []

        for _constraint in _schema.constraints or []:
            if not isinstance(_constraint, glue.ForeignKeyConstraint):
                _constraints.append(_constraint)
                continue

            required = bool(
                [_prop for _prop in _schema.properties if _prop.name in _constraint.fields and _prop.required]
            )
            _schema.properties = [_prop for _prop in _schema.properties if _prop.name not in _constraint.fields]
            _field_name = (_schema.metadata or {})[FOREIGN_KEYS_PROPERTY][_constraint.name]

            if not any(_prop.name == _field_name for _prop in _schema.properties):
                _schema.properties.append(
                    glue.PropertySchema(
                        name=_field_name,
                        type=dict,
                        required=required,
                    ),
                )

        _schema.constraints = _constraints

        return glue.RegisterSchema(schema=_schema)

    @staticmethod
    def _adjust_pk_constraint(constraint: BaseConstraint) -> None:
        if isinstance(constraint, glue.PrimaryKeyConstraint):
            if '_x_' in constraint.name:
                constraint.name = constraint.name.rsplit('_x_', 1)[0]

            constraint.name += f'_x_{uuid.uuid4().hex[:8]}'


class SchemaCommandExecutor(_BaseSchemaCommandExecutor):
    def __init__(
        self,
        connection: Union['SqliteHistoricalConnection', 'PostgresHistoricalConnection'],
        schema_command: glue.SchemaCommand,
        historical_table_schema: HistoricalTableSchema,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.schema_command = copy(schema_command)
        self.schema_version_manager = HistoricalSchemaVersionManager()
        self._historical_table_schema = historical_table_schema

    @property
    def historical_table_schema(self) -> HistoricalTableSchema:
        if self._historical_table_schema is None:
            msg = 'Historical table schema is not set.'
            raise ValueError(msg)

        return self._historical_table_schema

    def execute(self) -> list[glue.Schema | None]:
        result: list[glue.Schema | None] = []
        items, data_transfer = self._transform_mutations()

        for _mutation in items:
            _result = self._execute_mutation(_mutation)
            result.extend(_result)

        for old_schema_ref, new_schema_ref in data_transfer:
            self._transfer_data(old_schema_ref, new_schema_ref)

        return result

    def _transform_mutations(
        self,
    ) -> tuple[
        list[glue.RegisterSchema],
        list[tuple[glue.SchemaReference, glue.SchemaReference]],
    ]:
        result: list[glue.RegisterSchema] = []
        data_transfer: list[tuple[glue.SchemaReference, glue.SchemaReference]] = []
        # group by schema name and type
        grouped: dict[tuple[str, type[glue.SchemaMutation]], list[glue.SchemaMutation]] = defaultdict(list)

        _type: type[glue.SchemaMutation]

        for schema_mutation in self.schema_command.mutations:
            if schema_mutation.get_schema_reference().version == '':
                self.connection.run_schema_mutation(schema_mutation)
                continue

            if not isinstance(schema_mutation, glue.DeleteSchema) and issubclass(
                type(schema_mutation),
                glue.ChangeSchema,
            ):
                _type = glue.ChangeSchema
            else:
                _type = type(schema_mutation)

            grouped[(schema_mutation.get_schema_name(), _type)].append(schema_mutation)

        # transform
        register_mutation: glue.RegisterSchema
        for (_schema_name, _mutation_type), _mutations in grouped.items():
            if _mutation_type is glue.ChangeSchema:
                register_mutation, old_schema_reference = self._transform_change_mutations_to_register(
                    _mutations,  # type: ignore[arg-type]
                )
                result.append(register_mutation)
                data_transfer.append((old_schema_reference, register_mutation.get_schema_reference()))
                continue

            if _mutation_type is glue.DeleteSchema:
                # We don't need to touch the schema in Lakehouse for DeleteSchema mutations
                continue
            else:
                self._check_single_mutation(_mutations)

                register_mutation = _mutations[0]  # type: ignore[assignment]
                register_mutation = self._exclude_unique_constraints(register_mutation)
                register_mutation = self._adjust_pk_constraints(register_mutation)
                register_mutation = self._adjust_fk_constraints(register_mutation)
                _mutation = self._adjust_to_historical_properties(register_mutation)

                result.append(_mutation)
        return result, data_transfer

    def _execute_mutation(
        self,
        mutation: glue.RegisterSchema,
    ) -> list[glue.Schema | None]:
        result: list[glue.Schema | None] = []
        reference = mutation.get_schema_reference()
        _mutation = copy(mutation)
        _new_table_version = get_identifier()

        if not reference.metadata or META_CLASS_NAME not in reference.metadata:
            msg = f'Missing metadata.__class_name__ in schema reference: {reference}. Mutation: {_mutation}'
            raise ValueError(msg)

        self.historical_table_schema.register_table_schema_version(
            table_name=reference.name,
            table_version=_new_table_version,
            schema_name=reference.metadata[META_CLASS_NAME],
            schema_version=reference.version,
        )

        _mutation.schema.name = format_historical_table_name(
            reference.name,
            _new_table_version,
        )
        self.connection.run_schema_mutation(_mutation)
        result.append(mutation.schema)

        return result

    def _transform_change_mutations_to_register(
        self,
        mutations: list[glue.ChangeSchema],
    ) -> tuple[glue.RegisterSchema, glue.SchemaReference]:
        _mutation = mutations[0]
        _old_schema_reference = _mutation.get_schema_reference()
        _existing_schema = self._get_existing_schema(
            schema_name=_old_schema_reference.name,
            schema_version=_old_schema_reference.version,
        )
        _schema = copy(_existing_schema)

        if _existing_schema.version:
            _schema.version = (_old_schema_reference.metadata or {})[META_NEW_CLASS_VERSION]

        _schema.metadata = _old_schema_reference.metadata

        for _mutation in mutations:
            if isinstance(_mutation, glue.RenameSchema):
                _schema.name = _mutation.new_schema_name
            elif isinstance(_mutation, glue.AddProperty):
                _schema.properties.append(_mutation.property)
            elif isinstance(_mutation, glue.DeleteProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.property_name:
                        del _schema.properties[_index]
                        break
            elif isinstance(_mutation, glue.RenameProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.old_name:
                        _property.name = _mutation.new_name
                        break
            elif isinstance(_mutation, glue.UpdateProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.property.name:
                        _schema.properties[_index] = _mutation.property
                        break
            elif isinstance(_mutation, glue.AddConstraint):
                if not _schema.constraints:
                    _schema.constraints = []

                _schema.constraints.append(_mutation.constraint)
            elif isinstance(_mutation, glue.DeleteConstraint):
                for _index, _constraint in enumerate(_schema.constraints or []):
                    if _constraint.name == _mutation.constraint_name:
                        if _schema.constraints:
                            del _schema.constraints[_index]
                        break
            elif isinstance(_mutation, glue.AddIndex):
                if not _schema.indexes:
                    _schema.indexes = []
                _schema.indexes.append(_mutation.index)
            elif isinstance(_mutation, glue.DeleteIndex):
                for _idx, _item in enumerate(_schema.indexes or []):
                    if _item.name == _mutation.index_name:
                        if _schema.indexes:
                            del _schema.indexes[_idx]
                        break
            else:
                msg = f'Unsupported mutation type: {type(_mutation)}'
                raise ValueError(msg)

        _create_mutation = glue.RegisterSchema(schema=_schema)
        _create_mutation = self._exclude_unique_constraints(_create_mutation)
        _create_mutation = self._adjust_pk_constraints(_create_mutation)
        _create_mutation = self._adjust_fk_constraints(_create_mutation)
        _create_mutation = self._adjust_to_historical_properties(_create_mutation)

        return _create_mutation, _old_schema_reference

    def _get_existing_schema(
        self,
        schema_name: str,
        schema_version: glue.Version | Versions | str = glue.Version.LATEST,
    ) -> glue.Schema:
        if isinstance(schema_version, glue.Version | Versions):
            if schema_version in (glue.Version.LATEST, Versions.LATEST):
                schema_version = self.schema_version_manager.get_latest_schema_version(schema_name)
            else:
                msg = f'Unsupported schema version: {schema_version}.'
                raise ValueError(msg)

        elif (schema_name, schema_version) in self._schemas_cache:
            return self._schemas_cache[(schema_name, schema_version)]

        _table_version = self.historical_table_schema.find_table_version(
            class_version=schema_version,
            table_name=schema_name,
        )
        _existing_schemas = self.connection.query_schema(
            filters=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                            table_name=SCHEMA_REGISTRY_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(f'{schema_name}{TABLE_NAME_VERSION_SEPARATOR}{_table_version}'),
                ),
            ),
        )

        if len(_existing_schemas) != 1:
            msg = (
                f'SchemaCommandExecutor._get_existing_schema failed: Expected 1 schema, got {len(_existing_schemas)}: '
                f'{schema_name}{TABLE_NAME_VERSION_SEPARATOR}{schema_version}'
            )
            raise ValueError(msg)

        _schema = _existing_schemas[0]

        # normalize PK
        for constraint in _schema.constraints or []:
            if not isinstance(constraint, glue.PrimaryKeyConstraint):
                continue

            constraint.fields = [field for field in constraint.fields if field != SECONDARY_PARTITION_KEY]

            if '_x_' in constraint.name:
                constraint.name = constraint.name.split('_x_', 1)[0]

        _schema = BaseTableSchemasManager.enrich_schema_metadata(_existing_schemas[0])
        self._schemas_cache[(schema_name, _schema.version)] = _schema

        return _schema

    def _transfer_data(self, old_schema_ref: glue.SchemaReference, new_schema_ref: glue.SchemaReference) -> None:
        # Iterate over the old data (paginated for efficiency), including only last version data and not deleted
        # Validate and transform the data to match the new schema (including type conversions).
        # Insert the transformed data into the new schema
        _new_schema = self._get_existing_schema(
            schema_name=new_schema_ref.name,
            schema_version=new_schema_ref.version,
        )
        _offset = 0

        while True:
            query = build_simple_query_statement_with_metadata(
                table=old_schema_ref,
                where=glue.Conditions(
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
                ),
                limit=glue.LimitQuery(
                    limit=self.DATA_TRANSFORM_BATCH_SIZE,
                    offset=_offset,
                ),
            )

            batch_data = self.connection.query(query)

            if not batch_data:
                break

            transformed_data: list[glue.Data] = []

            for item in batch_data:
                try:
                    _data = validate_data_by_schema(item.data, _new_schema)
                except ValidationError as err:
                    msg = f'Unable to transfer data during schema migration. Error: {err}'
                    raise AmsdalError(msg) from err

                # Generate a new version
                _data[SECONDARY_PARTITION_KEY] = get_identifier()

                # Copy Metadata from the old data. It will be updated on the connection level.
                _data[METADATA_KEY] = item.data[METADATA_KEY]

                transformed_data.append(
                    glue.Data(
                        data=_data,
                        metadata=old_schema_ref.metadata,
                    ),
                )

            if transformed_data:
                # Execute mutations via Historical Connection to transfer target data
                records = self.connection.run_mutations(
                    [
                        glue.UpdateData(
                            schema=new_schema_ref,
                            data=_data,
                        )
                        for _data in transformed_data
                    ]
                )

                # Execute mutations via Historical Connection to create M2M records
                _m2m_inserts: list[DataMutation] = []

                for _record in records:
                    for _record_item in _record or []:
                        _m2m_inserts.extend(self._fetch_and_generate_m2m_inserts(new_schema_ref, _record_item))

                self.connection.run_mutations(_m2m_inserts)

            # Move to next batch
            _offset += self.DATA_TRANSFORM_BATCH_SIZE
            if len(batch_data) < self.DATA_TRANSFORM_BATCH_SIZE:
                break

    def _fetch_and_generate_m2m_inserts(
        self,
        new_schema_ref: glue.SchemaReference,
        data: glue.Data,
    ) -> list[glue.InsertData]:
        insert_data_mutations = []
        # Find referenced by via Reference table
        current_metadata = Metadata(**data.data[METADATA_KEY])

        try:
            current_metadata.object_id = json.loads(current_metadata.object_id)
        except Exception:
            ...

        # Create Metadata for prev version of object
        prev_metadata = Metadata(
            object_id=current_metadata.object_id,
            object_version=current_metadata.prior_version,
            _next_version=current_metadata.object_version,
            class_schema_reference=current_metadata.class_schema_reference,
        )
        existing_references = prev_metadata.referenced_by

        if not existing_references:
            return []

        # Group existing_references by (class_name, class_version)
        grouped_references = defaultdict(list)

        for reference in existing_references:
            # Create a tuple key with class_name and class_version
            key = (reference.ref.class_name, reference.ref.class_version)

            # Add reference to the appropriate group (no need to check if key exists)
            grouped_references[key].append(reference)

        _conditions = []
        for class_name, class_version in grouped_references:
            # get class schema
            _conditions.append(
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name='name'),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(class_name),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name='version'),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(class_version),
                    ),
                ),
            )

        table_schemas = {
            (table_schema.name, table_schema.version): table_schema
            for table_schema in self.connection.query_schema(
                filters=glue.Conditions(*_conditions, connector=glue.FilterConnector.OR),
            )
        }

        for (table_name, class_version), references in grouped_references.items():
            table_schema = table_schemas[(table_name, class_version)]
            resolved_class_name = self.historical_table_schema.find_class_name(
                table_name=table_name,
                class_version=class_version,
            )
            pk_constraint = next(
                constraint
                for constraint in (table_schema.constraints or [])
                if isinstance(constraint, glue.PrimaryKeyConstraint)
            )
            pk_fields = [field for field in pk_constraint.fields if field != SECONDARY_PARTITION_KEY]
            ref_by_reference = glue.SchemaReference(
                name=table_name,
                version=class_version,
                metadata={META_CLASS_NAME: resolved_class_name},
            )

            for _ref in references:
                _object_id = _ref.ref.object_id

                if not isinstance(_object_id, list):
                    _object_id = [_object_id]

                _ref_conditions = [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=pk),
                                table_name=ref_by_reference.name,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(_object_id[idx]),
                    )
                    for idx, pk in enumerate(pk_fields)
                ]

                _ref_conditions.append(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SECONDARY_PARTITION_KEY),
                                table_name=ref_by_reference.name,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(_ref.ref.object_version),
                    ),
                )

                _ref_by_data = self.connection.query(
                    glue.QueryStatement(
                        table=ref_by_reference,
                        where=glue.Conditions(*_ref_conditions),
                        limit=glue.LimitQuery(
                            limit=1,
                        ),
                    ),
                )
                _ref_by_data_item = _ref_by_data[0] if _ref_by_data else None

                if not _ref_by_data_item:
                    msg = f'Cannot find referenced object by conditions: {_ref}.'
                    raise RuntimeError(msg)

                _target_id = current_metadata.object_id

                if len(current_metadata.object_id) == 1:
                    _target_id = _target_id[0]

                # Update ref to target data
                _data = _ref_by_data_item.data
                _found = self.adjust_references_in_data(
                    _data,
                    target_class_name=new_schema_ref.name,
                    target_object_id=_target_id,
                    target_object_version=current_metadata.prior_version,  # type: ignore[arg-type]
                    replace_object_version=current_metadata.object_version,
                    replace_class_version=new_schema_ref.version,
                )

                if not _found:
                    msg = (
                        f'Cannot find target object reference in the existing data. '
                        f'Data: {_data}. '
                        f'Object: {current_metadata.model_dump()}'
                    )
                    raise RuntimeError(msg)

                # del object version
                del _data[SECONDARY_PARTITION_KEY]

                insert_data_mutations.append(
                    glue.InsertData(
                        schema=ref_by_reference,
                        data=[
                            glue.Data(
                                data=_data,
                                metadata={
                                    META_PRIMARY_KEY_FIELDS: dict.fromkeys(pk_fields, Any),
                                },
                            ),
                        ],
                    ),
                )
        return insert_data_mutations


class AsyncSchemaCommandExecutor(_BaseSchemaCommandExecutor):
    def __init__(
        self,
        connection: Union['AsyncSqliteHistoricalConnection', 'AsyncPostgresHistoricalConnection'],
        schema_command: glue.SchemaCommand,
        historical_table_schema: AsyncHistoricalTableSchema | None = None,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.schema_command = copy(schema_command)
        self.schema_version_manager = AsyncHistoricalSchemaVersionManager()
        self._historical_table_schema = historical_table_schema

    @property
    def historical_table_schema(self) -> AsyncHistoricalTableSchema:
        if self._historical_table_schema is None:
            msg = 'Historical table schema is not set.'
            raise ValueError(msg)

        return self._historical_table_schema

    async def execute(self) -> list[glue.Schema | None]:
        result: list[glue.Schema | None] = []
        items, data_transfer = await self._transform_mutations()

        for _mutation in items:
            _result = await self._execute_mutation(_mutation)  # type: ignore[arg-type]
            result.extend(_result)

        for old_schema_ref, new_schema_ref in data_transfer:
            await self._transfer_data(old_schema_ref, new_schema_ref)

        return result

    async def _transform_mutations(
        self,
    ) -> tuple[
        list[glue.RegisterSchema | glue.DeleteSchema],
        list[tuple[glue.SchemaReference, glue.SchemaReference]],
    ]:
        result: list[glue.RegisterSchema | glue.DeleteSchema] = []
        data_transfer: list[tuple[glue.SchemaReference, glue.SchemaReference]] = []
        # group by schema name and type
        grouped: dict[tuple[str, type[glue.SchemaMutation]], list[glue.SchemaMutation]] = defaultdict(list)

        _type: type[glue.SchemaMutation]

        for schema_mutation in self.schema_command.mutations:
            if schema_mutation.get_schema_reference().version == '':
                await self.connection.run_schema_mutation(schema_mutation)
                continue

            if not isinstance(schema_mutation, glue.DeleteSchema) and issubclass(
                type(schema_mutation),
                glue.ChangeSchema,
            ):
                _type = glue.ChangeSchema
            else:
                _type = type(schema_mutation)

            grouped[(schema_mutation.get_schema_name(), _type)].append(schema_mutation)

        # transform
        register_mutation: glue.RegisterSchema
        for (_schema_name, _mutation_type), _mutations in grouped.items():
            if _mutation_type is glue.ChangeSchema:
                register_mutation, old_schema_reference = await self._transform_change_mutations_to_register(
                    _mutations,  # type: ignore[arg-type]
                )
                result.append(register_mutation)
                data_transfer.append((old_schema_reference, register_mutation.get_schema_reference()))
                continue

            if _mutation_type is glue.DeleteSchema:
                # We don't need to touch the schema in Lakehouse for DeleteSchema mutations
                continue
            else:
                self._check_single_mutation(_mutations)

                register_mutation = _mutations[0]  # type: ignore[assignment]
                register_mutation = self._exclude_unique_constraints(register_mutation)
                register_mutation = self._adjust_pk_constraints(register_mutation)
                register_mutation = self._adjust_fk_constraints(register_mutation)
                _mutation = self._adjust_to_historical_properties(register_mutation)

                result.append(_mutation)
        return result, data_transfer

    async def _execute_mutation(
        self,
        mutation: glue.RegisterSchema,
    ) -> list[glue.Schema | None]:
        result: list[glue.Schema | None] = []
        reference = mutation.get_schema_reference()
        _mutation = copy(mutation)
        _new_table_version = get_identifier()

        if not reference.metadata or META_CLASS_NAME not in reference.metadata:
            msg = f'Missing metadata.__class_name__ in schema reference: {reference}. Mutation: {_mutation}'
            raise ValueError(msg)

        await self.historical_table_schema.register_table_schema_version(
            table_name=reference.name,
            table_version=_new_table_version,
            schema_name=reference.metadata[META_CLASS_NAME],
            schema_version=reference.version,
        )

        _mutation.schema.name = format_historical_table_name(
            reference.name,
            _new_table_version,
        )
        await self.connection.run_schema_mutation(_mutation)
        result.append(mutation.schema)

        return result

    async def _transform_change_mutations_to_register(
        self,
        mutations: list[glue.ChangeSchema],
    ) -> tuple[glue.RegisterSchema, glue.SchemaReference]:
        _mutation = mutations[0]
        _old_schema_reference = _mutation.get_schema_reference()
        _existing_schema = await self._get_existing_schema(
            schema_name=_old_schema_reference.name,
            schema_version=_old_schema_reference.version,
        )
        _schema = copy(_existing_schema)

        if _existing_schema.version:
            _schema.version = (_old_schema_reference.metadata or {})[META_NEW_CLASS_VERSION]

        _schema.metadata = _old_schema_reference.metadata

        for _mutation in mutations:
            if isinstance(_mutation, glue.RenameSchema):
                _schema.name = _mutation.new_schema_name
            elif isinstance(_mutation, glue.AddProperty):
                _schema.properties.append(_mutation.property)
            elif isinstance(_mutation, glue.DeleteProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.property_name:
                        del _schema.properties[_index]
                        break
            elif isinstance(_mutation, glue.RenameProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.old_name:
                        _property.name = _mutation.new_name
                        break
            elif isinstance(_mutation, glue.UpdateProperty):
                for _index, _property in enumerate(_schema.properties):
                    if _property.name == _mutation.property.name:
                        _schema.properties[_index] = _mutation.property
                        break
            elif isinstance(_mutation, glue.AddConstraint):
                if not _schema.constraints:
                    _schema.constraints = []

                _schema.constraints.append(_mutation.constraint)
            elif isinstance(_mutation, glue.DeleteConstraint):
                for _index, _constraint in enumerate(_schema.constraints or []):
                    if _constraint.name == _mutation.constraint_name:
                        if _schema.constraints:
                            del _schema.constraints[_index]
                        break
            elif isinstance(_mutation, glue.AddIndex):
                if not _schema.indexes:
                    _schema.indexes = []
                _schema.indexes.append(_mutation.index)
            elif isinstance(_mutation, glue.DeleteIndex):
                for _idx, _item in enumerate(_schema.indexes or []):
                    if _item.name == _mutation.index_name:
                        if _schema.indexes:
                            del _schema.indexes[_idx]
                        break
            else:
                msg = f'Unsupported mutation type: {type(_mutation)}'
                raise ValueError(msg)

        _create_mutation = glue.RegisterSchema(schema=_schema)
        _create_mutation = self._exclude_unique_constraints(_create_mutation)
        _create_mutation = self._adjust_pk_constraints(_create_mutation)
        _create_mutation = self._adjust_fk_constraints(_create_mutation)
        _create_mutation = self._adjust_to_historical_properties(_create_mutation)

        return _create_mutation, _old_schema_reference

    async def _get_existing_schema(
        self,
        schema_name: str,
        schema_version: glue.Version | Versions | str = glue.Version.LATEST,
    ) -> glue.Schema:
        if isinstance(schema_version, glue.Version | Versions):
            if schema_version in (glue.Version.LATEST, Versions.LATEST):
                schema_version = await self.schema_version_manager.get_latest_schema_version(schema_name)
            else:
                msg = f'Unsupported schema version: {schema_version}.'
                raise ValueError(msg)

        elif (schema_name, schema_version) in self._schemas_cache:
            return self._schemas_cache[(schema_name, schema_version)]

        _table_version = await self.historical_table_schema.find_table_version(
            class_version=schema_version,
            table_name=schema_name,
        )
        _existing_schemas = await self.connection.query_schema(
            filters=glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=SCHEMA_TABLE_NAME_FIELD),
                            table_name=SCHEMA_REGISTRY_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(f'{schema_name}{TABLE_NAME_VERSION_SEPARATOR}{_table_version}'),
                ),
            ),
        )

        if len(_existing_schemas) != 1:
            msg = f'SchemaCommandExecutor._get_existing_schema failed: Expected 1 schema, got {len(_existing_schemas)}'
            raise ValueError(msg)

        _schema = _existing_schemas[0]

        # normalize PK
        for constraint in _schema.constraints or []:
            if not isinstance(constraint, glue.PrimaryKeyConstraint):
                continue

            constraint.fields = [field for field in constraint.fields if field != SECONDARY_PARTITION_KEY]

            if '_x_' in constraint.name:
                constraint.name = constraint.name.split('_x_', 1)[0]

        _schema = BaseTableSchemasManager.enrich_schema_metadata(_existing_schemas[0])
        self._schemas_cache[(schema_name, _schema.version)] = _schema

        return _schema

    async def _transfer_data(self, old_schema_ref: glue.SchemaReference, new_schema_ref: glue.SchemaReference) -> None:
        # Iterate over the old data (paginated for efficiency), including only last version data and not deleted
        # Validate and transform the data to match the new schema (including type conversions).
        # Insert the transformed data into the new schema
        _new_schema = await self._get_existing_schema(
            schema_name=new_schema_ref.name,
            schema_version=new_schema_ref.version,
        )
        _offset = 0

        while True:
            query = build_simple_query_statement_with_metadata(
                table=old_schema_ref,
                where=glue.Conditions(
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
                ),
                limit=glue.LimitQuery(
                    limit=self.DATA_TRANSFORM_BATCH_SIZE,
                    offset=_offset,
                ),
            )

            batch_data = await self.connection.query(query)

            if not batch_data:
                break

            transformed_data: list[glue.Data] = []

            for item in batch_data:
                try:
                    _data = validate_data_by_schema(item.data, _new_schema)
                except ValidationError as err:
                    msg = f'Unable to transfer data during schema migration. Error: {err}'
                    raise AmsdalError(msg) from err

                # Generate a new version
                _data[SECONDARY_PARTITION_KEY] = get_identifier()

                # Copy Metadata from the old data. It will be updated on the connection level.
                _data[METADATA_KEY] = item.data[METADATA_KEY]

                transformed_data.append(
                    glue.Data(
                        data=_data,
                        metadata=old_schema_ref.metadata,
                    ),
                )

            if transformed_data:
                # Execute mutations via Historical Connection to transfer target data
                records = await self.connection.run_mutations(
                    [
                        glue.UpdateData(
                            schema=new_schema_ref,
                            data=_data,
                        )
                        for _data in transformed_data
                    ]
                )

                # Execute mutations via Historical Connection to create M2M records
                _m2m_inserts: list[DataMutation] = []

                for _record in records:
                    for _record_item in _record or []:
                        _m2m_inserts.extend(await self._fetch_and_generate_m2m_inserts(new_schema_ref, _record_item))

                await self.connection.run_mutations(_m2m_inserts)

            # Move to next batch
            _offset += self.DATA_TRANSFORM_BATCH_SIZE
            if len(batch_data) < self.DATA_TRANSFORM_BATCH_SIZE:
                break

    async def _fetch_and_generate_m2m_inserts(
        self,
        new_schema_ref: glue.SchemaReference,
        data: glue.Data,
    ) -> list[glue.InsertData]:
        insert_data_mutations = []
        # Find referenced by via Reference table
        current_metadata = Metadata(**data.data[METADATA_KEY])

        try:
            current_metadata.object_id = json.loads(current_metadata.object_id)
        except Exception:
            ...

        # Create Metadata for prev version of object
        prev_metadata = Metadata(
            object_id=current_metadata.object_id,
            object_version=current_metadata.prior_version,
            _next_version=current_metadata.object_version,
            class_schema_reference=current_metadata.class_schema_reference,
        )

        existing_references = await AsyncMetadataInfoQuery.get_referenced_by(prev_metadata)

        if not existing_references:
            return []

        # Group existing_references by (class_name, class_version)
        grouped_references = defaultdict(list)

        for reference in existing_references:
            # Create a tuple key with class_name and class_version
            key = (reference.ref.class_name, reference.ref.class_version)

            # Add reference to the appropriate group (no need to check if key exists)
            grouped_references[key].append(reference)

        _conditions = []
        for class_name, class_version in grouped_references:
            # get class schema
            _conditions.append(
                glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name='name'),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(class_name),
                    ),
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name='version'),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(class_version),
                    ),
                ),
            )

        table_schemas = {
            (table_schema.name, table_schema.version): table_schema
            for table_schema in await self.connection.query_schema(
                filters=glue.Conditions(*_conditions, connector=glue.FilterConnector.OR),
            )
        }

        for (table_name, class_version), references in grouped_references.items():
            table_schema = table_schemas[(table_name, class_version)]
            resolved_class_name = await self.historical_table_schema.find_class_name(
                table_name=table_name,
                class_version=class_version,
            )
            pk_constraint = next(
                constraint
                for constraint in (table_schema.constraints or [])
                if isinstance(constraint, glue.PrimaryKeyConstraint)
            )
            pk_fields = [field for field in pk_constraint.fields if field != SECONDARY_PARTITION_KEY]
            ref_by_reference = glue.SchemaReference(
                name=table_name,
                version=class_version,
                metadata={META_CLASS_NAME: resolved_class_name},
            )

            for _ref in references:
                _object_id = _ref.ref.object_id

                if not isinstance(_object_id, list):
                    _object_id = [_object_id]

                _ref_conditions = [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=pk),
                                table_name=ref_by_reference.name,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(_object_id[idx]),
                    )
                    for idx, pk in enumerate(pk_fields)
                ]

                _ref_conditions.append(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SECONDARY_PARTITION_KEY),
                                table_name=ref_by_reference.name,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(_ref.ref.object_version),
                    ),
                )

                _ref_by_data = await self.connection.query(
                    glue.QueryStatement(
                        table=ref_by_reference,
                        where=glue.Conditions(*_ref_conditions),
                        limit=glue.LimitQuery(
                            limit=1,
                        ),
                    ),
                )
                _ref_by_data_item = _ref_by_data[0] if _ref_by_data else None

                if not _ref_by_data_item:
                    msg = f'Cannot find referenced object by conditions: {_ref}.'
                    raise RuntimeError(msg)

                _target_id = current_metadata.object_id

                if len(current_metadata.object_id) == 1:
                    _target_id = _target_id[0]

                # Update ref to target data
                _data = _ref_by_data_item.data
                _found = self.adjust_references_in_data(
                    _data,
                    target_class_name=new_schema_ref.name,
                    target_object_id=_target_id,
                    target_object_version=current_metadata.prior_version,  # type: ignore[arg-type]
                    replace_object_version=current_metadata.object_version,
                    replace_class_version=new_schema_ref.version,
                )

                if not _found:
                    msg = (
                        f'Cannot find target object reference in the existing data. '
                        f'Data: {_data}. '
                        f'Object: {current_metadata.model_dump()}'
                    )
                    raise RuntimeError(msg)

                # del object version
                del _data[SECONDARY_PARTITION_KEY]

                insert_data_mutations.append(
                    glue.InsertData(
                        schema=ref_by_reference,
                        data=[
                            glue.Data(
                                data=_data,
                                metadata={
                                    META_PRIMARY_KEY_FIELDS: dict.fromkeys(pk_fields, Any),
                                },
                            ),
                        ],
                    ),
                )
        return insert_data_mutations
