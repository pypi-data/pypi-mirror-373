from pathlib import Path
from typing import Any

from pydantic import BaseModel


class VerifyError(BaseModel):
    """
    Represents an error encountered during verification.

    Attributes:
        file_path (Path): The path to the file where the error occurred.
        message (str): A message describing the error.
        details (Any): Additional details about the error.
    """

    file_path: Path
    message: str
    details: Any
