import re
from typing import Any

import typer
from pydantic import BaseModel
from rich import print as rprint

from amsdal_cli.commands.generate.enums import AttributeType
from amsdal_cli.commands.generate.enums import JsonType
from amsdal_cli.commands.generate.enums import OptionName
from amsdal_cli.commands.generate.utils.cast_to_attribute_type import cast_to_attribute_type
from amsdal_cli.utils.text import rich_error


class Attribute(BaseModel):
    """
    Represents an attribute of a model.

    Attributes:
        name (str): The name of the attribute.
        type (AttributeType): The type of the attribute.
        reference (str | None): The reference type if the attribute is a relationship.
        default (Any): The default value of the attribute.
        index (bool): Indicates if the attribute is indexed.
        required (bool): Indicates if the attribute is required.
        unique (bool): Indicates if the attribute is unique.
        item_key_type (str | None): The key type if the attribute is a dictionary.
        item_value_type (str | None): The value type if the attribute is a dictionary.
    """

    class NotSet: ...

    name: str
    type: AttributeType
    reference: str | None = None
    default: Any = NotSet
    index: bool = False
    required: bool = False
    unique: bool = False
    item_key_type: str | None = None
    item_value_type: str | None = None

    @property
    def json_type(self) -> str | None:
        """
        Resolves the JSON type for the attribute.

        Returns:
            str | None: The JSON type of the attribute, or None if it cannot be resolved.
        """
        return self.resolve_attribute_type_to_json(self.type, reference_type=self.reference)

    @property
    def has_items(self) -> bool:
        """
        Checks if the attribute has items.

        Returns:
            bool: True if the attribute has items, False otherwise.
        """
        return self.json_items is not None

    @property
    def json_items(self) -> dict[str, Any]:  # type: ignore[return]
        """
        Resolves the JSON items for the attribute.

        Returns:
            dict[str, Any]: A dictionary representing the JSON items of the attribute, or None if it cannot be resolved.
        """
        if self.reference and self.type == AttributeType.HAS_MANY:
            return {'type': self.reference}
        elif self.type == AttributeType.DICT and self.item_key_type and self.item_value_type:
            return {
                'key': {
                    'type': self.resolve_attribute_type_to_json(self.item_key_type, self.item_key_type),
                },
                'value': {
                    'type': self.resolve_attribute_type_to_json(self.item_value_type, self.item_value_type),
                },
            }

    @staticmethod
    def resolve_attribute_type_to_json(attribute_type: str | AttributeType, reference_type: str | None) -> str | None:
        """
        Resolves the JSON type for the given attribute type.

        Args:
            attribute_type (str | AttributeType): The attribute type to be resolved.
            reference_type (str | None): The reference type if the attribute is a relationship.

        Returns:
            str | None: The resolved JSON type, or None if it cannot be resolved.
        """
        try:
            match AttributeType(attribute_type):
                case AttributeType.STRING:
                    return JsonType.STRING.value
                case AttributeType.INTEGER:
                    return JsonType.INTEGER.value
                case AttributeType.NUMBER:
                    return JsonType.NUMBER.value
                case AttributeType.BOOLEAN:
                    return JsonType.BOOLEAN.value
                case AttributeType.HAS_MANY:
                    return JsonType.ARRAY.value
                case AttributeType.DICT:
                    return JsonType.DICT.value
                case _:
                    return reference_type
        except ValueError:
            return reference_type


def split_attributes(attributes_string: str) -> list[str]:
    """
    Splits a string of attributes into a list of individual attributes.

    Args:
        attributes_string (str): The string containing attributes to be split.

    Returns:
        list[str]: A list of individual attribute strings.
    """
    return re.split(r'\s(?=(?:[^"]*"[^"]*")*[^"]*$)', attributes_string.replace("'", '"'))


def parse_attributes(attrs: list[str]) -> list[Attribute]:
    """
    Parses attributes from the command line arguments and returns a list of Attribute objects.

    Args:
        attrs (list[str]): A list of attribute strings from the command line arguments.

    Returns:
        list[Attribute]: A list of Attribute objects.

    Examples:
        input: ['name:string:default="John Doe" age:number:index:default=18 address:string:required']
        output: [
            Attribute(name='name', type='string', default='John Doe'),
            Attribute(name='age', type='number', index=True, default=18),
            Attribute(name='address', type='string', required=True),
        ]
    """
    attributes: dict[str, Attribute] = {}

    for _attr_item in attrs:
        if not _attr_item:
            continue

        for attr in split_attributes(_attr_item):
            [attr_name, _attr_type, *attr_options] = attr.split(':')
            attr_type = AttributeType(_attr_type)
            params: dict[str, Any] = {}

            if attr_name in attributes:
                rprint(rich_error(f'The "{attr_name}" attribute is duplicated!'))
                raise typer.Exit

            if attr_type in (AttributeType.BELONGS_TO, AttributeType.HAS_MANY):
                try:
                    params['reference'] = JsonType[AttributeType(attr_options[0].lower()).name].value
                except ValueError:
                    params['reference'] = attr_options[0]

                attr_options = attr_options[1:]
            elif attr_type == AttributeType.DICT:
                params['item_key_type'] = attr_options[0]
                params['item_value_type'] = attr_options[1]
                attr_options = attr_options[2:]

            for attr_option in attr_options:
                if attr_option.lower() == OptionName.INDEX.value:
                    params['index'] = True
                    continue

                # property can be marked as indexed + required + unique
                if attr_option.lower() == OptionName.REQUIRED.value:
                    params['required'] = True
                    continue

                # property can be marked as indexed + required + unique
                if attr_option.lower() == OptionName.UNIQUE.value:
                    params['unique'] = True
                    continue

                if '=' in attr_option:
                    _option, value = attr_option.split('=')
                    option = OptionName(_option)

                    match option:
                        case OptionName.DEFAULT:
                            params['default'] = cast_to_attribute_type(attr_type, value)
                        case _:
                            rprint(rich_error(f'Unknown option "{option}"'))
                            raise typer.Exit

            attributes[attr_name] = Attribute(
                name=attr_name,
                type=attr_type,
                **params,
            )
    return list(attributes.values())
