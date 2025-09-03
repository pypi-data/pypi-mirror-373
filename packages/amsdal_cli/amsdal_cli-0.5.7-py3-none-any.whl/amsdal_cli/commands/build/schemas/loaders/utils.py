import json
import logging
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def load_object_schema_from_json_file(file_path: Path, model_cls: type[BaseModel]) -> Iterator[BaseModel]:
    """
    Loads object schema from a JSON file and yields instances of the given model class.

    This function reads the content of the specified JSON file and attempts to parse it. If the content is a list,
    it yields instances of the given model class for each item in the list. Otherwise, it yields a single instance
    of the model class.

    Args:
        file_path (Path): The path to the JSON file containing the data.
        model_cls (type[BaseModel]): The Pydantic model class to validate and instantiate the data.

    Yields:
        Iterator[BaseModel]: An iterator over instances of the model class created from the JSON data.

    Raises:
        json.JSONDecodeError: If the JSON file cannot be decoded.
    """
    content = file_path.read_text('utf-8')

    try:
        config_json = json.loads(content)
    except json.JSONDecodeError as e:
        logger.exception('Error loading JSON %s', file_path.resolve(), exc_info=e)
        raise
    else:
        if isinstance(config_json, list):
            for _item in config_json:
                yield model_cls.model_validate(_item)
        else:
            yield model_cls.model_validate(config_json)
