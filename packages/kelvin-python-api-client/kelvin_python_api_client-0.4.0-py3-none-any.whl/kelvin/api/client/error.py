"""
Errors.
"""

from __future__ import annotations

import json
from textwrap import indent
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from requests import Response

from .serialize import lower

if TYPE_CHECKING:
    from .data_model import DataModel


class ClientError(Exception):
    """General exception"""


class LoginError(ClientError):
    """Login exception"""


class APIError(ClientError):
    """API Error."""

    errors: List[DataModel]

    def __init__(self, response: Response, converter: Optional[Callable[[Any], DataModel]] = None) -> None:
        """Initialise API error."""

        from .model.responses import ErrorMessage

        self.response = response

        if converter is not None:
            result = converter(response.json())
            if hasattr(result, "errors"):
                self.errors = result.errors
            elif hasattr(result, "error"):
                self.errors = [result.error]
            else:
                self.errors = [result]
        else:
            self.errors = []
            for error in response.json().get("errors", []):
                message = error.get("message", [])
                if not isinstance(message, list):
                    message = [message]
                self.errors += [ErrorMessage(client=None, **{**error, "message": [str(x) for x in message]})]

        super().__init__()

    def __str__(self) -> str:
        # return json.dumps([error.dict() for error in self.errors], indent=2)
        return json.dumps(lower(self.errors), indent=2)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(errors={self.errors!r})"


class ResponseError(ClientError):
    """Response error."""

    def __init__(self, message: str, response: Response) -> None:
        """Initialise error."""

        self.message = message
        self.response = response

    def __str__(self) -> str:
        content_type = self.response.headers.get("Content-Type", "unknown").split(";", 1)[0]

        return f"{self.message} ({content_type}):\n{indent(self.response.text, '  ')}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message!r}, response={self.response!r})"
