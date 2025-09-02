"""
Data serialisation.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from math import isfinite
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Tuple, Type, cast
from uuid import UUID

import yaml
from pydantic import AnyUrl

from kelvin.api.client.base_model import BaseModelRoot
from kelvin.krn import KRN

from .utils import chdir


def load_include(filename: str, loader: Callable[[Any], Any]) -> Any:
    """Load include data."""

    index: Any

    if ":" in filename:
        filename, index = filename.rsplit(":", 1)
    else:
        index = None

    try:
        filename = filename.format_map(os.environ)
    except KeyError as e:
        raise ValueError(f"Unknown path variable {e!s} in filename {filename!r}")

    path = Path(filename).expanduser().resolve()

    with path.open("rt") as file, chdir(path.parent):
        result = loader(file) if path.suffix in (".yaml", ".yml", ".json") else file.read()

    if index is None:
        return result

    for level in index.split("."):
        if level[level[0] in "+-" :].isnumeric():
            level = int(level)
        try:
            result = result[level]
        except (IndexError, KeyError):
            raise ValueError(f"Unknown level {level!r} in filename {str(filename)!r}")

    return result


tokens = {"null", "true", "false", "NaN"}
delimiters = {("{", "}"), ("[", "]"), ('"', '"')}
number_re = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$")


def is_json(x: str) -> bool:
    """Check if value is probably a JSON string."""

    if not x:
        return False
    if x in tokens:
        return True
    if x.isnumeric():
        return True
    if x[0].isalpha():
        return False
    if len(x) == 1:
        return False
    if (x[0], x[-1]) in delimiters:
        return True
    if number_re.match(x):
        return True

    return False


def lower(x: Any, skip: bool = True) -> Any:
    """Lower data to a json-ready representation."""

    if x is None:
        return x
    if isinstance(x, str):
        return str(x)
    if isinstance(x, bool):
        return bool(x)
    if isinstance(x, int):
        return int(x)
    if isinstance(x, float):
        return x if isfinite(x) else None
    if isinstance(x, KRN) or issubclass(type(x), KRN):
        return str(x)
    if isinstance(x, AnyUrl):
        return str(x)
    if isinstance(x, Mapping):
        if not skip:
            return {lower(k, skip): lower(v, skip) for k, v in x.items()}
        return {
            k: v
            for k, v in (
                (lower(k, skip), lower(v, skip))
                for k, v in x.items()
                if not isinstance(k, str) or not k.startswith("__")
            )
            if v is not ...
        }
    if isinstance(x, datetime):
        suffix = "Z" if x.microsecond else ".000000Z"
        return x.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + suffix
    if isinstance(x, date):
        return x.isoformat()
    if isinstance(x, timedelta):
        return x.total_seconds()
    if isinstance(x, BaseModelRoot):
        return lower(x.root, skip)
    if isinstance(x, Iterable):
        if not skip:
            return [lower(v, skip) for v in x]
        return [v for v in (lower(v, skip) for v in x) if v is not ...]
    if isinstance(x, Enum):
        return x.name
    if isinstance(x, UUID):
        return str(x)

    if skip:
        return ...

    raise ValueError(f"Un-lowerable type: {type(x).__name__}")


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder."""

    def default(self, x: Any) -> Any:
        """Return a JSON-serialisable object."""

        try:
            return lower(x, skip=False)
        except ValueError:
            return super().default(x)


def jsonify(x: Any, sort_keys: bool = True, cls: Type[json.JSONEncoder] = JSONEncoder, **kwargs: Any) -> str:
    """Convert object to JSON."""

    return json.dumps(x, sort_keys=sort_keys, cls=cls, **kwargs)


class LoaderMeta(type):
    """Metaclass to add include constructor."""

    def __new__(metacls: Type[LoaderMeta], name: str, bases: Tuple[Type, ...], __dict__: Dict[str, Any]) -> LoaderMeta:
        """Add include constructer to class."""

        result = cast(LoaderMeta, super().__new__(metacls, name, bases, __dict__))

        # register the include constructor on the class
        result.add_constructor("!include", result.construct_include)  # type: ignore

        return result


class Loader(yaml.SafeLoader, metaclass=LoaderMeta):
    """YAML Loader with `!include` constructor."""

    def construct_include(self, node: yaml.ScalarNode) -> Any:
        """Include file referenced at node."""

        x = self.construct_scalar(node), lambda x: yaml.load(x, Loader=Loader)  # nosec
        if not isinstance(x, str):
            raise ValueError(f"Invalid filename type {type(x)!r}")

        return load_include(*x)


class Dumper(yaml.Dumper):
    """Custom YAML encoder."""

    def represent_data(self, x: Any) -> Any:
        """Return a YAML-serialisable representation."""

        if x is None:
            return super().represent_none(None)
        if isinstance(x, str):
            if "\n" in x:
                # use indented style for strings with newlines
                # strip trailing spaces, leading and trailing newlines
                x = re.sub(r"[ \t]+\n", "\n", x).lstrip("\n").rstrip()
                return self.represent_scalar("tag:yaml.org,2002:str", str(x), style="|")
            return self.represent_str(str(x))
        if isinstance(x, bool):
            return self.represent_bool(bool(x))
        if isinstance(x, int):
            return self.represent_int(int(x))
        if isinstance(x, float):
            return self.represent_float(float(x))
        if isinstance(x, Mapping):
            return self.represent_dict({**x})
        if isinstance(x, datetime):
            return self.represent_str(x.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + "Z")
        if isinstance(x, date):
            return self.represent_str(x.isoformat())
        if isinstance(x, Iterable):
            return self.represent_list([*x])
        if isinstance(x, Enum):
            return self.represent_str(x.name)

        return super().represent_data(x)


YAML_SEPARATOR = "\n...\n"


def yamlify(x: Any, sort_keys: bool = False, Dumper: Type[Dumper] = Dumper, **kwargs: Any) -> str:
    """Convert object to YAML."""

    result = cast(str, yaml.dump(x, sort_keys=sort_keys, Dumper=Dumper, **kwargs))

    return (
        result[: -len(YAML_SEPARATOR)]
        if result.endswith(YAML_SEPARATOR)
        else result[:-1] if result.endswith("\n") else result
    )
