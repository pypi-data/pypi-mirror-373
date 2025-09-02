"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class DeprecatedAppRegistry(ApiServiceModel):
    @classmethod
    def create_legacy_app(
        cls,
        data: Optional[Union[requests.LegacyAppCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.LegacyAppCreate:
        """
        Create a new App or App Version in the App Registry. A new version will be automatically appended if the App already exists.

        Note : The Kelvin API request is not the recommended way to create an App and will not be documented. Check Kelvin's documentation on the best methods to create Apps.

        Because the Applications have migrated to new types, this endpoint converts
        the legacy type to the current one as shown in the following table:

        | Legacy Type | Current Type |
        |-------------|--------------|
        | `kelvin`    | `app`        |
        | `bridge`    | `importer    |
        | `docker`    | `docker`     |

        **Permission Required:** `kelvin.permission.app_registry.create`.

        ``createLegacyApp``: ``POST`` ``/api/v4/appregistry/create``

        Parameters
        ----------
        data: requests.LegacyAppCreate, optional
        **kwargs:
            Extra parameters for requests.LegacyAppCreate
              - create_legacy_app: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/appregistry/create",
            {},
            {},
            {},
            {},
            data,
            "requests.LegacyAppCreate",
            False,
            {"201": responses.LegacyAppCreate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_legacy_app_registry_apps(
        cls,
        type: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[responses.LegacyAppItem], responses.LegacyAppRegistryAppsListPaginatedResponseCursor]:
        """
        Returns a list of Apps in the App Registry and its parameters. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.app_registry.read`.

        ``listLegacyAppRegistryApps``: ``GET`` ``/api/v4/appregistry/list``

        Parameters
        ----------
        type : :obj:`Sequence[str]`
            A filter on the list based on the key `type`. This type is the
            **legacy type**, mapped from the current App Types.
        search : :obj:`Sequence[str]`
        pagination_type : :obj:`Literal['limits', 'cursor', 'stream']`
            Method of pagination to use for return results where `total_items` is
            greater than `page_size`. `cursor` and `limits` will return one `page`
            of results, `stream` will return all results. ('limits', 'cursor',
            'stream')
        page_size : :obj:`int`
            Number of objects to be returned in each page. Page size can range
            between 1 and 10000 objects.
        page : :obj:`int`
            An integer for the wanted page of results. Used only with
            `pagination_type` set as `limits`.
        next : :obj:`str`
            An alphanumeric string bookmark to indicate where to start for the
            next page. Used only with `pagination_type` set as `cursor`.
        previous : :obj:`str`
            An alphanumeric string bookmark to indicate where to end for the
            previous page. Used only with `pagination_type` set as `cursor`.
        direction : :obj:`Literal['asc', 'desc']`
            Sorting order according to the `sort_by` parameter. ('asc', 'desc')
        sort_by : :obj:`Sequence[str]`

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/appregistry/list",
            {},
            {
                "type": type,
                "search": search,
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.LegacyAppRegistryAppsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.LegacyAppItem], responses.LegacyAppRegistryAppsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/appregistry/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_legacy_app(cls, app_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete all versions of an App in the App Registry. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.app_registry.delete`.

        ``deleteLegacyApp``: ``POST`` ``/api/v4/appregistry/{app_name}/delete``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App Registry App key `name` to delete. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/appregistry/{app_name}/delete",
            {"app_name": app_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_legacy_app_registry_app(
        cls, app_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.LegacyAppRegistryAppGet:
        """
        Retrieve the parameters of an App in the App Registry.

        Because the Applications have migrated to new types, this endpoint converts
        the current type to the legacy one as shown in the following table:

        | Current Type | Legacy Type |
        |--------------|-------------|
        | `app`        | `kelvin`    |
        | `importer`   | `bridge`    |
        | `exporter`   | `bridge`    |
        | `docker`     | `docker`    |

        **Permission Required:** `kelvin.permission.app_registry.read`.

        ``getLegacyAppRegistryApp``: ``GET`` ``/api/v4/appregistry/{app_name}/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App Registry App key `name` to retrieve. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/appregistry/{app_name}/get",
            {"app_name": app_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.LegacyAppRegistryAppGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_legacy_app(
        cls,
        app_name: str,
        data: Optional[Union[requests.LegacyAppUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.LegacyAppUpdate:
        """
        Update an existing App with a new 'title' and/or 'description'. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.app_registry.update`.

        ``updateLegacyApp``: ``POST`` ``/api/v4/appregistry/{app_name}/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App Registry App key `name` to retrieve. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.LegacyAppUpdate, optional
        **kwargs:
            Extra parameters for requests.LegacyAppUpdate
              - update_legacy_app: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/appregistry/{app_name}/update",
            {"app_name": app_name},
            {},
            {},
            {},
            data,
            "requests.LegacyAppUpdate",
            False,
            {"200": responses.LegacyAppUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_legacy_app_version(
        cls, app_name: str, app_version: str, _dry_run: bool = False, _client: Any = None
    ) -> None:
        """
        Permanently one version of an App in the App Registry. All other versions of an App will remain unaffected. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.app_registry.delete`.

        ``deleteLegacyAppVersion``: ``POST`` ``/api/v4/appregistry/{app_name}/versions/{app_version}/delete``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App Registry App key `name` to delete. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        app_version : :obj:`str`, optional
            Version number of the App in the App Registry to delete.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/appregistry/{app_name}/versions/{app_version}/delete",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_legacy_app_version(
        cls, app_name: str, app_version: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.LegacyAppVersionGet:
        """
        Retrieve the parameters of a specific version of an App in the App Registry.

        Because the Applications have migrated to new types, this endpoint converts
        the current type to the legacy one as shown in the following table:

        | Current Type | Legacy Type |
        |--------------|-------------|
        | `app`        | `kelvin`    |
        | `importer`   | `bridge`    |
        | `exporter`   | `bridge`    |
        | `docker`     | `docker`    |

        **Permission Required:** `kelvin.permission.app_registry.read`.

        ``getLegacyAppVersion``: ``GET`` ``/api/v4/appregistry/{app_name}/versions/{app_version}/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App Registry App key `name` to retrieve. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        app_version : :obj:`str`, optional
            Version number of the App in the App Registry to retrieve.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/appregistry/{app_name}/versions/{app_version}/get",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.LegacyAppVersionGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result
