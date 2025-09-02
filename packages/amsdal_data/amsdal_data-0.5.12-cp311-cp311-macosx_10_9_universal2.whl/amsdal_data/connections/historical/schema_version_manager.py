from collections import defaultdict
from typing import Any
from typing import TypeAlias

import amsdal_glue as glue
from amsdal_utils.models.enums import ModuleType
from amsdal_utils.models.enums import Versions
from amsdal_utils.utils.singleton import Singleton

from amsdal_data.connections.constants import CLASS_OBJECT
from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import OBJECT_TABLE
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata
from amsdal_data.errors import QueryError

SchemaNameType: TypeAlias = str
SchemaVersionType: TypeAlias = str | glue.Version
PropertyNameType: TypeAlias = str
PropertyType: TypeAlias = Any

PROPERTIES_FIELD = 'properties'
STORAGE_METADATA_FIELD = 'storage_metadata'
PRIMARY_KEY_FIELD = 'primary_key'
PROPERTIES_TYPE_FIELD = 'type'


class HistoricalSchemaVersionManager(metaclass=Singleton):
    def __init__(self) -> None:
        self._cache_scheme_types: dict[SchemaNameType, ModuleType] = {}
        self._cache_last_versions: dict[SchemaNameType, SchemaVersionType] = {}
        self._cache_object_classes: list[dict[SchemaNameType, Any]] = []
        self._cache_class_properties: dict[
            SchemaNameType,
            dict[
                SchemaVersionType,
                dict[
                    PropertyNameType,
                    PropertyType,
                ],
            ],
        ] = defaultdict(dict)
        self._get_all_schema_versions: dict[SchemaNameType, list[SchemaVersionType]] = {}

    @property
    def object_classes(self) -> list[dict[str, Any]]:
        if not self._cache_object_classes:
            _searched_data = self._search_classes(OBJECT_TABLE) or []
            self._cache_object_classes = [_data.data for _data in _searched_data]

            for _object_class in _searched_data:
                _cached_class = self._cache_class_properties[_object_class.data[PRIMARY_PARTITION_KEY]]
                _cached_class[_object_class.data[SECONDARY_PARTITION_KEY]] = {
                    prop_name: prop[PROPERTIES_TYPE_FIELD]
                    for prop_name, prop in _object_class.data[PROPERTIES_FIELD].items()
                }

        return self._cache_object_classes

    @property
    def class_object_classes(self) -> list[dict[str, Any]]:
        return [
            object_class for object_class in self.object_classes if object_class[PRIMARY_PARTITION_KEY] == CLASS_OBJECT
        ]

    def register_object_class(self, item: dict[str, Any]) -> None:
        self._cache_object_classes.append(item)

    def register_last_version(self, schema_name: str, schema_version: str) -> None:
        self._cache_last_versions[schema_name] = schema_version

    def get_all_schema_properties(
        self,
        schema_name: str,
    ) -> dict[SchemaVersionType, dict[PropertyNameType, PropertyType]]:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            msg = f'The schema name "{schema_name}" is not versioned.'
            raise ValueError(msg)

        if schema_name not in self._cache_class_properties:
            self.get_all_schema_versions(schema_name)

        return self._cache_class_properties[schema_name]

    def get_all_schema_versions(self, schema_name: str) -> list[str]:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return []

        # search in object table
        data = [
            item[SECONDARY_PARTITION_KEY] for item in self.object_classes if item[PRIMARY_PARTITION_KEY] == schema_name
        ]

        if data:
            return data

        result = []

        if schema_name in self._get_all_schema_versions:
            return self._get_all_schema_versions[schema_name]

        for class_object in self.class_object_classes:
            _data = self._search_classes(
                table_name=class_object[PRIMARY_PARTITION_KEY],
                table_version=class_object[SECONDARY_PARTITION_KEY],
                where=glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                table_name=class_object[PRIMARY_PARTITION_KEY],
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(schema_name),
                    ),
                ),
            )

            if _data:
                result.extend([item.data[SECONDARY_PARTITION_KEY] for item in _data])

                for _schema in _data:
                    _cached_class = self._cache_class_properties[schema_name]
                    _props = _schema.data.get(PROPERTIES_FIELD, {})
                    _storage_metadata = _schema.data.get(STORAGE_METADATA_FIELD) or {}
                    _pks = _storage_metadata.get(PRIMARY_KEY_FIELD) or [PRIMARY_PARTITION_KEY]

                    for _pk in _pks:
                        if _pk not in _props:
                            # if primary key is not in properties, it's our "partition_key"
                            _props[_pk] = {'type': 'string'}

                    _cached_class[_schema.data[SECONDARY_PARTITION_KEY]] = {
                        prop_name: prop[PROPERTIES_TYPE_FIELD] for prop_name, prop in _props.items()
                    }
        self._get_all_schema_versions[schema_name] = result

        return result

    def get_latest_schema_version(
        self,
        schema_name: str,
        *,
        from_cache_only: bool = False,
    ) -> str | glue.Version | Versions:
        from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
        from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD

        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return ''

        if schema_name not in self._cache_last_versions:
            if from_cache_only:
                return glue.Version.LATEST

            # search in object table
            data = self.find_object_class(schema_name, glue.Version.LATEST)

            if data:
                # try to find core class
                self._cache_last_versions[schema_name] = data[SECONDARY_PARTITION_KEY]
            else:
                # try to find user class object
                for class_object in self.class_object_classes:
                    _data = self._search_classes(
                        table_name=class_object[PRIMARY_PARTITION_KEY],
                        table_version=class_object[SECONDARY_PARTITION_KEY],
                        only=[
                            glue.FieldReference(
                                field=glue.Field(name=SECONDARY_PARTITION_KEY),
                                table_name=class_object[PRIMARY_PARTITION_KEY],
                            ),
                        ],
                        where=glue.Conditions(
                            glue.Condition(
                                left=glue.FieldReferenceExpression(
                                    field_reference=glue.FieldReference(
                                        field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                        table_name=class_object[PRIMARY_PARTITION_KEY],
                                    ),
                                ),
                                lookup=glue.FieldLookup.EQ,
                                right=glue.Value(schema_name),
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
                        limit=glue.LimitQuery(limit=1),
                    )

                    if _data:
                        item = _data[0]
                        self._cache_last_versions[schema_name] = item.data[SECONDARY_PARTITION_KEY]

                        break

        if schema_name not in self._cache_last_versions:
            self._cache_last_versions[schema_name] = glue.Version.LATEST

        return self._cache_last_versions[schema_name]

    def find_object_class(
        self,
        schema_name: str,
        schema_version: str | glue.Version = glue.Version.LATEST,
    ) -> dict[str, Any] | None:
        from amsdal_data.connections.historical.data_query_transform import METADATA_FIELD

        for object_class in self.object_classes:
            if object_class[PRIMARY_PARTITION_KEY] == schema_name:
                if schema_version == glue.Version.LATEST:
                    if not object_class[METADATA_FIELD]['_next_version']:
                        return object_class
                    continue

                if object_class[SECONDARY_PARTITION_KEY] == schema_version:
                    return object_class
        return None

    def resolve_schema_type(self, schema_name: str) -> ModuleType:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return ModuleType.CORE

        if schema_name not in self._cache_scheme_types:
            # search in object table
            data = next(
                iter(
                    item.get('schema_type', ModuleType.CORE)
                    for item in self.object_classes
                    if item[PRIMARY_PARTITION_KEY] == schema_name
                ),
                None,
            )

            if data:
                self._cache_scheme_types[schema_name] = data
            else:
                self._cache_scheme_types[schema_name] = ModuleType.CORE

        return self._cache_scheme_types[schema_name]

    def clear_versions(self) -> None:
        self._cache_scheme_types.clear()
        self._cache_last_versions.clear()
        self._cache_object_classes.clear()
        self._cache_class_properties.clear()

    def _search_classes(
        self,
        table_name: str,
        table_version: str | glue.Version = glue.Version.LATEST,
        only: list[glue.FieldReference] | None = None,
        where: glue.Conditions | None = None,
        limit: glue.LimitQuery | None = None,
    ) -> list[glue.Data] | None:
        from amsdal_data.application import DataApplication

        operation_manager = DataApplication().operation_manager
        query = build_simple_query_statement_with_metadata(
            table=glue.SchemaReference(name=table_name, version=table_version),
            only=only,
            where=where,
            limit=limit,
        )
        result = operation_manager.query_lakehouse(query)

        if not result.success:
            msg = f'Failed to search class: {result.message}'
            raise QueryError(msg) from result.exception

        return result.data


class AsyncHistoricalSchemaVersionManager(metaclass=Singleton):
    def __init__(self) -> None:
        self._cache_scheme_types: dict[SchemaNameType, ModuleType] = {}
        self._cache_last_versions: dict[SchemaNameType, SchemaVersionType] = {}
        self._cache_object_classes: list[dict[SchemaNameType, Any]] = []
        self._cache_class_properties: dict[
            SchemaNameType,
            dict[
                SchemaVersionType,
                dict[
                    PropertyNameType,
                    PropertyType,
                ],
            ],
        ] = defaultdict(dict)
        self._get_all_schema_versions: dict[SchemaNameType, list[SchemaVersionType]] = {}

    @property
    async def object_classes(self) -> list[dict[str, Any]]:
        if not self._cache_object_classes:
            _searched_data = await self._search_classes(OBJECT_TABLE) or []
            self._cache_object_classes = [_data.data for _data in _searched_data]

            for _object_class in _searched_data:
                _cached_class = self._cache_class_properties[_object_class.data[PRIMARY_PARTITION_KEY]]
                _cached_class[_object_class.data[SECONDARY_PARTITION_KEY]] = {
                    prop_name: prop[PROPERTIES_TYPE_FIELD]
                    for prop_name, prop in _object_class.data[PROPERTIES_FIELD].items()
                }

        return self._cache_object_classes

    @property
    async def class_object_classes(self) -> list[dict[str, Any]]:
        return [
            object_class
            for object_class in await self.object_classes
            if object_class[PRIMARY_PARTITION_KEY] == CLASS_OBJECT
        ]

    def register_object_class(self, item: dict[str, Any]) -> None:
        self._cache_object_classes.append(item)

    def register_last_version(self, schema_name: str, schema_version: str) -> None:
        self._cache_last_versions[schema_name] = schema_version

    async def get_all_schema_properties(
        self,
        schema_name: str,
    ) -> dict[SchemaVersionType, dict[PropertyNameType, PropertyType]]:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            msg = f'The schema name "{schema_name}" is not versioned.'
            raise ValueError(msg)

        if schema_name not in self._cache_class_properties:
            await self.get_all_schema_versions(schema_name)

        return self._cache_class_properties[schema_name]

    async def get_all_schema_versions(self, schema_name: str) -> list[str]:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return []

        # search in object table
        data = [
            item[SECONDARY_PARTITION_KEY]
            for item in await self.object_classes
            if item[PRIMARY_PARTITION_KEY] == schema_name
        ]

        if data:
            return data

        result = []

        if schema_name in self._get_all_schema_versions:
            return self._get_all_schema_versions[schema_name]

        for class_object in await self.class_object_classes:
            _data = await self._search_classes(
                table_name=class_object[PRIMARY_PARTITION_KEY],
                table_version=class_object[SECONDARY_PARTITION_KEY],
                where=glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                table_name=class_object[PRIMARY_PARTITION_KEY],
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(schema_name),
                    ),
                ),
            )

            if _data:
                result.extend([item.data[SECONDARY_PARTITION_KEY] for item in _data])

                for _schema in _data:
                    _cached_class = self._cache_class_properties[schema_name]
                    _props = _schema.data.get(PROPERTIES_FIELD, {})
                    _storage_metadata = _schema.data.get(STORAGE_METADATA_FIELD) or {}
                    _pks = _storage_metadata.get(PRIMARY_KEY_FIELD) or [PRIMARY_PARTITION_KEY]

                    for _pk in _pks:
                        if _pk not in _props:
                            # if primary key is not in properties, it's our "partition_key"
                            _props[_pk] = {'type': 'string'}

                    _cached_class[_schema.data[SECONDARY_PARTITION_KEY]] = {
                        prop_name: prop[PROPERTIES_TYPE_FIELD] for prop_name, prop in _props.items()
                    }
        self._get_all_schema_versions[schema_name] = result

        return result

    async def get_latest_schema_version(
        self,
        schema_name: str,
        *,
        from_cache_only: bool = False,
    ) -> str | glue.Version | Versions:
        from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
        from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD

        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return ''

        if schema_name not in self._cache_last_versions:
            if from_cache_only:
                return glue.Version.LATEST

            # search in object table
            data = await self.find_object_class(schema_name, glue.Version.LATEST)

            if data:
                # try to find core class
                self._cache_last_versions[schema_name] = data[SECONDARY_PARTITION_KEY]
            else:
                # try to find user class object
                for class_object in await self.class_object_classes:
                    _data = await self._search_classes(
                        table_name=class_object[PRIMARY_PARTITION_KEY],
                        table_version=class_object[SECONDARY_PARTITION_KEY],
                        only=[
                            glue.FieldReference(
                                field=glue.Field(name=SECONDARY_PARTITION_KEY),
                                table_name=class_object[PRIMARY_PARTITION_KEY],
                            ),
                        ],
                        where=glue.Conditions(
                            glue.Condition(
                                left=glue.FieldReferenceExpression(
                                    field_reference=glue.FieldReference(
                                        field=glue.Field(name=PRIMARY_PARTITION_KEY),
                                        table_name=class_object[PRIMARY_PARTITION_KEY],
                                    ),
                                ),
                                lookup=glue.FieldLookup.EQ,
                                right=glue.Value(schema_name),
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
                        limit=glue.LimitQuery(limit=1),
                    )

                    if _data:
                        item = _data[0]
                        self._cache_last_versions[schema_name] = item.data[SECONDARY_PARTITION_KEY]

                        break

        if schema_name not in self._cache_last_versions:
            self._cache_last_versions[schema_name] = glue.Version.LATEST

        return self._cache_last_versions[schema_name]

    async def find_object_class(
        self,
        schema_name: str,
        schema_version: str | glue.Version = glue.Version.LATEST,
    ) -> dict[str, Any] | None:
        from amsdal_data.connections.historical.data_query_transform import METADATA_FIELD

        for object_class in await self.object_classes:
            if object_class[PRIMARY_PARTITION_KEY] == schema_name:
                if schema_version == glue.Version.LATEST:
                    if not object_class[METADATA_FIELD]['_next_version']:
                        return object_class
                    continue

                if object_class[SECONDARY_PARTITION_KEY] == schema_version:
                    return object_class
        return None

    async def resolve_schema_type(self, schema_name: str) -> ModuleType:
        if schema_name in (
            METADATA_TABLE,
            REFERENCE_TABLE,
            TRANSACTION_TABLE,
            OBJECT_TABLE,
        ):
            # these tables are not versioned
            return ModuleType.CORE

        if schema_name not in self._cache_scheme_types:
            # search in object table
            data = next(
                iter(
                    item.get('schema_type', ModuleType.CORE)
                    for item in await self.object_classes
                    if item[PRIMARY_PARTITION_KEY] == schema_name
                ),
                None,
            )

            if data:
                self._cache_scheme_types[schema_name] = data
            else:
                self._cache_scheme_types[schema_name] = ModuleType.CORE

        return self._cache_scheme_types[schema_name]

    def clear_versions(self) -> None:
        self._cache_scheme_types.clear()
        self._cache_last_versions.clear()
        self._cache_object_classes.clear()
        self._cache_class_properties.clear()

    async def _search_classes(
        self,
        table_name: str,
        table_version: str | glue.Version = glue.Version.LATEST,
        only: list[glue.FieldReference] | None = None,
        where: glue.Conditions | None = None,
        limit: glue.LimitQuery | None = None,
    ) -> list[glue.Data] | None:
        from amsdal_data.application import AsyncDataApplication

        operation_manager = AsyncDataApplication().operation_manager

        query = build_simple_query_statement_with_metadata(
            table=glue.SchemaReference(name=table_name, version=table_version),
            only=only,
            where=where,
            limit=limit,
        )
        result = await operation_manager.query_lakehouse(query)

        if not result.success:
            msg = f'Failed to search class: {result.message}'
            raise QueryError(msg) from result.exception

        return result.data
