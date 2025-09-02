"""
API Service Model.
"""

from __future__ import annotations

import json
from collections import ChainMap
from datetime import datetime, timezone
from importlib import import_module
from types import FunctionType, MethodType
from typing import TYPE_CHECKING, Any, Dict, Iterator, Mapping, Optional, Sequence, Tuple, Type, TypeVar, Union, cast

import structlog
from pydantic import ConfigDict, ValidationError
from typing_inspect import get_args, get_origin

from kelvin.api.client.data_model import DataModel, KIterator, KList
from kelvin.api.client.model.pagination import PaginationLimits
from kelvin.api.client.serialize import lower

from .base_model import BaseModel, BaseModelMeta, BaseModelRoot
from .error import APIError, ResponseError
from .serialize import is_json
from .utils import file_tuple, metadata_tuple

if TYPE_CHECKING:
    from .client import Client

logger = structlog.get_logger(__name__)

T = TypeVar("T")

JSON_CONTENT_TYPES = (
    "application/json",
    "application/x-json-stream",
)
MODELS = "kelvin.api.client.model"


def resolve_fields(x: Mapping[str, Any]) -> Dict[str, Any]:
    """Resolve fields from data models."""

    result: Dict[str, Any] = {**x}
    items = [*x.items()]

    for name, value in items:
        if "_" in name and isinstance(value, DataModel):
            head, tail = name.rsplit("_", 1)
            if head != type(value).__name__.lower():
                raise TypeError(f"Unable to get {name!r} from {type(value).__name__!r} object")
            value = result[name] = value[tail]
        if isinstance(value, datetime):
            suffix = "Z" if value.microsecond else ".000000Z"
            result[name] = value.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + suffix

    return result


class ApiServiceModelMeta(BaseModelMeta):
    """DataModel metaclass."""

    def __new__(
        metacls: Type[ApiServiceModelMeta], name: str, bases: Tuple[Type, ...], __dict__: Dict[str, Any]
    ) -> ApiServiceModelMeta:
        cls = cast(ApiServiceModelMeta, super().__new__(metacls, name, bases, __dict__))

        # kill unused fields so that they can be used by models
        cls.fields = cls.schema = None  # type: ignore

        return cls

    def __repr__(self) -> str:
        """Pretty representation."""

        methods = "\n".join(
            f"  - {name}: " + x.__doc__.lstrip().split("\n")[0]
            for name, x in ((name, getattr(self, name)) for name in sorted(vars(self)) if not name.startswith("_"))
            if x.__doc__ is not None and isinstance(x, (FunctionType, MethodType))
        )

        return f"{self.__name__}:\n{methods}"

    def __str__(self) -> str:
        """Return str(self)."""

        return f"<class {self.__name__!r}>"


def get_type(name: str) -> Type:
    module_name, type_name = name.rsplit(".", 1)
    return getattr(import_module(f"{MODELS}.{module_name}"), type_name)


P = TypeVar("P", bound=DataModel)


