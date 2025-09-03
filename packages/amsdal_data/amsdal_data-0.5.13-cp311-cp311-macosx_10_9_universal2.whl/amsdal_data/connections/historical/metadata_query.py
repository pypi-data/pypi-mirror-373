from typing import Any

import amsdal_glue as glue

from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD


def build_metadata_query(
    object_id: list[Any],
    class_name: str,
) -> glue.QueryStatement:
    return glue.QueryStatement(
        table=glue.SubQueryStatement(
            alias='m',
            query=glue.QueryStatement(
                table=glue.SchemaReference(name=METADATA_TABLE, version=glue.Version.LATEST),
                only=[glue.FieldReference(field=glue.Field(name='*'), table_name=METADATA_TABLE)],
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
                                                table_name=METADATA_TABLE,
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
                                                table_name=METADATA_TABLE,
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
                where=glue.Conditions(
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(
                                    name='class_schema_reference',
                                    child=glue.Field(
                                        name='ref',
                                        child=glue.Field(
                                            name='object_id',
                                        ),
                                    ),
                                ),
                                table_name=METADATA_TABLE,
                            ),
                            output_type=str,
                        ),
                        lookup=glue.FieldLookup.EQ,
                        right=glue.Value(class_name),
                    ),
                ),
            ),
        ),
        where=glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(field=glue.Field(name='object_id'), table_name='m'),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(object_id),
            ),
            glue.Conditions(
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(field=glue.Field(name=NEXT_VERSION_FIELD), table_name='m'),
                    ),
                    lookup=glue.FieldLookup.ISNULL,
                    right=glue.Value(True),
                ),
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(field=glue.Field(name=NEXT_VERSION_FIELD), table_name='m'),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    right=glue.Value(''),
                ),
                connector=glue.FilterConnector.OR,
            ),
        ),
    )
