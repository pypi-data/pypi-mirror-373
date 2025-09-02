from copy import copy

import amsdal_glue as glue
from amsdal_utils.models.enums import Versions

from amsdal_data.connections.constants import SCHEMA_TABLE_NAME_FIELD
from amsdal_data.connections.constants import SCHEMA_VERSION_FIELD
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_data.services.historical_table_schema import AsyncHistoricalTableSchema
from amsdal_data.services.historical_table_schema import HistoricalTableSchema


class BaseQueryFiltersTransform:
    def __init__(self, schema_query_filters: glue.Conditions | None) -> None:
        self.schema_query_filters = copy(schema_query_filters) if schema_query_filters else None


class SchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    def __init__(
        self,
        schema_query_filters: glue.Conditions | None,
        historical_table_schema: HistoricalTableSchema,
    ) -> None:
        super().__init__(schema_query_filters)
        self.schema_version_manager = HistoricalSchemaVersionManager()
        self.historical_table_schema = historical_table_schema

    def transform(self) -> glue.Conditions | None:
        if not self.schema_query_filters:
            return self.schema_query_filters
        return self._transform(self.schema_query_filters)

    def process_data(self, data: list[glue.Schema]) -> list[glue.Schema]:
        """
        We need to extract table version from the full table name and translate it to the class version.
        """
        result = []

        for item in data:
            _item = copy(item)

            if TABLE_NAME_VERSION_SEPARATOR in item.name:
                _name, _table_version = _item.name.split(TABLE_NAME_VERSION_SEPARATOR)
                _item.name = _name
                _item.version = self.historical_table_schema.find_class_version(table_version=_table_version)

            for constraint in _item.constraints or []:
                if isinstance(constraint, glue.PrimaryKeyConstraint):
                    _item.name, _ = _item.name.rsplit('_x_', 1) if '_x_' in _item.name else (_item.name, None)

            result.append(_item)

        return result

    def _transform(self, item: glue.Conditions) -> glue.Conditions:
        """
        AMSDAL operates always with class versions, but in Lakehouse we have table_version.
        So we need to replace class version with table version in the query.
        Also, we need to replace table name with full table name in the query, e.g. users__v__LATEST to
        specific version.
        """
        _conditions: list[glue.Condition | glue.Conditions] = []

        for _condition in item.children:
            if isinstance(_condition, glue.Conditions):
                _conditions.append(self._transform(_condition))
                continue

            if isinstance(_condition.left, glue.FieldReferenceExpression):
                if _condition.left.field_reference.field.name == SCHEMA_VERSION_FIELD:
                    if isinstance(_condition.right, glue.Value):
                        _conditions.append(self._replace_class_version(_condition))
                        continue
                elif _condition.left.field_reference.field.name == SCHEMA_TABLE_NAME_FIELD:
                    if isinstance(_condition.right, glue.Value):
                        _conditions.append(self._normalize_full_table_name(_condition))
                        continue

            if isinstance(_condition.right, glue.FieldReferenceExpression):
                if _condition.right.field_reference.field.name == SCHEMA_VERSION_FIELD:
                    if isinstance(_condition.left, glue.Value):
                        _conditions.append(self._replace_class_version(_condition))
                        continue
                elif _condition.right.field_reference.field.name == SCHEMA_TABLE_NAME_FIELD:
                    if isinstance(_condition.left, glue.Value):
                        _conditions.append(self._normalize_full_table_name(_condition))
                        continue

            _conditions.append(_condition)

        return glue.Conditions(
            *_conditions,
            connector=item.connector,
            negated=item.negated,
        )

    def _replace_class_version(self, condition: glue.Condition) -> glue.Condition:
        if isinstance(condition.left, glue.FieldReferenceExpression):
            _value = condition.right.value  # type: ignore[attr-defined]
        else:
            _value = condition.left.value  # type: ignore[attr-defined]

        if not _value:
            return condition

        if _value in (
            glue.Version.ALL,
            Versions.ALL,
        ):
            # Replace with `True is True`
            condition.left = glue.Value(True)
            condition.lookup = glue.FieldLookup.EQ
            condition.right = glue.Value(True)

            return condition

        if _value in (
            glue.Version.LATEST,
            Versions.LATEST,
        ):
            msg = 'You should not use LATEST in the query schemas. Use specific class version instead.'
            raise ValueError(msg)

        table_version = self.historical_table_schema.find_table_version(_value)

        if isinstance(condition.left, glue.FieldReferenceExpression):
            condition.right.value = table_version  # type: ignore[attr-defined]
        else:
            condition.left.value = table_version  # type: ignore[attr-defined]

        return condition

    def _normalize_full_table_name(self, condition: glue.Condition) -> glue.Condition:
        if isinstance(condition.left, glue.FieldReferenceExpression):
            _value = condition.right.value  # type: ignore[attr-defined]
        else:
            _value = condition.left.value  # type: ignore[attr-defined]

        if TABLE_NAME_VERSION_SEPARATOR not in _value:
            return condition

        _name, _version = _value.split(TABLE_NAME_VERSION_SEPARATOR)

        if _version != glue.Version.LATEST.value:
            return condition

        class_version = self.schema_version_manager.get_latest_schema_version(_name)
        table_version = self.historical_table_schema.find_table_version(class_version)

        _value = f'{_name}{TABLE_NAME_VERSION_SEPARATOR}{table_version}'

        if isinstance(condition.left, glue.FieldReferenceExpression):
            condition.right.value = _value  # type: ignore[attr-defined]
        else:
            condition.left.value = _value  # type: ignore[attr-defined]

        return condition


class AsyncSchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    def __init__(
        self,
        schema_query_filters: glue.Conditions | None,
        historical_table_schema: AsyncHistoricalTableSchema,
    ) -> None:
        super().__init__(schema_query_filters)
        self.schema_version_manager = AsyncHistoricalSchemaVersionManager()
        self.historical_table_schema = historical_table_schema

    async def transform(self) -> glue.Conditions | None:
        if not self.schema_query_filters:
            return self.schema_query_filters
        return await self._transform(self.schema_query_filters)

    async def process_data(self, data: list[glue.Schema]) -> list[glue.Schema]:
        """
        We need to extract table version from the full table name and translate it to the class version.
        """
        result = []

        for item in data:
            _item = copy(item)

            if TABLE_NAME_VERSION_SEPARATOR in item.name:
                _name, _table_version = _item.name.split(TABLE_NAME_VERSION_SEPARATOR)
                _item.name = _name
                _item.version = await self.historical_table_schema.find_class_version(table_version=_table_version)

            for constraint in _item.constraints or []:
                if isinstance(constraint, glue.PrimaryKeyConstraint):
                    _item.name, _ = _item.name.rsplit('_x_', 1) if '_x_' in _item.name else (_item.name, None)

            result.append(_item)

        return result

    async def _transform(self, item: glue.Conditions) -> glue.Conditions:
        """
        AMSDAL operates always with class versions, but in Lakehouse we have table_version.
        So we need to replace class version with table version in the query.
        Also, we need to replace table name with full table name in the query, e.g. users__v__LATEST to
        specific version.
        """
        _conditions: list[glue.Condition | glue.Conditions] = []

        for _condition in item.children:
            if isinstance(_condition, glue.Conditions):
                _conditions.append(await self._transform(_condition))
                continue

            if isinstance(_condition.left, glue.FieldReferenceExpression):
                if _condition.left.field_reference.field.name == SCHEMA_VERSION_FIELD:
                    if isinstance(_condition.right, glue.Value):
                        _conditions.append(await self._replace_class_version(_condition))
                        continue
                elif _condition.left.field_reference.field.name == SCHEMA_TABLE_NAME_FIELD:
                    if isinstance(_condition.right, glue.Value):
                        _conditions.append(await self._normalize_full_table_name(_condition))
                        continue

            if isinstance(_condition.right, glue.FieldReferenceExpression):
                if _condition.right.field_reference.field.name == SCHEMA_VERSION_FIELD:
                    if isinstance(_condition.left, glue.Value):
                        _conditions.append(await self._replace_class_version(_condition))
                        continue
                elif _condition.right.field_reference.field.name == SCHEMA_TABLE_NAME_FIELD:
                    if isinstance(_condition.left, glue.Value):
                        _conditions.append(await self._normalize_full_table_name(_condition))
                        continue

            _conditions.append(_condition)

        return glue.Conditions(
            *_conditions,
            connector=item.connector,
            negated=item.negated,
        )

    async def _replace_class_version(self, condition: glue.Condition) -> glue.Condition:
        if isinstance(condition.left, glue.FieldReferenceExpression):
            _value = condition.right.value  # type: ignore[attr-defined]
        else:
            _value = condition.left.value  # type: ignore[attr-defined]

        if not _value:
            return condition

        if _value in (
            glue.Version.ALL,
            Versions.ALL,
        ):
            # Replace with `True is True`
            condition.left = glue.Value(True)
            condition.lookup = glue.FieldLookup.EQ
            condition.right = glue.Value(True)

            return condition

        if _value in (
            glue.Version.LATEST,
            Versions.LATEST,
        ):
            msg = 'You should not use LATEST in the query schemas. Use specific class version instead.'
            raise ValueError(msg)

        table_version = await self.historical_table_schema.find_table_version(_value)

        if isinstance(condition.left, glue.FieldReferenceExpression):
            condition.right.value = table_version  # type: ignore[attr-defined]
        else:
            condition.left.value = table_version  # type: ignore[attr-defined]

        return condition

    async def _normalize_full_table_name(self, condition: glue.Condition) -> glue.Condition:
        if isinstance(condition.left, glue.FieldReferenceExpression):
            _value = condition.right.value  # type: ignore[attr-defined]
        else:
            _value = condition.left.value  # type: ignore[attr-defined]

        if TABLE_NAME_VERSION_SEPARATOR not in _value:
            return condition

        _name, _version = _value.split(TABLE_NAME_VERSION_SEPARATOR)

        if _version != glue.Version.LATEST.value:
            return condition

        class_version = await self.schema_version_manager.get_latest_schema_version(_name)
        table_version = await self.historical_table_schema.find_table_version(class_version)

        _value = f'{_name}{TABLE_NAME_VERSION_SEPARATOR}{table_version}'

        if isinstance(condition.left, glue.FieldReferenceExpression):
            condition.right.value = _value  # type: ignore[attr-defined]
        else:
            condition.left.value = _value  # type: ignore[attr-defined]

        return condition