class ApiServiceModel(BaseModel, metaclass=ApiServiceModelMeta):
    """API Service Model base-class."""

    if TYPE_CHECKING:
        fields: Any = None
        schema: Any = None
    model_config: ConfigDict = ConfigDict(extra="allow")
    # TODO: Remove this attribute
    __slots__ = ("_client",)

    # TODO: Delete Client from the constructor
    def __init__(self, client: Optional[Client] = None, **kwargs: Any) -> None:
        """Initialise model."""
        super().__init__(**kwargs)

        object.__setattr__(self, "_client", client)

    # TODO: Delete this property, Client is always passed to the function
    @property
    def client(self) -> Optional[Client]:
        """Resource client."""

        if self._client is not None:
            return self._client

        if self._owner is not None:
            return self._owner.client

        return None

    def __getattribute__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith("_"):
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""

        if name.startswith("_"):
            super().__setattr__(name, value)

    @classmethod
    def _make_request(
        cls,
        client: Optional[Client],
        method: str,
        path: str,
        values: Mapping[str, Any],
        params: Mapping[str, Any],
        files: Mapping[str, Any],
        headers: Mapping[str, Any],
        data: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]],
        body_type: Optional[str],
        array_body: bool,
        result_types: Mapping[str, Optional[Type[Any]]],
        stream: bool = False,
        dry_run: bool = False,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make request to API."""

        if client is None:
            raise ValueError("No client set.")

        # check for fields that need to be dereferenced
        values = resolve_fields(values)
        params = resolve_fields(params)
        files = resolve_fields(files)
        headers = resolve_fields(headers)

        if "{" in path:
            path = path.format_map(values)

        body_data: Any = None

        if body_type is not None:
            body_type_ = get_type(body_type)

            def prepare(x: Mapping[str, Any]) -> Dict[str, Any]:
                if kwargs:
                    x = ChainMap(kwargs, x)  # type: ignore
                return {
                    k: v
                    for k, v in ((name, x.get(name)) for name in cast(Type[DataModel], body_type_).model_fields)
                    if v is not None
                }

            if array_body:
                if data is None:
                    data = [{}] if kwargs else []
                elif not isinstance(data, Sequence) and all(isinstance(x, Mapping) for x in data):
                    raise ValueError("Data must be a sequence of mappings")

                body_data = [
                    body_type_(**lower(prepare(x))).dict(by_alias=True) for x in cast(Sequence[Mapping[str, Any]], data)
                ]
            else:
                if data is None:
                    data = {}
                elif not isinstance(data, Mapping):
                    raise ValueError("Data must be a mapping")

                body_data = body_type_(**lower(prepare(data))).dict(by_alias=True)
        else:
            body_data = None
        metadata = None
        if "metadata" in files:
            metadata = files.pop("metadata")
        files = {k: file_tuple(v) for k, v in files.items()}
        if metadata is not None:
            files = {**files, "metadata": metadata_tuple(metadata)}
        if dry_run:
            return {
                "path": path,
                "method": method,
                "data": body_data,
                "params": params,
                "files": files,
                "headers": headers,
            }

        response = client.request(path, method, body_data, params, files, headers, raise_error=False, stream=stream)

        try:
            content_type = response.headers.get("Content-Type", "")
            if content_type == "application/octet-stream":
                return response.iter_content(1024)

            if content_type == "application/yaml":
                return response.iter_content(1024)

            status_code = response.status_code

            result_type = result_types.get(str(status_code), ...)

            if not response.ok:
                if result_type is ...:
                    # try to fill gap with first not "OK" response
                    result_type = next(
                        (v for k, v in sorted(result_types.items()) if not 200 <= int(k) < 300),
                        ...,
                    )
                    if result_type is ...:
                        logger.warning("Unknown response code", status_code=status_code)
                        result_type = None
                        if content_type == "application/json" or is_json(response.text):
                            raise APIError(response)
                        response.raise_for_status()

            elif result_type is ...:
                # try to fill gap with first "OK" response
                result_type = next((v for k, v in sorted(result_types.items()) if 200 <= int(k) < 300), ...)
                if result_type is ...:
                    logger.warning("Unknown response code", status_code=status_code)
                    result_type = None

            if isinstance(result_type, type):
                if not content_type.startswith(JSON_CONTENT_TYPES):
                    with response:
                        raise ResponseError(
                            f"Unexpected response for {result_type.__name__}",  # type: ignore
                            response,
                        )

                def converter(x: Any) -> Any:
                    if issubclass(result_type, BaseModelRoot):  # type: ignore
                        return result_type(x)  # type: ignore

                    if isinstance(x, list):
                        return result_type(x)  # type: ignore
                    return result_type(**x)  # type: ignore

            elif get_origin(result_type) is list:
                result_type, *_ = get_args(result_type)
                if not content_type.startswith(JSON_CONTENT_TYPES):
                    with response:
                        raise ResponseError(
                            f"Unexpected response for {result_type.__name__}",  # type: ignore
                            response,
                        )

                def converter(x: Any) -> Any:
                    return KList([result_type(**v) for v in x])  # type: ignore

            else:
                if not content_type.startswith(JSON_CONTENT_TYPES):
                    with response:
                        return response.text or None

                def converter(x: Any) -> Any:
                    return x

            if not response.ok:
                with response:
                    raise APIError(response, converter)

            if stream:

                def results() -> Iterator[Any]:
                    i = -1
                    errors = []
                    success = False
                    with response:
                        for x in response.iter_lines():
                            if not x:
                                continue
                            i += 0
                            records = json.loads(x)
                            if isinstance(records, dict):
                                records = [records]

                            for record in records:
                                try:
                                    yield converter(record)
                                except ValidationError as e:
                                    errors += [(i, e)]
                                    continue
                                else:
                                    success = True

                        if not errors:
                            return

                        if not success:
                            raise errors[0][1] from None
                        elif errors:
                            summary = "\n".join(f"  {i}: {x}" for i, x in errors)
                            logger.warning("Skipped items", result_type=result_type, summary=summary)

                results.__qualname__ = "results"

                return KIterator(results())
            else:
                with response:
                    try:
                        return converter(response.json())
                    except ValidationError as e:
                        raise e from None

        except Exception:
            response.close()
            raise

    @classmethod
    def scan(
        cls,
        client: Optional[Client],
        path: str,
        api_response: Any,
        flatten: bool = True,
        method: str = "GET",
        data: Any = None,
    ) -> Iterator[Any]:
        """Iterate pages."""

        result = api_response

        if client is None:
            raise ValueError("No client set.")

        while True:
            if not result.data:
                return

            if flatten:
                yield from result.data
            else:
                yield result.data

            pagination = result.pagination
            if pagination is None:
                return

            if isinstance(pagination, PaginationLimits):
                page = pagination.page
                if page is None:
                    return

                total_pages = pagination.total_pages
                if page == total_pages:
                    return
                page_size = len(result.data)
                params = {"page": page + 1, "page_size": page_size}
            else:
                next_page = pagination.next_page
                if next_page is None:
                    return

                if "?" in next_page:
                    path = next_page
                    params = {}
                else:
                    page_size = len(result.data)
                    params = {"next": next_page, "page_size": page_size}

            with client.request(path, method=method, params=params, data=data) as response:
                result = type(api_response)(**response.json(), client=client)

    @classmethod
    def fetch(
        cls, client: Optional[Client], path: str, api_response: Any, method: str = "GET", data: Any = None
    ) -> Sequence[Any]:
        """Fetch all data."""

        return type(api_response.data)(cls.scan(client, path, api_response, True, method=method, data=data))
