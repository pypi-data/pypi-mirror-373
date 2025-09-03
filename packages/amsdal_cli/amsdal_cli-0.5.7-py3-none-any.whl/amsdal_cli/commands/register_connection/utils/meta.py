from typing import Any


def process_meta(meta: list[str] | None) -> dict[str, dict[str, Any]]:
    """
    Process meta information for the connection.
    Example input: pk="data.csv:column_name" -> {'data.csv': {'pk': ['column_name']}}
    """

    data: dict[str, dict[str, Any]] = {}

    if not meta:
        return data

    for meta_item in meta:
        key, value = meta_item.split('=', 1)
        key = key.strip()
        value = value.strip()
        file_name, column_names = value.split(':', 1)
        _column_names = column_names.split(',')

        _per_file_meta = data.setdefault(file_name.strip(), {})
        _per_file_meta[key] = [col.strip() for col in _column_names]

    return data
