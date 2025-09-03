from typing import Any

from pydantic import BaseModel


class ClassItem(BaseModel):
    class_name: str
    properties: list[dict[str, Any]]


class Transaction(BaseModel):
    title: str
    properties: dict[str, Any]
