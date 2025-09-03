import ast
import traceback
from pathlib import Path

from amsdal_cli.commands.verify.models import VerifyError


def verify_python_file(python_file: Path) -> list[VerifyError]:
    """
    Verify the Python file for syntax errors.

    Args:
        python_file (Path): The path to the Python file.

    Returns:
        list[VerifyError]: A list of VerifyError objects if there are errors, otherwise an empty list.
    """
    try:
        with python_file.open('rt') as _file:
            ast.parse(_file.read())
    except Exception as ex:
        return [
            VerifyError(
                file_path=python_file,
                message='Cannot parse PY file',
                details=f'{ex}: {traceback.format_exc()}',
            ),
        ]

    return []
