"""
Kelvin API Client.
"""

from __future__ import annotations

from functools import wraps
from types import FunctionType, MethodType
from typing import Any, Generic, List, Mapping, Type, TypeVar

from .api.app_parameters import AppParameters
from .api.app_workloads import AppWorkloads
from .api.apps import Apps
from .api.asset import Asset
from .api.asset_insights import AssetInsights
from .api.control_change import ControlChange
from .api.custom_actions import CustomActions
from .api.data_quality import DataQuality
from .api.data_tag import DataTag
from .api.datastreams import Datastreams
from .api.deprecated_app_registry import DeprecatedAppRegistry
from .api.deprecated_bridge import DeprecatedBridge
from .api.deprecated_parameters import DeprecatedParameters
from .api.deprecated_workload import DeprecatedWorkload
from .api.filestorage import Filestorage
from .api.guardrails import Guardrails
from .api.instance import Instance
from .api.orchestration import Orchestration
from .api.properties import Properties
from .api.recommendation import Recommendation
from .api.secret import Secret
from .api.thread import Thread
from .api.timeseries import Timeseries
from .api.user import User
from .api.user_authorization import UserAuthorization
from .api_service_model import ApiServiceModel
from .base_client import BaseClient

MODELS: Mapping[str, Type[ApiServiceModel]] = {
    "deprecated_app_registry": DeprecatedAppRegistry,  # type: ignore
    "deprecated_bridge": DeprecatedBridge,  # type: ignore
    "deprecated_parameters": DeprecatedParameters,  # type: ignore
    "deprecated_workload": DeprecatedWorkload,  # type: ignore
    "app_parameters": AppParameters,  # type: ignore
    "app_workloads": AppWorkloads,  # type: ignore
    "apps": Apps,  # type: ignore
    "asset": Asset,  # type: ignore
    "asset_insights": AssetInsights,  # type: ignore
    "control_change": ControlChange,  # type: ignore
    "custom_actions": CustomActions,  # type: ignore
    "data_quality": DataQuality,  # type: ignore
    "data_tag": DataTag,  # type: ignore
    "datastreams": Datastreams,  # type: ignore
    "filestorage": Filestorage,  # type: ignore
    "guardrails": Guardrails,  # type: ignore
    "instance": Instance,  # type: ignore
    "orchestration": Orchestration,  # type: ignore
    "properties": Properties,  # type: ignore
    "recommendation": Recommendation,  # type: ignore
    "secret": Secret,  # type: ignore
    "thread": Thread,  # type: ignore
    "timeseries": Timeseries,  # type: ignore
    "user": User,  # type: ignore
    "user_authorization": UserAuthorization,  # type: ignore
}


T = TypeVar("T", bound=ApiServiceModel)


class DataModelProxy(Generic[T]):
    """Proxy client to data models."""

    def __init__(self, model: Type[T], client: Client) -> None:
        """Initialise resource adaptor."""

        self._model = model
        self._client = client

    def new(self, **kwargs: Any) -> T:
        """New instance."""

        return self._model(self._client, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Map name to method."""

        if name.startswith("_"):
            return super().__getattribute__(name)

        try:
            f = getattr(self._model, name)
        except AttributeError:
            return super().__getattribute__(name)

        if isinstance(f, (FunctionType, MethodType)):

            @wraps(f)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return f(*args, **kwargs, _client=self._client)

            return wrapper

        return super().__getattribute__(name)

    def __dir__(self) -> List[str]:
        """List methods for model."""

        return sorted(
            k
            for k in vars(self._model)
            if not k.startswith("_") and isinstance(getattr(self._model, k), (FunctionType, MethodType))
        )

    def __str__(self) -> str:
        """Return str(self)."""

        return str(self._model)

    def __repr__(self) -> str:
        """Return repr(self)."""

        return repr(self._model)


class Client(BaseClient):
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

    deprecated_app_registry: Type[DeprecatedAppRegistry]
    deprecated_bridge: Type[DeprecatedBridge]
    deprecated_parameters: Type[DeprecatedParameters]
    deprecated_workload: Type[DeprecatedWorkload]
    app_parameters: Type[AppParameters]
    app_workloads: Type[AppWorkloads]
    apps: Type[Apps]
    asset: Type[Asset]
    asset_insights: Type[AssetInsights]
    control_change: Type[ControlChange]
    custom_actions: Type[CustomActions]
    data_quality: Type[DataQuality]
    data_tag: Type[DataTag]
    datastreams: Type[Datastreams]
    filestorage: Type[Filestorage]
    guardrails: Type[Guardrails]
    instance: Type[Instance]
    orchestration: Type[Orchestration]
    properties: Type[Properties]
    recommendation: Type[Recommendation]
    secret: Type[Secret]
    thread: Type[Thread]
    timeseries: Type[Timeseries]
    user: Type[User]
    user_authorization: Type[UserAuthorization]

    def __dir__(self) -> List[str]:
        """Return list of names of the object items/attributes."""

        return [*super().__dir__(), *MODELS]

    def __getattr__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith("_") or name in super().__dir__():
            return super().__getattribute__(name)  # pragma: no cover

        try:
            model = MODELS[name]
        except KeyError:
            return super().__getattribute__(name)

        return DataModelProxy(model, self)
