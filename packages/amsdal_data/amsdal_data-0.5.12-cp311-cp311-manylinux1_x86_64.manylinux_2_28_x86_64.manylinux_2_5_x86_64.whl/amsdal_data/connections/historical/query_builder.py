from typing import Any

import amsdal_glue as glue

from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS


def split_conditions(conditions: glue.Conditions | glue.Condition) -> list[glue.Conditions]:
    if isinstance(conditions, glue.Condition):
        return [glue.Conditions(conditions)]

    if len(conditions.children) == 1:
        return [conditions]

    if conditions.connector == glue.FilterConnector.OR:
        if conditions.negated:
            return _process_and_split(_reverse_conditions(conditions))

        return _process_or_split(conditions)

    if conditions.negated:
        return _process_or_split(_reverse_conditions(conditions))

    return _process_and_split(conditions)


def pull_out_filter_from_query(
    conditions: glue.Conditions,
    field: glue.Field,
) -> tuple[set[Any], glue.Conditions | None]:
    if conditions.connector != glue.FilterConnector.AND:
        msg = 'Only AND connector is supported'
        raise ValueError(msg)

    pulled_values = set()
    result_conditions = conditions.__copy__()
    result_conditions.children = []

    for child in conditions.children:
        if isinstance(child, glue.Conditions):
            _values, _conditions = pull_out_filter_from_query(child, field)
            pulled_values.update(_values)

            if _conditions is not None:
                result_conditions.children.append(_conditions)

            continue

        if (
            isinstance(child.left, glue.FieldReferenceExpression)
            and child.left.field_reference.field == field
            and isinstance(child.right, glue.Value)
        ):
            pulled_values.add(child.right.value)
        else:
            result_conditions.children.append(child)

    if result_conditions.children:
        if len(result_conditions.children) == 1 and isinstance(result_conditions.children[0], glue.Conditions):
            return pulled_values, result_conditions.children[0]
        else:
            return pulled_values, result_conditions

    return pulled_values, None


def sort_items(items: list[glue.Data], order_by_list: list[glue.OrderByQuery] | None) -> list[glue.Data]:
    if not order_by_list:
        return items

    for order_by in reversed(order_by_list):
        items.sort(
            key=lambda item: get_field_value(item.data, order_by.field.field, order_by.field.table_name) or 0,
            reverse=(order_by.direction == glue.OrderDirection.DESC),
        )
    return items


def get_field_value(item: dict[str, Any], field: glue.Field, table_name: str | None = None) -> Any:
    _field = field
    value = item

    if table_name == METADATA_TABLE_ALIAS:
        _field = glue.Field(name=field.name, parent=glue.Field(name='_metadata'))

    if _field.parent:
        value = get_field_value(item, _field.parent)

    if _field.name not in value:
        msg = f'Field {_field.name} not found in {value}'
        raise ValueError(msg)

    return value[_field.name]


def _process_and_split(conditions: glue.Conditions) -> list[glue.Conditions]:
    splits: list[glue.Conditions] = []

    for child_condition in conditions.children:
        child_splits = split_conditions(child_condition)

        if not splits:
            splits = child_splits
            continue

        new_splits = []

        for existing_split in splits:
            for child_split in child_splits:
                new_splits.append(existing_split & child_split)

        splits = new_splits

    return splits


def _process_or_split(conditions: glue.Conditions) -> list[glue.Conditions]:
    splits = []

    for child_condition in conditions.children:
        splits.extend(split_conditions(child_condition))

    return splits


def _reverse_conditions(conditions: glue.Conditions) -> glue.Conditions:
    return glue.Conditions(
        *[
            ~child_condition if isinstance(child_condition, glue.Conditions) else ~glue.Conditions(child_condition)
            for child_condition in conditions.children
        ],
        connector=conditions.connector,
        negated=not conditions.negated,
    )
