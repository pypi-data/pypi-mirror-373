from typing import Any

from amsdal_cli.commands.generate.enums import AttributeType


def cast_to_attribute_type(
    attr_type: AttributeType,
    value: str,
) -> Any:
    """
    Casts a string value to the specified attribute type.

    Args:
        attr_type (AttributeType): The type to which the value should be cast.
        value (str): The string value to be cast.

    Returns:
        Any: The value cast to the specified attribute type, or None if the value is 'null'.
    """
    if value.lower() == 'null':
        return None

    match attr_type:
        case AttributeType.NUMBER:
            return float(value)
        case AttributeType.BOOLEAN:
            return value.lower() == 'true'
        case _:
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value
