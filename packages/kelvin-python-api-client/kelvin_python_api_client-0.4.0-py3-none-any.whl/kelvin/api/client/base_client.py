"""
Kelvin API Client.
"""

# TODO:
# - dummy email for user

from __future__ import annotations

import json
import re
import zlib
from asyncio import CancelledError
from collections import deque
from datetime import date, datetime, timedelta, timezone
from enum import IntFlag, auto
from functools import reduce
from gzip import GzipFile
from hashlib import sha256
from operator import or_
from pathlib import Path
from time import time
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    ClassVar,
    Deque,
    Dict,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import quote, urlparse

import jwt
import keycloak
import keyring
import requests
import structlog
import urllib3
import xdg
from keycloak.exceptions import KeycloakAuthenticationError
from pydantic import AnyUrl, ConfigDict, Field, ValidationInfo, field_validator, model_validator
from requests import PreparedRequest, Response
from requests.adapters import BaseAdapter, HTTPAdapter
from requests.exceptions import ConnectionError, RequestException
from urllib3.exceptions import InsecureRequestWarning
from websockets.client import connect
from websockets.datastructures import SupportsKeysAndGetItem
from websockets.exceptions import WebSocketException

from .config import Configuration
from .error import APIError, ClientError, LoginError
from .retry import APIRetry
from .serialize import is_json, jsonify
from .utils import duration, get_host_type
from .version import version

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter  # pragma: no cover

logger = structlog.get_logger(__name__)

EllipsisType = type(...)

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class History(NamedTuple):
    """Request history item."""

    url: str
    method: str
    body: Optional[str]
    start: datetime
    end: datetime
    request: PreparedRequest
    response: Response

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Pretty representation."""

        name = type(self).__name__

        with p.group(4, f"{name}(", ")"):
            for i, (k, v) in enumerate(self._asdict().items()):
                if i:
                    p.text(",")
                    p.breakable()
                else:
                    p.breakable("")
                p.text(f"{k}=")
                p.pretty(v.isoformat() if isinstance(v, date) else v)


class ClientConfiguration(Configuration):
    """Configuration for resource client."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    _FILENAME: ClassVar[Optional[str]] = "{XDG_CONFIG_HOME}/kelvin/client.yaml"
    _KEY: ClassVar[Optional[str]] = "client"
    _ENV_PREFIX: ClassVar[Optional[str]] = "KELVIN_CLIENT__"
    metadata: Optional[Dict[str, Any]] = Field(None, description="Cached server metadata")

    @model_validator(mode="before")
    def validate_config(cls, values: Dict[str, Any]) -> Any:
        """Validate client secret field."""
        if "client_id" in values and "client_secret" not in values and "username" not in values:
            values["username"] = values.get("client_id", "kelvin-client")

        if "client_secret" in values and "username" not in values:
            values["username"] = values.get("client_id", "kelvin-client")

        return values

    @field_validator("url", mode="before")
    def check_url(cls, value: Optional[str], validation_info: ValidationInfo) -> str:
        """Validate URL field."""
        values = validation_info.data
        if value is None:
            value = values.get("site")
            if value is None:
                raise TypeError("url must be specified")
        if not re.match(r"\w+://", value):
            value = f"https://{value}"
        if "." not in value:
            value = f"{value}.kelvininc.com"
        if values.get("metadata") is None:
            verify = not bool(re.match(r"\d+\.\d+\.\d+\.\d+$", urlparse(value).netloc))
            try:
                with requests.get(f"{value}/metadata", verify=verify, timeout=15) as response:
                    values["metadata"] = response.json()
            except RequestException:
                values["metadata"] = {}
                raise TypeError("Unable to retrieve metadata")
        return value

    url: AnyUrl = Field(None, description="Base URL of API")

    @field_validator("realm_name", mode="before")
    def check_realm_name(cls, value: Optional[str], validation_info: ValidationInfo) -> Optional[str]:
        """Validate realm field."""
        values = validation_info.data
        if value is None:
            metadata = values.get("metadata")
            value = metadata.get("authentication", {}).get("realm") if metadata is not None else None
            if value is None:
                url = values.get("url")
                if url is None:
                    return ""
                value = values["url"].host.split(".", 1)[0]
        return value

    realm_name: Optional[str] = Field(None, description="KeyCloak realm")
    username: Optional[str] = Field(..., description="User name")
    client_id: Optional[str] = Field("kelvin-client", description="Client ID")
    client_secret: Optional[str] = Field(None, description="Client secret key")

    token: Optional[Dict[str, Any]] = Field(None, description="Access token")

    retries: int = Field(3, description="Number of retries")
    timeout: Union[float, Tuple[float, float]] = Field(
        (6.05, 10.0), description="Request timeout(s) in seconds: (connect, read)"
    )
    gzip: bool = Field(False, description="Use gzip on requests")

    @field_validator("verify", mode="before")
    def validate_verify(cls, value: Optional[bool], validation_info: ValidationInfo) -> Any:
        """Validate verify option."""
        values = validation_info.data
        if value is not None or "url" not in values:
            return value

        return get_host_type(values["url"]) == "domain"

    verify: bool = Field(None, description="Verify SSL/TLS certificates")
    history: int = Field(5, description="Number of requests to retain in history")
    headers: Dict[str, Any] = Field({}, description="Additional headers to add to requests")


