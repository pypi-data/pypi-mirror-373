import json
import traceback
from json import JSONDecodeError
from pathlib import Path

from amsdal_cli.commands.verify.models import VerifyError


def verify_json_model(model_file: Path) -> list[VerifyError]:
    """
    Verify the JSON model file.

    Args:
        model_file (Path): The path to the JSON model file.

    Returns:
        list[VerifyError]: A list of VerifyError objects if there are errors, otherwise an empty list.
    """
    try:
        with model_file.open('rt') as _file:
            data = json.loads(_file.read())
    except (JSONDecodeError, TypeError) as err:
        return [
            VerifyError(
                file_path=model_file,
                message='Cannot parse JSON file',
                details=f'{err}: {traceback.format_exc()}',
            ),
        ]

    if not isinstance(data, dict):
        return [
            VerifyError(
                file_path=model_file,
                message='Incorrect JSON format',
                details=f'The JSON model should be defined as an object instead of {type(data)}',
            ),
        ]

    return []
