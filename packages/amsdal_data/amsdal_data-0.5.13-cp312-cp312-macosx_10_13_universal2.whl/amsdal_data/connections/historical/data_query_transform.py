from copy import deepcopy
from typing import Any

import amsdal_glue as glue
from amsdal_glue_core.common.expressions.expression import Expression

from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY

OBJECT_ID_FIELD = 'object_id'
OBJECT_VERSION_FIELD = 'object_version'
METADATA_FIELD = '_metadata'
NEXT_VERSION_FIELD = 'next_version'
PK_FIELD_ALIAS_FOR_METADATA = '_pk_for_metadata'

MODEL_TABLE_ALIAS = 't1'
METADATA_TABLE_ALIAS = 't2'

METADATA_SELECT_EXPRESSION = f"""
json_object(
    '_next_version', {METADATA_TABLE_ALIAS}.next_version,
    'object_id', {METADATA_TABLE_ALIAS}.object_id,
    'object_version', {METADATA_TABLE_ALIAS}.object_version,
    'prior_version', {METADATA_TABLE_ALIAS}.prior_version,
    'class_schema_reference', json({METADATA_TABLE_ALIAS}.class_schema_reference),
    'class_meta_schema_reference', json({METADATA_TABLE_ALIAS}.class_meta_schema_reference),
    'is_deleted', {METADATA_TABLE_ALIAS}.is_deleted,
    'created_at', {METADATA_TABLE_ALIAS}.created_at,
    'updated_at', {METADATA_TABLE_ALIAS}.updated_at,
    'transaction', json({METADATA_TABLE_ALIAS}.'transaction')
)
"""
PG_METADATA_SELECT_EXPRESSION = f"""
json_build_object(
    '_next_version', json_agg({METADATA_TABLE_ALIAS}."next_version")->0,
    'object_id', json_agg({METADATA_TABLE_ALIAS}.object_id)->0,
    'object_version', json_agg({METADATA_TABLE_ALIAS}.object_version)->0,
    'prior_version', json_agg({METADATA_TABLE_ALIAS}.prior_version)->0,
    'class_schema_reference', json_agg(to_json({METADATA_TABLE_ALIAS}.class_schema_reference))->0,
    'class_meta_schema_reference', json_agg(to_json({METADATA_TABLE_ALIAS}.class_meta_schema_reference))->0,
    'is_deleted', json_agg({METADATA_TABLE_ALIAS}.is_deleted)->0,
    'created_at', json_agg({METADATA_TABLE_ALIAS}.created_at)->0,
    'updated_at', json_agg({METADATA_TABLE_ALIAS}.updated_at)->0,
    'transaction', json_agg(to_json({METADATA_TABLE_ALIAS}."transaction"))->0
)
"""

DEFAULT_PKS = {'partition_key': str}

META_PRIMARY_KEY_FIELDS = '__primary_key_fields__'
META_PRIMARY_KEY = '__primary_key__'
META_FOREIGN_KEYS = '__foreign_keys__'
META_CLASS_NAME = '__class_name__'
META_NEW_CLASS_VERSION = '__new_class_version__'


class MetadataExpression(glue.RawExpression):
    def __init__(self, output_type: type[Any] | None = None) -> None:
        super().__init__(
            value='<<METADATA_SELECT_EXPRESSION (should be replaced in connection)>>',
            output_type=output_type,
        )