class MirrorMode(IntFlag):
    """Mirror modes."""

    NONE = 0
    DUMP = auto()
    LOAD = auto()
    BOTH = DUMP | LOAD


class BaseClient:
    """
    Kelvin API Client.

    Parameters
    ----------
    config : :obj:`ClientConfiguration`, optional
        Configuration object
    password : :obj:`str`, optional
        Password for obtaining access token
    totp : :obj:`str`, optional
        Time-based one-time password
    verbose : :obj:`bool`, optional
        Log requests/responses
    use_keychain : :obj:`bool`, optional
        Store credentials securely in system keychain
    store_token : :obj:`bool`, optional
        Store access token
    login : :obj:`bool`, optional
        Login to API
    mirror : :obj:`str`, optional
        Directory to use for caching mirrored responses (created if not existing)
    mirror_mode : :obj:`MirrorMode`, :obj:`str` or :obj:`list`, optional
        Mode of response mirroring:
            - ``dump``: Save responses in mirror cache
            - ``load``: Load responses from mirror cache (if available)
            - ``both``: Both dump and load
            - ``none``: Do not dump or load
    _adapter : :obj:`requests.adapters.BaseAdapter`, optional
        Optional requests adapter instance (e.g. :obj:`requests.adapters.HTTPAdapter`).
        Useful for testing.

    """

    T = TypeVar("T", bound="BaseClient")
    USER_AGENT: str = f"kelvin-api-client=={version}"

    def __init__(
        self,
        config: Optional[Union[ClientConfiguration, Mapping[str, Any]]] = None,
        url: Optional[AnyUrl] = None,
        username: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        verbose: bool = False,
        use_keychain: bool = True,
        store_token: bool = True,
        login: bool = False,
        mirror: Optional[Union[Path, str]] = None,
        mirror_mode: Union[MirrorMode, str, Sequence[str]] = MirrorMode.NONE,
        _adapter: Optional[BaseAdapter] = None,
    ) -> None:
        """Initialise client."""
        if config is None:
            if url is None:
                raise TypeError("url must be specified")
            if username is None and client_id is None:
                raise TypeError("username or client_id  must be specified")
            elif username is not None:
                config = ClientConfiguration(url=url, username=username)
            elif username is None and client_id is not None:
                if client_secret is not None:
                    config = ClientConfiguration(url=url, client_id=client_id, client_secret=client_secret)
                else:
                    config = ClientConfiguration(url=url, client_id=client_id)
            else:
                config = ClientConfiguration()
        elif not isinstance(config, ClientConfiguration):
            config = ClientConfiguration(**config)

        self.config = config

        if _adapter is None:
            _adapter = HTTPAdapter(max_retries=APIRetry(total=config.retries), pool_connections=50, pool_maxsize=50)

        host = urlparse(str(config.url))

        self._verbose = verbose
        self._history: Deque[History] = deque(maxlen=config.history)

        if isinstance(mirror_mode, str):
            mirror_mode = MirrorMode[mirror_mode.upper()]
        elif isinstance(mirror_mode, Sequence):
            mirror_mode = cast(MirrorMode, reduce(or_, mirror_mode, MirrorMode.NONE))
        elif mirror_mode is None:
            mirror_mode = MirrorMode.BOTH if mirror is not None else MirrorMode.NONE
        elif not isinstance(mirror_mode, MirrorMode):
            raise TypeError(f"Mirror mode must be a string or a list of strings: {mirror_mode!r}")

        if isinstance(mirror, str):
            mirror = Path(mirror)
        elif mirror is None:
            mirror = Path(xdg.XDG_CACHE_HOME, "kelvin", "mirror")
        elif not isinstance(mirror, Path):
            raise TypeError(f"Mirror directory must be a string or path: {mirror!r}")

        mirror = mirror.expanduser().resolve()

        if mirror_mode and not mirror.is_dir():
            try:
                logger.info("Creating mirror directory", path=mirror)
                mirror.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ClientError(f"Unable to create mirror directory: {e}")

        self._mirror = mirror
        self._mirror_mode = mirror_mode

        self._session = requests.Session()
        self._session.auth = lambda x: x
        self._session.adapters.clear()
        self._session.mount(f"{host.scheme}://{host.netloc}", _adapter)

        if not self.config.verify:
            urllib3.disable_warnings(InsecureRequestWarning)

        self._keycloak = keycloak.KeycloakOpenID(
            f"{config.url}/auth/",
            config.realm_name,
            config.client_id,
            config.client_secret,
            verify=self.config.verify,
            custom_headers=self.config.headers,
        )

        self._session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
            }
        )

        self._keyring = keyring.get_keyring() if use_keychain else None
        self._password: Optional[str] = None

        if password is not None:
            self.password = password
        self._token = {**config.token} if config.token is not None else {}
        self._store_token = store_token

        if login:
            self.login(totp=totp)

    @classmethod
    def from_token(
        cls: Type[T],
        token: Union[Mapping[str, Any], str],
        config: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> T:
        """
        Initialise from token.

        Parameters
        ----------
        token : :obj:`dict`
            Keycloak token
        config : :obj:`dict`, optional
            Additional overrides of configuration.
        **kwargs
            Additional arguments for :obj:`ClientConfiguration` and :obj:`Client`

        """

        if isinstance(token, Mapping):
            token = {**token}
        else:
            token = {"access_token": token}

        info = cls._decode_token(token)

        # add missing field
        if "expires_in" not in token:
            token["expires_in"] = info["exp"] - info["iat"]

        issuer = urlparse(info["iss"])
        url = f"{issuer.scheme}://{issuer.netloc}"
        path, *_, realm_name = issuer.path[1:].split("/")
        username = info["preferred_username"]

        config = {**config} if config is not None else {}
        config.update({field: kwargs.pop(field) for field in ClientConfiguration.model_fields if field in kwargs})

        # infer some metadata
        config["metadata"] = {
            "api": {"url": url, "docs": "/api/swagger"},
            "authentication": {"url": url, "realm": realm_name, "path": f"/{path}"},
        }

        return cls(
            ClientConfiguration(
                url=url,
                realm_name=realm_name,
                username=username,
                token=token,
                **config,
            ),
            **kwargs,
        )

    @classmethod
    def from_file(
        cls: Type[T],
        filename: Optional[Union[str, Path, IO[Any]]] = None,
        site: Optional[str] = None,
        key: Optional[Union[str, EllipsisType]] = ...,  # type: ignore
        parent: Optional[Union[str, Path, IO[Any]]] = None,
        create: bool = True,
        config: Optional[Mapping[str, Any]] = None,
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
        parent : :obj:`dict`, optional
            Filename or readable file-like with optional defaults to overlay with data
            from filename.
        key : :obj:`str`, optional
            Key under which data has been optionally nested in a larger configuration
            structure.
        create : :obj:`bool`, optional
            Create file from defaults and provided data if filename does not exist.
        config : :obj:`dict`, optional
            Additional overrides of configuration.
        **kwargs
            Additional arguments for :obj:`ClientConfiguration` and :obj:`Client`

        """

        config = {**config} if config is not None else {}
        config.update({field: kwargs.pop(field) for field in ClientConfiguration.model_fields if field in kwargs})

        return cls(
            ClientConfiguration.from_file(filename, site=site, key=key, parent=parent, create=create, **config),
            **kwargs,
        )

    def _update_headers(self, clear: bool = False) -> None:
        """Update headers for session."""

        if clear:
            try:
                del self._session.headers["Authorization"]
            except KeyError:
                pass
            return

        self._session.headers["Authorization"] = f"Bearer {self._token['access_token']}"

    @property
    def headers(self) -> Dict[str, Union[str, bytes]]:
        """Session headers."""

        return {**self._session.headers}

    @property
    def token(self) -> Dict[str, Any]:
        """Access token."""

        return {**self._token}

    @property
    def password(self) -> Optional[str]:
        """Get password."""

        if self._password is not None or self._keyring is None:
            return self._password

        site = self.config.site
        if site is None:
            return self._password

        site_key = f"kelvin-api-client::{site}"
        self._password = self._keyring.get_password(site_key, self.config.username)

        return self._password

    @password.setter
    def password(self, value: Optional[str]) -> Optional[str]:
        """Set password."""

        if self._keyring is not None:
            site = self.config.site
            if site is not None:
                site_key = f"kelvin-api-client::{site}"
                if value is not None:
                    self._keyring.set_password(site_key, self.config.username, value)
                else:
                    try:
                        self._keyring.delete_password(site_key, self.config.username)
                    except keyring.errors.PasswordDeleteError:
                        pass

        self._password = value

        return value

    @classmethod
    def _decode_token(cls, token: Mapping[str, Any], key: str = "access_token") -> Dict[str, Any]:
        return jwt.decode(token.get(key, ""), options={"verify_signature": False})

    @property
    def last_login(self) -> float:
        """Last login time."""

        try:
            return float(self._decode_token(self._token).get("iat", 0))
        except jwt.DecodeError:
            return 0.0

    def login(
        self,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        client_secret: Optional[str] = None,
        auth_code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        store_token: Optional[bool] = None,
        margin: float = 10.0,
        force: bool = False,
    ) -> None:
        """Perform login, using refresh token if still valid (within margin)."""

        # update pass if given
        if password is not None and password != self.password:
            self.password = password

        if totp is not None:
            force = True

        last_login = self.last_login
        now = time()

        # token should still be valid
        if not force and now < last_login + self._token.get("expires_in", 0) - margin:
            self._update_headers()
            return

        dirty = {}

        if force or now >= last_login + self._token.get("refresh_expires_in", 0) - margin:
            if password is None:
                password = self.password
            if client_secret is None:
                client_secret = self.config.client_secret

            if password is None and client_secret is None and auth_code is None:
                raise LoginError("Password/secret/code required to perform login")

            # refresh metadata
            url = self.config.url
            verify = self.config.verify
            with self._session.get(f"{url}/metadata", verify=verify) as response:
                dirty["metadata"] = self.config.metadata = response.json()

            username = self.config.username
            grant_type = (
                "authorization_code"
                if auth_code is not None
                else "client_credentials" if client_secret is not None else "password"
            )

            try:
                token = self._keycloak.token(
                    username=username,
                    password=password,
                    totp=totp,
                    grant_type=grant_type,
                    code=auth_code,
                    redirect_uri=redirect_uri,
                )
            except KeycloakAuthenticationError:
                raise LoginError("Incorrect credentials")
        else:
            token = self._keycloak.refresh_token(self._token["refresh_token"])

        self._token.clear()
        self._token.update(token)

        if store_token is None:
            store_token = self._store_token

        if store_token and self.config.filename is not None:
            dirty["token"] = {**token, "last_login": self.last_login}
            self.config.to_file(dirty=dirty)

        self._update_headers()

    def logout(self) -> None:
        """Logout from server."""

        self.password = None
        self._update_headers(clear=True)

        refresh_token = self._token.get("refresh_token")
        self._token.clear()
        if refresh_token is None:
            return

        try:
            self._keycloak.logout(refresh_token)
        except keycloak.KeycloakGetError as e:
            logger.warn("Unable to invalidate token", error=e.error_message)

        self.config.to_file(dirty={"token": {"last_login": 0.0}})

    @property
    def user_info(self) -> Dict[str, Any]:
        """Information for logged-in user."""

        token = self._token.get("access_token")
        if token is None:
            self.login()

        return self._keycloak.userinfo(token)

    @property
    def roles(self) -> List[str]:
        """User roles."""

        return sorted(self.user_info["kelvin-roles"])

    @property
    def history(self) -> List[History]:
        """Get request history."""

        return [*self._history]

    @property
    def sites(self) -> List[str]:
        """Known site names."""

        return [*self.config.sites]

    def _path(self, x: str) -> str:
        """Build API path."""

        if re.match(r"\w+://", x):
            return x

        return f"{str(self.config.url).rstrip('/')}/{x.lstrip('/')}"

    def request(
        self,
        path: str,
        method: str,
        data: Any,
        params: Any = None,
        files: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        json: bool = True,
        timeout: Optional[Union[Tuple[float, float], float]] = None,
        verify: Optional[Union[bool, str]] = None,
        gzip: Optional[bool] = None,
        raise_error: bool = True,
        **kwargs: Any,
    ) -> Response:
        """Submit a request to the API."""

        headers = {**headers} if headers is not None else {**self.config.headers}
        if timeout is None:
            timeout = self.config.timeout
        if verify is None:
            verify = self.config.verify
        if gzip is None:
            gzip = self.config.gzip

        method = method.upper()
        url = self._path(path)

        if data is not None:
            if json:
                data = jsonify(data, allow_nan=False, separators=(",", ":"))
                headers["Content-Type"] = "application/json"

            body = data

            if gzip and isinstance(data, str):
                data = zlib.compress(data.encode("utf-8"))
                headers["Content-Encoding"] = "gzip"
        else:
            body = None

        if self._mirror_mode & MirrorMode.LOAD:
            response = self._load_response(url, method, body)

            if response is not None:
                logger.debug("Loaded response from mirror", path=path)
                return response

        self.login()

        # allow one retry after re-authenticating
        attempt = 0
        retries = 0

        while True:
            attempt += 1

            start = datetime.now(timezone.utc)

            try:
                response = self._session.request(
                    method,
                    url,
                    data=data,
                    params=params,
                    files=files,
                    headers=headers,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=False,
                    **kwargs,
                )
            except ConnectionError:
                retries += 1
                logger.debug("Unable to connect", url=url)
                if retries > self.config.retries:
                    raise
                attempt = 0
                continue
            except RequestException:
                logger.error("Unable to complete request", url=url)
                raise

            end = datetime.now(timezone.utc)

            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]

            if attempt < 2 and (
                response.status_code == requests.codes.unauthorized
                or response.is_redirect
                or content_type == "text/html"
            ):
                self.login(force=True)
                continue

            entry = History(url, method, body, start, end, response.request, response)
            if self._verbose:
                logger.debug("Request", **entry._asdict())

            self._history += [entry]

            if raise_error and not response.ok:
                with response:
                    if content_type == "application/json" or is_json(response.text):
                        raise APIError(response)
                    response.raise_for_status()

            if self._mirror_mode & MirrorMode.DUMP:
                self._dump_response(url, method, body, response)

            return response

        raise ClientError("Too many unauthorised requests")

    # mirror handlers
    def _mirror_path(self, url: str, method: str, body: Optional[str]) -> Path:
        """Generate unique storage path."""

        host, *_ = urlparse(url).netloc.split(":", 1)
        name = quote(re.sub(r"^\w+://[^/]+/", "", url).replace("/", "-"))
        key = sha256(body.encode("utf-8")).hexdigest()[:8] if body is not None else ""

        return Path(self._mirror, host, f'{name}+{method}{"@" if key else ""}{key}')

    def _load_response(self, url: str, method: str, body: Optional[str]) -> Optional[Response]:
        """Attempt to retrieve response from mirror cache."""

        path = self._mirror_path(url, method, body)

        if not path.is_file():
            return None

        response = Response()
        response.url = url
        response.status_code = 200
        response.reason = "OK"
        response.encoding = "utf-8"

        with GzipFile(path, "rb") as f:
            response._content = f.read()  # type: ignore

        if is_json(response.text):
            response.headers["Content-Type"] = "application/json"

        return response

    def _dump_response(self, url: str, method: str, body: Any, response: Response) -> None:
        """Save response in mirror cache."""

        path = self._mirror_path(url, method, body)

        if not path.parent.is_dir():
            try:
                logger.info("Creating mirror host directory", path=str(path.parent))
                path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ClientError(f"Unable to create mirror host directory: {e}")

        with GzipFile(path, "wb") as f:
            f.writelines(response.iter_content(1024))

    # convenience aliases
    def get(self, path: str, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a GET request to the API."""

        return self.request(path, "GET", data=None, params=params, **kwargs)

    def delete(self, path: str, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a DELETE request to the API."""

        return self.request(path, "DELETE", data=None, params=params, **kwargs)

    def post(self, path: str, data: Any, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a POST request to the API."""

        return self.request(path, "POST", data=data, params=params, **kwargs)

    def put(self, path: str, data: Any, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a PUT request to the API."""

        return self.request(path, "PUT", data=data, params=params, **kwargs)

    def patch(self, path: str, data: Any, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a PATCH request to the API."""

        return self.request(path, "PATCH", data=data, params=params, **kwargs)

    async def stream(
        self,
        resources: Sequence[str],
        deliver: Union[str, timedelta] = "last",
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream of resource messages."""

        if isinstance(deliver, timedelta):
            deliver = duration(deliver)

        uri = f"wss://{self.config.url.host}/dataflow/ws"

        async for ws in connect(uri, extra_headers=ExtraHeaders(self)):
            logger.info("Websocket connected")

            now = datetime.now(timezone.utc)
            suffix = "Z" if now.microsecond else ".000000Z"

            subscription = {
                "source": "krn:wl:kelvin/client",
                "type": "sub-req",
                "timestamp": now.replace(tzinfo=None).isoformat() + suffix,
                "payload": {
                    "type": "data",
                    "resources": resources,
                    "deliver": deliver,
                },
            }

            try:
                await ws.send(json.dumps(subscription))

                async for message in ws:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        logger.warning("Unable to decode message", message=message)
                        continue

                    timestamp = data.get("timestamp")
                    if isinstance(timestamp, str):
                        try:
                            data["timestamp"] = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
                        except ValueError:
                            logger.warning("Unable to parse timestamp", message=message)
                            continue

                    yield data

            except WebSocketException as e:
                logger.error(f"Websocket error: {e}")
                continue
            except (CancelledError, KeyboardInterrupt):
                logger.info("Websocket stopped")
                break

    def __str__(self) -> str:
        """Return str(self)."""

        name = type(self).__name__

        return f"{name}(url={str(self.config.url)!r})"

    def __repr__(self) -> str:
        """Return repr(self)."""

        return str(self)

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Pretty representation."""

        name = type(self).__name__

        with p.group(4, f"{name}(", ")"):
            p.text(f"url={str(self.config.url)!r}")


class ExtraHeaders(SupportsKeysAndGetItem):
    """Wrapper to keep Authorization header updated for websocket connection."""

    def __init__(self, client: BaseClient) -> None:
        """Initialise header wrapper."""

        self._client = client

    def keys(self) -> Iterable[str]:
        """Keys."""

        return ["Authorization"]

    def __getitem__(self, key: str) -> str:
        """Get item."""

        if key == "Authorization":
            client = self._client
            client.login()

            return cast(str, client.headers[key])

        raise KeyError(key)
