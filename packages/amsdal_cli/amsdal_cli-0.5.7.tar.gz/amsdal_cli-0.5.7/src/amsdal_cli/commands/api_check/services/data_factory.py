import random
import string
from typing import Any

from faker import Faker

from amsdal_cli.commands.api_check.data_classes import ClassItem


class DataFactory:
    _faker = Faker()

    @classmethod
    def build_data(cls, class_item: ClassItem) -> dict[str, Any]:
        """
        Build sample data for a class based on its properties.

        Args:
            class_item: The class item containing property definitions

        Returns:
            A dictionary with generated data for each property
        """
        result = {'_type': class_item.class_name}

        for prop in class_item.properties:
            prop_name = prop.get('title', '')
            prop_type = prop.get('type', 'string')

            # Skip if no name
            if not prop_name:
                continue

            # Generate value based on type
            result[prop_name] = cls.generate_value_for_type(prop_type, prop)

        return result

    @classmethod
    def build_update_data(cls, class_item: ClassItem, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build updated data for an existing object.

        Args:
            class_item: The class item containing property definitions
            data: The existing data to update

        Returns:
            A dictionary with updated data
        """
        result = {'_type': class_item.class_name}

        # Copy metadata if present
        if '_metadata' in data:
            result['_metadata'] = data['_metadata']

        for prop in class_item.properties:
            prop_name = prop.get('key', '')
            prop_type = prop.get('type', 'string')

            # Skip if no name
            if not prop_name:
                continue

            # For update, we'll modify some values but keep others
            threshold = 0.5
            if prop_name in data and random.random() < threshold:  # noqa: S311
                # Keep 50% of values the same
                result[prop_name] = data[prop_name]
            else:
                # Generate new values for the rest
                result[prop_name] = cls.generate_value_for_type(prop_type, prop)

        return result

    @classmethod
    def generate_value_for_type(
        cls,
        type_name: str,
        prop_info: dict[str, Any],
    ) -> Any:
        """
        Generate a random value for a given type.

        Args:
            type_name: The type of the property
            prop_info: Additional property information

        Returns:
            A randomly generated value appropriate for the type
        """
        # Check if there's a default value
        if 'default' in prop_info:
            return prop_info['default']

        # Generate based on type
        type_lower = type_name.lower()

        if type_lower == 'string':
            return cls._faker.text(max_nb_chars=50)

        elif type_lower == 'integer':
            return cls._faker.random_int(min=1, max=1000)

        elif type_lower == 'number':
            return cls._faker.pyfloat(positive=True, right_digits=2, max_value=1000)

        elif type_lower == 'boolean':
            return cls._faker.boolean()

        elif type_lower == 'date':
            return cls._faker.date_object().isoformat()

        elif type_lower == 'datetime':
            return cls._faker.date_time().isoformat()

        elif type_lower == 'array':
            # Check if items type is specified
            if 'items' in prop_info and prop_info['items'] is not None:
                items_info = prop_info['items']
                item_type = items_info.get('type', 'string')
                # Generate array with proper item types
                return [
                    cls.generate_value_for_type(item_type, items_info)
                    for _ in range(random.randint(1, 3))  # noqa: S311
                ]
            else:
                # Fallback to array of strings if no items info
                return [cls._faker.word() for _ in range(random.randint(1, 3))]  # noqa: S311

        elif type_lower in {'dictionary', 'object'}:
            # Check if key and value types are specified
            if 'items' in prop_info and prop_info['items'] is not None:
                items_info = prop_info['items']
                key_info = items_info.get('key', {'type': 'string'})
                value_info = items_info.get('value', {'type': 'string'})

                # Generate dictionary with proper key and value types
                result = {}
                for _ in range(random.randint(1, 3)):  # noqa: S311
                    # For keys, we need to ensure they're strings or can be converted to strings
                    key = cls.generate_value_for_type(key_info.get('type', 'string'), key_info)
                    if not isinstance(key, str):
                        key = str(key)
                    value = cls.generate_value_for_type(value_info.get('type', 'string'), value_info)
                    result[key] = value
                return result
            else:
                # Fallback to dictionary of strings if no items info
                return {cls._faker.word(): cls._faker.word() for _ in range(random.randint(1, 3))}  # noqa: S311

        elif type_lower == 'binary':
            # Generate a small binary string
            return ''.join(random.choice(string.ascii_letters) for _ in range(10))  # noqa: S311

        # For any other type, it might be a reference to another class
        # For testing purposes, we'll return a dictionary with a _type field
        return None
