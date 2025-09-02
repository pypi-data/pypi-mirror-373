"""
Client Configuration.
"""

from __future__ import annotations

import json
import os
import pkgutil
from contextlib import AbstractContextManager, nullcontext
from copy import deepcopy
from functools import partial, reduce
from io import StringIO
from pathlib import Path
from textwrap import dedent, indent
from typing import (
    IO,
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

import xdg
from filelock import FileLock, Timeout
from jinja2 import StrictUndefined, Template, TemplateSyntaxError, UndefinedError
from pydantic import ConfigDict, Field
from pydantic_core import PydanticUndefinedType
from ruamel.yaml import YAML, Node, RoundTripConstructor, YAMLError
from ruamel.yaml.composer import Composer

from .base_model import BaseModel
from .serialize import is_json, jsonify, load_include, lower, yamlify
from .utils import chdir, flatten, inflate, merge, relative_to_home, update

EllipsisType = type(...)

LOCK_TIMEOUT = 1.0


def is_complex_type(annotation: object) -> bool:
    """
    Return True if `annotation` is a 'complex' type:
      - It's a Pydantic model
      - Or it's a container/generic (List, Dict, Tuple, Set, Union, etc.)
    """

    if annotation is None or annotation is ...:
        # e.g. an ellipsis in type hints
        return False

    origin = get_origin(annotation)
    if origin is Union:
        union_args = get_args(annotation)
        # Typically we want the non-NoneType argument
        non_none_args = [arg for arg in union_args if arg is not type(None)]
        # For Optional[T], there's only one non-None type
        if len(non_none_args) == 1:
            origin = non_none_args[0]
    # Check for container types
    if origin in (list, dict, set, tuple, frozenset, type(Union)):
        return True

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return True

    return False


def compose_document(self: Composer) -> Node:
    """Override for internal compose document."""

    self.parser.get_event()  # Drop the DOCUMENT-START event.
    node = self.compose_node(None, None)  # Compose the root node.
    self.parser.get_event()  # Drop the DOCUMENT-END event.
    # self.anchors = {}    # see https://stackoverflow.com/a/44913652/182469
    return node


def include_constructor(loader: RoundTripConstructor, node: Node) -> Any:
    """Process include constructor."""

    parent = cast(YAML, loader.loader)

    child = YAML(typ=parent.typ[0], pure=parent.pure)
    child.composer.anchors = loader.composer.anchors

    return load_include(node.value, child.load)


# configure YAML to support include
yaml = YAML(typ="rt", pure=True)  # rt loader is "safe"
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.preserve_quotes = True  # type: ignore
yaml.Composer.compose_document = compose_document  # type: ignore
yaml.Constructor.add_constructor("!include", include_constructor)


class ConfigError(Exception):
    """Configuration Error."""


T = TypeVar("T", bound="Configuration")


class Configuration(BaseModel):
    """
    Configuration Base Model.

    When creating derived classes, optionally set the following attributes:

    - ``_FILENAME``: Default filename to use when saving configuration for the first time.
      This can be templated to depend upon environment and ``XDG_*`` variables.
    - ``_TEMPLATE``: Optional Jinja2 template to use when creating initial configuration files.
    - ``_KEY``: Optional key (e.g. ``kelvin.client``, with dots corresponding to nested levels)
      to access configuration data if nested within a larger structure.
    - ``_FACTORY_NAME``: Optional to use for for class factory.
    - ``_ENV_PREFIX`` can be specified (e.g. ``KELVIN_CLIENT__``) to map
      environment variables at configuration load-time to override loaded values.

    .. note::
        Environment variables _always_ override values loaded from configuration (and defaults).

    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    _FILENAME: ClassVar[Optional[Union[str, Path]]] = None
    _TEMPLATE: ClassVar[Optional[Union[str, Path]]] = None
    _KEY: ClassVar[Optional[str]] = None
    _ENV_PREFIX: ClassVar[Optional[str]] = None

    sites: Dict[str, Dict[str, Any]] = Field({}, description="Site-specific overrides")
    site: Optional[str] = None

    # keep these fields out of __dict__
    __slots__ = ("_filename", "_key", "_data", "_dirty")

    def __init__(
        self,
        values: Optional[Mapping[str, Any]] = None,
        _filename: Optional[Path] = None,
        _site: Optional[str] = None,
        _key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        _data: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialise configuration.

        .. note::

            Usually `Configuration.from_file` is used to load configuration.

        Parameters
        ----------
        values : :obj:`dict`, optional
            Values to load into configuration.
        _filename : :obj:`str` or :obj:`path`, optional
            Filename from which data was loaded (not used directly)
        _site : :obj:`str`, optional
            Optional site name for site-specific configuration (not used directly)
        _key : :obj:`str`, optional
            Optional nesting key (not used directly)
        _data : :obj:`dict`, optional
            Data loaded from round-tripping YAML loader caching comments from
            file source (not used directly).
        **kwargs
            Additional values

        """

        if values is None:
            values = {}

        if _key is ...:
            _key = self._KEY

        # overcome attribute setters for pydantic.BaseModel
        _setattr = partial(object.__setattr__, self)

        _setattr("_filename", _filename)
        _setattr("_key", _key)
        _setattr("_data", _data)
        _setattr("_dirty", {*[]})

        sites = values.get("sites", {})

        # load site vars as kwargs
        if _site is not None:
            sites = merge(sites, kwargs.pop("sites", {}))
            try:
                site = sites[_site]
            except KeyError:
                if not kwargs:
                    raise ConfigError(f"Unknown site {_site!r}")
                site = sites[_site] = {}
            kwargs = merge(site, kwargs)
            kwargs["site"] = _site

        env_vars = self._env_vars()
        extra = merge(kwargs, env_vars)

        super().__init__(**merge(values, {"sites": sites}, extra))

        # mark extra values as dirty
        for name, value in flatten(extra, sequence=False):
            if name == "site":
                continue
            self._mark(name)

        # mark non-default values as dirty
        for name, value in self.items():
            if name == "site":
                continue
            if value != self.model_fields[name].default:
                self._mark(name)

    @property
    def filename(self) -> Optional[Path]:
        """Config filename."""

        return self._filename  # type: ignore

    @property
    def key(self) -> Optional[str]:
        """Config key."""

        return self._key  # type: ignore

    @property
    def owner(self) -> Optional[Configuration]:
        """Config owner."""

        return self._owner  # type: ignore

    @property
    def data(self) -> Optional[MutableMapping[str, Any]]:
        """Config data."""

        return self._data  # type: ignore

    @property
    def dirty(self) -> Set[str]:
        """Config data."""

        return self._dirty  # type: ignore

    @classmethod
    def _env_vars(cls) -> Dict[str, Any]:
        """Extract environment variables."""

        env_prefix = cls._ENV_PREFIX

        if env_prefix is None:
            return {}

        # collate prefixed environment variables split on __
        env_vars = inflate(
            [
                (k, json.loads(v) if is_json(v) else v)
                for k, v in (
                    (name.replace(env_prefix, "", 1), value)
                    for name, value in os.environ.items()
                    if name.startswith(env_prefix)
                )
            ],
            separator="__",
        )

        names = [field.alias if field.alias else name for name, field in cls.model_fields.items()]

        return {name: env_vars[name.upper()] for name in names if name.upper() in env_vars}

    def _mark(self, name: str) -> None:
        """Mark name dirty and inform owner."""

        self.dirty.add(name)

        if self.owner:
            self.owner._mark("{self._name}.{name}")

    def _clean(self) -> None:
        """Reset dirty set."""

        self.dirty.clear()

        for value in self.values():
            if isinstance(value, Configuration):
                value._clean()

    def __setattr__(self, name: str, value: Any) -> Any:
        """Set attribute."""

        old_value = self.get(name, ...)
        if old_value == value:
            return old_value

        result = super().__setattr__(name, value)

        if isinstance(value, Mapping):
            for key in value:
                self._mark(f"{name}.{key}")
        else:
            self._mark(name)

        return result

    @classmethod
    def default_path(cls) -> Path:
        """Build default config path from env/XDG; no instance access."""
        fn = cls._FILENAME
        if fn is None:
            raise ConfigError(f"No default filename for {cls.__name__!r}")

        if isinstance(fn, Path):
            return fn.expanduser().resolve()

        xdg_vars = {k: v for k, v in vars(xdg).items() if k.startswith("XDG_")}
        return Path(fn.format_map({**os.environ, **xdg_vars})).expanduser().resolve()

    @classmethod
    def _get_nested(
        cls,
        data: Mapping[str, Any],
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
    ) -> Any:
        """Descend into nested structure."""

        if key is ...:
            key = cls._KEY

        if key is None:
            return data

        try:
            return reduce(lambda x, y: x[y], key.split("."), data)
        except KeyError as e:
            raise ConfigError(f"Level {e!s} not present in configuration: {key}")

    def _build_nested(
        self,
        data: Mapping[str, Any],
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
    ) -> Mapping[str, Any]:
        """Build nested structure."""

        if key is ...:
            key = self.key

        if key is None:
            return data

        return reduce(lambda x, y: {y: x}, key.split("."), data)

    @classmethod
    def _indent_nested(
        cls,
        text: str,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
    ) -> str:
        """Indent nested structure."""

        if key is ...:
            key = cls._KEY

        if key is None:
            return text

        for x in key.split("."):
            text = f"{x}:\n{indent(text, '  ')}"

        return text

    @classmethod
    def _template(cls) -> str:
        """Configuration template."""

        fields = {
            field.alias if field.alias else name: field for name, field in cls.model_fields.items() if name != "site"
        }
        fields["sites"] = fields.pop("sites")  # move to last position

        template = cls._TEMPLATE

        # resolve template
        if isinstance(template, str):
            if "\n" not in template:
                template_resource = pkgutil.get_data(cls.__module__, template)
                if template_resource is None:
                    raise ValueError("Invalid template resource")
                text = template_resource.decode("utf-8")
            else:
                text = dedent(template)
        elif isinstance(template, Path):
            text = template.read_text()
        elif template is None:
            # create basic template
            text = "\n".join(
                (
                    f"{name}:{comment}\n{{{{ {name} }}}}"
                    if is_complex_type(field.annotation) and field.default and field.default is not ...
                    else f"{name}: {{{{ {name} }}}}{comment}"
                )
                for name, field, comment in (
                    (
                        name,
                        field,
                        f"  # {field.description}" if field.description else "",
                    )
                    for name, field in fields.items()
                )
            )
        else:
            raise TypeError(f"Invalid template type {type(template).__name__!r}")

        variables = {}

        for name, field_info in fields.items():
            default_value = field_info.default  # could be None, Ellipsis, or a real value

            # If we interpret "complex" to mean is_complex_field(...) and default is neither None nor Ellipsis
            if (
                is_complex_type(field_info.annotation)
                and default_value
                and not isinstance(field_info.default, PydanticUndefinedType)
            ):
                variables[name] = indent(yamlify(default_value), "  ")
            else:
                # If default is Ellipsis => no default, so treat as None in your code
                actual_value = default_value if not isinstance(field_info.default, PydanticUndefinedType) else None
                variables[name] = jsonify(actual_value)

        try:
            return Template(text, undefined=StrictUndefined).render(**variables)
        except TemplateSyntaxError as e:
            raise ConfigError(f"Invalid config template: {e}")
        except UndefinedError as e:
            raise ConfigError(f"Missing value: {e}")

    @classmethod
    def from_yaml(
        cls: Type[T],
        data: Union[str, IO[Any]],
        site: Optional[str] = None,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        parent: Optional[Union[Mapping[str, Any], T]] = None,
        **kwargs: Any,
    ) -> T:
        """
        Initialise from YAML file.

        Parameters
        ----------
        data : :obj:`str` or file-like
            String or readable file-like.
        site : :obj:`str`, optional
            Optional site name for site-specific configuration
        key : :obj:`str`, optional
            Key under which data has been optionally nested in a larger configuration
            structure.
        parent : :obj:`dict`, optional
            Optional defaults to overlay with data.
        **kwargs
            Additional overrides of values.

        """
        filename = Path(data.name) if not isinstance(data, str) and hasattr(data, "name") else None
        _data = yaml.load(data) or {}

        values = cls._get_nested(_data, key)

        if parent is not None:
            values = merge(parent, values)

        return cls(values, _filename=filename, _site=site, _key=key, _data=_data, **kwargs)

    def to_yaml(
        self,
        file: Optional[IO[Any]] = None,
        comments: bool = True,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        dirty: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """
        Write config to file, preserving comments.

        Parameters
        ----------
        file : file-like, optional
            Writable file-like object. If not provided, function returns string.
        comments : :obj:`bool`, optional
            Include original comments in the output.
        key : :obj:`str`, optional
            Key under which data has been optionally nested in a larger configuration
            structure.

        """

        values = self.dict()
        values.pop("site")

        # separate out "dirty" (non-default) data
        if self.site is not None:
            sites = values.pop("sites", {})
            if dirty is None:
                dirty = {}
            items = flatten(values, sequence=False)
            values = inflate(((k, v) for k, v in items if k not in self.dirty))
            dirty = merge(inflate(((k, v) for k, v in items if k in self.dirty)), dirty)
            values["sites"] = sites
            if self.site not in sites:
                sites[self.site] = dirty
            else:
                update(sites[self.site], dirty)

        data = self._build_nested(values, key)

        if self.data is not None:
            data = update(deepcopy(self.data), data)
            if not comments:
                data = {**data}  # destroy comments by copying data

        if file is None:
            with StringIO() as buffer:
                yaml.dump(data, buffer)
                return buffer.getvalue()

        yaml.dump(data, file)

        return None

    @classmethod
    def from_file(
        cls: Type[T],
        filename: Optional[Union[str, Path, IO[Any]]] = None,
        site: Optional[str] = None,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        parent: Optional[Union[str, Path, IO[Any], T]] = None,
        create: bool = False,
        **kwargs: Any,
    ) -> T:
        """
        Initialise from YAML filename.

        Parameters
        ----------
        filename : :obj:`str` or file-like, optional
            Optional filename or readable file-like. If not provided, data will be read
            from default location (if known).
        site : :obj:`str`, optional
            Optional site name for site-specific configuration
        key : :obj:`str`, optional
            Key under which data has been optionally nested in a larger configuration
            structure.
        parent : :obj:`dict`, optional
            Filename or readable file-like with optional defaults to overlay with data
            from filename.
        create : :obj:`bool`, optional
            Create file from defaults and provided data if filename does not exist.
        **kwargs
            Additional overrides of values.

        """

        if parent is not None and not isinstance(parent, cls):
            parent = cls.from_file(parent, site=site, key=key, parent=None, create=False)  # type: ignore

        # infer filename if not given
        if filename is None:
            filename = cls.default_path()

        if isinstance(filename, str):
            filename = Path(filename)

        file: IO[Any]

        if isinstance(filename, Path):
            filename = filename.expanduser().resolve()

            if not filename.parent.exists():
                filename.parent.mkdir(parents=True)

            if not filename.exists():
                if not create:
                    raise ConfigError(f"Configuration file does not exist: {str(filename)!r}")

                file = StringIO(cls._indent_nested(cls._template(), key))
                file.name = str(filename)
                if site is not None:
                    kwargs = {"sites": {site: kwargs}}
            else:
                file = filename.open("rt")
        elif hasattr(filename, "read"):
            file = filename
            if hasattr(file, "name"):
                filename = Path(file.name).expanduser().resolve()
            else:
                filename = None
        else:
            raise TypeError(f"Invalid file type {type(filename).__name__!r}")

        lock = cast(
            AbstractContextManager,
            FileLock(f"{filename}.lock", timeout=LOCK_TIMEOUT) if isinstance(filename, Path) else nullcontext,
        )
        try:
            with lock:
                # chdir to support !include on relative paths
                with file, chdir(filename):
                    try:
                        result = cls.from_yaml(file, site=site, key=key, parent=parent, **kwargs)
                    except (ConfigError, YAMLError) as e:
                        raise ConfigError(f"Unable to load file {str(filename)!r}: {e}")

                # write out named string buffer
                if isinstance(filename, Path):
                    if create and isinstance(file, StringIO):
                        write = True
                    elif site is not None and not result.sites.get(site):
                        write = True
                    else:
                        write = False

                    if write:
                        result.to_file(filename, key=key, lock=lock)
        except Timeout:
            raise ConfigError(f"Configuration file {str(filename)!r} is locked")

        return result

    def to_file(
        self,
        filename: Optional[Union[str, Path, IO[Any]]] = None,
        comments: bool = True,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        dirty: Optional[Mapping[str, Any]] = None,
        lock: Optional[AbstractContextManager] = None,
    ) -> None:
        """Save to filename."""
        # infer filename if not given
        if filename is None:
            filename = type(self).default_path()

        if isinstance(filename, str):
            filename = Path(filename)

        file: IO[Any]

        if isinstance(filename, Path):
            filename = filename.expanduser().resolve()
            if not filename.parent.exists():
                filename.parent.mkdir(parents=True)
            file = filename.open("wt")
        elif hasattr(filename, "read"):
            file = filename
        else:
            raise TypeError(f"Invalid file type {type(filename).__name__!r}")

        if lock is None:
            lock = cast(
                AbstractContextManager,
                FileLock(f"{filename}.lock", timeout=LOCK_TIMEOUT) if isinstance(filename, Path) else nullcontext,
            )

        try:
            with lock, file:
                self.to_yaml(file, comments=comments, key=key, dirty=dirty)
        except Timeout:
            raise ConfigError(f"Configuration file {str(filename)!r} is locked")

    @classmethod
    def from_dir(
        cls, directory: Optional[Union[str, Path]] = None, pattern: str = "*.yaml", **kwargs: Any
    ) -> List[Configuration]:
        """
        Load all configuration files from directory.

        Parameters
        ----------
        directory : :obj:`str` or :obj:`Path`, optional
            Optional directory. If not provided, data will be read from current directory.
        pattern : :obj:`str`, optional
            Optional filter glob pattern.
        **kwargs
            Optional arguments passed to :ref:`Configuration.from_file`

        """

        if directory is None:
            directory = Path.cwd()

        if isinstance(directory, str):
            directory = Path(directory)

        if isinstance(directory, Path):
            directory = directory.expanduser().resolve()
            if not directory.is_dir():
                raise ValueError(f"{str(directory)!r} is not a directory")

        return [cls.from_file(file, **kwargs) for file in directory.glob(pattern)]

    def _items_pretty_(self) -> Iterator[Tuple[str, Any]]:
        """Pretty items list."""

        # put sites last
        items = sorted(super()._items_pretty_(), key=lambda x: (x[0] == "sites", x))

        if self.filename is not None:
            items += [("_filename", str(relative_to_home(self.filename)))]
        if self.key is not None:
            items += [("_key", self.key)]

        return iter(items)

    def dict(self, **kwargs: Any) -> Any:
        """
        Generate a dictionary representation of the model, optionally specifying which
        fields to include or exclude.
        """

        return lower(super().model_dump(**kwargs))