def build_metadata_join_query(table_name: str, metadata: dict[str, Any] | None) -> glue.JoinQuery:
    pks = (metadata or {}).get(META_PRIMARY_KEY) or [PRIMARY_PARTITION_KEY]
    items: list[Expression] = []

    for pk in pks:
        reference_field = glue.Field(name=pk)

        items.append(
            glue.FieldReferenceExpression(
                field_reference=glue.FieldReference(
                    field=reference_field,
                    table_name=table_name,
                ),
            ),
        )

    value_expression = glue.JsonbArrayExpression(items=items)

    return glue.JoinQuery(
        table=glue.SubQueryStatement(
            query=glue.QueryStatement(
                table=glue.SchemaReference(
                    name=METADATA_TABLE,
                    alias='_m',
                    version=glue.Version.LATEST,
                    metadata=metadata,
                ),
                only=[
                    glue.FieldReference(
                        field=glue.Field(name='*'),
                        table_name='_m',
                    ),
                ],
                annotations=[
                    glue.AnnotationQuery(
                        value=glue.SubQueryStatement(
                            query=glue.QueryStatement(
                                only=[
                                    glue.FieldReference(
                                        field=glue.Field(name='object_version'),
                                        table_name='_m2',
                                    ),
                                ],
                                table=glue.SchemaReference(
                                    name=METADATA_TABLE,
                                    version=glue.Version.LATEST,
                                    alias='_m2',
                                ),
                                where=glue.Conditions(
                                    glue.Condition(
                                        left=glue.FieldReferenceExpression(
                                            field_reference=glue.FieldReference(
                                                field=glue.Field(name='object_version'),
                                                table_name='_m',
                                            ),
                                        ),
                                        lookup=glue.FieldLookup.EQ,
                                        right=glue.FieldReferenceExpression(
                                            field_reference=glue.FieldReference(
                                                field=glue.Field(name='prior_version'),
                                                table_name='_m2',
                                            ),
                                        ),
                                    ),
                                    glue.Condition(
                                        left=glue.FieldReferenceExpression(
                                            field_reference=glue.FieldReference(
                                                field=glue.Field(name='object_id'),
                                                table_name='_m',
                                            ),
                                        ),
                                        lookup=glue.FieldLookup.EQ,
                                        right=glue.FieldReferenceExpression(
                                            field_reference=glue.FieldReference(
                                                field=glue.Field(name='object_id'),
                                                table_name='_m2',
                                            ),
                                        ),
                                    ),
                                    connector=glue.FilterConnector.AND,
                                ),
                            ),
                            alias=NEXT_VERSION_FIELD,
                        ),
                    ),
                ],
            ),
            alias=METADATA_TABLE_ALIAS,
        ),
        join_type=glue.JoinType.INNER,
        on=glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name='object_id'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                    output_type=dict,
                ),
                lookup=glue.FieldLookup.EQ,
                right=value_expression,
            ),
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name='object_version'),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SECONDARY_PARTITION_KEY),
                        table_name=table_name,
                    ),
                ),
            ),
            connector=glue.FilterConnector.AND,
        ),
    )


def build_simple_query_statement_with_metadata(
    table: glue.SchemaReference,
    only: list[glue.FieldReference | glue.FieldReferenceAliased] | None = None,
    annotations: list[glue.AnnotationQuery] | None = None,
    joins: list[glue.JoinQuery] | None = None,
    where: glue.Conditions | None = None,
    order_by: list[glue.OrderByQuery] | None = None,
    limit: glue.LimitQuery | None = None,
) -> glue.QueryStatement:
    pks = (table.metadata or {}).get(META_PRIMARY_KEY) or [PRIMARY_PARTITION_KEY]
    table_name = table.alias or table.name

    _only = only or [
        glue.FieldReference(
            field=glue.Field(name='*'),
            table_name=table_name,
        ),
    ]

    _annotations = annotations or []
    _annotations.extend(
        [
            glue.AnnotationQuery(
                value=glue.ExpressionAnnotation(
                    expression=MetadataExpression(),
                    alias=METADATA_FIELD,
                ),
            ),
        ],
    )

    _joins = joins or []
    _joins.append(build_metadata_join_query(table_name, table.metadata))

    _group_by = [
        glue.GroupByQuery(
            field=glue.FieldReference(
                field=glue.Field(name=pk_field),
                table_name=table_name,
            ),
        )
        for pk_field in [*pks, SECONDARY_PARTITION_KEY]
    ]

    if order_by:
        for order_field in order_by:
            _group_by.append(glue.GroupByQuery(field=order_field.field))

    return glue.QueryStatement(
        only=_only,
        annotations=_annotations,
        table=table,
        joins=_joins,
        where=where,
        group_by=_group_by,
        order_by=order_by,
        limit=limit,
    )


class DataQueryTransform:
    def __init__(self, query: glue.QueryStatement):
        self.query = deepcopy(query)

    def transform(
        self,
        metadata_select_expression: str = METADATA_SELECT_EXPRESSION,
    ) -> glue.QueryStatement:
        return self._transform_query(self.query, metadata_select_expression)

    def _transform_query(
        self,
        query: glue.QueryStatement,
        metadata_select_expression: str = METADATA_SELECT_EXPRESSION,
    ) -> glue.QueryStatement:
        if isinstance(query.table, glue.SubQueryStatement):
            query.table.query = self._transform_query(
                query.table.query,
                metadata_select_expression=metadata_select_expression,
            )

        for annotation in query.annotations or []:
            if isinstance(annotation.value, glue.SubQueryStatement):
                annotation.value.query = self._transform_query(
                    annotation.value.query,
                    metadata_select_expression=metadata_select_expression,
                )
            elif isinstance(annotation.value, glue.ExpressionAnnotation):
                if isinstance(annotation.value.expression, MetadataExpression):
                    annotation.value.expression.value = metadata_select_expression

        for join in query.joins or []:
            if isinstance(join.table, glue.SubQueryStatement) and join.table.alias != METADATA_TABLE_ALIAS:
                join.table.query = self._transform_query(
                    join.table.query,
                    metadata_select_expression=metadata_select_expression,
                )

        return query
