import copy
from typing import Any


def _merge_list_of_lists(parent: list[list[str]], child: list[list[str]]) -> list[list[str]]:
    result_elements = [sorted(child_element) for child_element in child]

    for parent_element in parent:
        sorted_parent_element = sorted(parent_element)
        if sorted_parent_element not in result_elements:
            result_elements.append(sorted_parent_element)

    return result_elements


def _merge_list_fields(parent: list[Any], child: list[Any]) -> list[Any]:
    if not parent:
        return child

    if not child:
        return parent

    if isinstance(parent[0], list):
        return _merge_list_of_lists(parent, child)

    for parent_element in parent:
        if parent_element not in child:
            child.append(parent_element)

    if isinstance(child[0], dict):
        return child

    return sorted(child)


def merge_schema(parent_schema: dict[str, Any], child_schema: dict[str, Any]) -> dict[str, Any]:
    """
    Merges the child schema into the parent schema.

    This function takes two schemas represented as dictionaries and merges the child schema into the parent schema.
    It handles merging of lists and dictionaries within the schemas, ensuring that the parent schema is updated with
    the values from the child schema.

    Args:
        parent_schema (dict[str, Any]): The parent schema to be merged into.
        child_schema (dict[str, Any]): The child schema to merge from.

    Returns:
        dict[str, Any]: The merged schema.
    """
    for field_name, field_value in child_schema.items():
        if parent_schema.get(field_name) is None:
            parent_schema[field_name] = copy.copy(field_value)
            continue

        if isinstance(field_value, list) and isinstance(parent_schema[field_name], list):
            parent_schema[field_name] = _merge_list_fields(parent_schema[field_name], field_value)
            continue

        if isinstance(field_value, dict) and isinstance(parent_schema[field_name], dict):
            parent_schema[field_name] = merge_schema(parent_schema[field_name], field_value)
            continue

        parent_schema[field_name] = copy.copy(field_value)

    return parent_schema
