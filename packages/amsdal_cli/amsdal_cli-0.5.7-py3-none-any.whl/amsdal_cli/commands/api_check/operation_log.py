import base64
import json
import re
from json import JSONEncoder
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class BytesJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('utf-8')
        return super().default(o)


class OperationLog(BaseModel):
    method: str
    uri: str
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, str] | None = None
    data: Any
    status_code: int
    response_data: Any
    response_headers: dict[str, str] = Field(default_factory=dict)

    @property
    def id(self) -> str:
        _params = json.dumps(self.params, cls=BytesJSONEncoder) if self.params else None
        _data = json.dumps(self.data, cls=BytesJSONEncoder) if self.data else None
        return f'{self.method} {self.uri} {_params} {_data}'

    def __str__(self) -> str:
        _response = (
            json.dumps(self.response_data, cls=BytesJSONEncoder) if not isinstance(self.response_data, str) else None
        )

        return f'{self.id} {self.status_code} {_response}'

    @classmethod
    def from_response(
        cls,
        response: Any,
        auth_headers: dict[str, Any] | None = None,
        *,
        ignore_object_version: bool = False,
        ignore_class_version: bool = False,
    ) -> 'OperationLog':
        request_headers = {key.lower(): value for key, value in response.request.headers.items()}

        if auth_headers:
            request_headers.update({key.lower(): '*****' for key in auth_headers})

        return cls(
            method=response.request.method,
            uri=response.request.url.path,
            headers=request_headers,
            params=dict(response.request.url.params.items()),
            data=response.request.content,
            status_code=response.status_code,
            response_data=cls._process_response_data(
                response.text,
                ignore_object_version=ignore_object_version,
                ignore_class_version=ignore_class_version,
            ),
            response_headers=response.headers,
        )

    @classmethod
    def _process_response_data(cls, text: str, *, ignore_object_version: bool, ignore_class_version: bool) -> Any:
        if ignore_object_version:
            text = re.sub(r'"object_version": "(?!(?:ALL|LATEST)\b).*?"', '"object_version": "ignore"', text)

        if ignore_class_version:
            text = re.sub(r'"class_version": "(?!(?:ALL|LATEST)\b).*?"', '"class_version": "ignore"', text)

        return text
