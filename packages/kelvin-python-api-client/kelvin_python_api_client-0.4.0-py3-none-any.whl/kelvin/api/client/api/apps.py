"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Apps(ApiServiceModel):
    @classmethod
    def list_apps_context(
        cls,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        data: Optional[Union[requests.AppsContextList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.AppsResourceContext], responses.AppsContextListPaginatedResponseCursor]:
        """
        List Apps Contexts

        **Permission Required:** `kelvin.permission.app.read`.

        ``listAppsContext``: ``POST`` ``/api/v4/apps/context/list``

        Parameters
        ----------
        sort_by : :obj:`Sequence[str]`
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
        data: requests.AppsContextList, optional
        **kwargs:
            Extra parameters for requests.AppsContextList
              - list_apps_context: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/context/list",
            {},
            {
                "sort_by": sort_by,
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
            },
            {},
            {},
            data,
            "requests.AppsContextList",
            False,
            {"200": responses.AppsContextListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.AppsResourceContext], responses.AppsContextListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/context/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_app_version(
        cls,
        data: Optional[Union[requests.AppVersionCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionCreate:
        """
        Create App Version

        **Permission Required:** `kelvin.permission.app.create`.

        ``createAppVersion``: ``POST`` ``/api/v4/apps/create``

        Parameters
        ----------
        data: requests.AppVersionCreate, optional
        **kwargs:
            Extra parameters for requests.AppVersionCreate
              - create_app_version: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/create",
            {},
            {},
            {},
            {},
            data,
            "requests.AppVersionCreate",
            False,
            {"201": responses.AppVersionCreate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_apps(
        cls,
        app_names: Optional[Sequence[str]] = None,
        app_types: Optional[Sequence[str]] = None,
        resources: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.AppShort], responses.AppsListPaginatedResponseCursor]:
        """
        Returns a list of Applications based on the provided filters and sort
        options.

        **Permission Required:** `kelvin.permission.app.read`.

        ``listApps``: ``GET`` ``/api/v4/apps/list``

        Parameters
        ----------
        app_names : :obj:`Sequence[str]`
            Filter the results by the provided application names.
        app_types : :obj:`Sequence[str]`
            Application type.
        resources : :obj:`Sequence[str]`
            Filter based on Resource (KRN format) associated with the App.
            Supported KRNs: `asset`.
        search : :obj:`Sequence[str]`
            Search the name or title of the application for the provided string.
        sort_by : :obj:`Sequence[str]`
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

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/list",
            {},
            {
                "app_names": app_names,
                "app_types": app_types,
                "resources": resources,
                "search": search,
                "sort_by": sort_by,
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.AppsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.AppShort], responses.AppsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_app(cls, app_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete App

        **Permission Required:** `kelvin.permission.app.delete`.

        ``deleteApp``: ``POST`` ``/api/v4/apps/{app_name}/delete``

        Parameters
        ----------
        app_name : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/delete",
            {"app_name": app_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_app(cls, app_name: str, _dry_run: bool = False, _client: Any = None) -> responses.AppGet:
        """
        Get details of an Application

        **Permission Required:** `kelvin.permission.app.read`.

        ``getApp``: ``GET`` ``/api/v4/apps/{app_name}/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/{app_name}/get",
            {"app_name": app_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.AppGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def patch_app(
        cls,
        app_name: str,
        data: Optional[Union[requests.AppPatch, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppPatch:
        """
        Update details of an Application. Any parameters that are not provided will
        remain unchanged.

        **Permission Required:** `kelvin.permission.app.update`.

        ``patchApp``: ``POST`` ``/api/v4/apps/{app_name}/patch``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        data: requests.AppPatch, optional
        **kwargs:
            Extra parameters for requests.AppPatch
              - patch_app: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/patch",
            {"app_name": app_name},
            {},
            {},
            {},
            data,
            "requests.AppPatch",
            False,
            {"200": responses.AppPatch, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_app_resources(
        cls,
        app_name: str,
        data: Optional[Union[requests.AppResourcesDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete App Resources

        **Permission Required:** `kelvin.permission.app.update`.

        ``deleteAppResources``: ``POST`` ``/api/v4/apps/{app_name}/resources/delete``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        data: requests.AppResourcesDelete, optional
        **kwargs:
            Extra parameters for requests.AppResourcesDelete
              - delete_app_resources: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/resources/delete",
            {"app_name": app_name},
            {},
            {},
            {},
            data,
            "requests.AppResourcesDelete",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def disable_app_resources(
        cls,
        app_name: str,
        data: Optional[Union[requests.AppResourcesDisable, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Disable App Resources

        **Permission Required:** `kelvin.permission.app.update`.

        ``disableAppResources``: ``POST`` ``/api/v4/apps/{app_name}/resources/disable``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        data: requests.AppResourcesDisable, optional
        **kwargs:
            Extra parameters for requests.AppResourcesDisable
              - disable_app_resources: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/resources/disable",
            {"app_name": app_name},
            {},
            {},
            {},
            data,
            "requests.AppResourcesDisable",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def enable_app_resources(
        cls,
        app_name: str,
        data: Optional[Union[requests.AppResourcesEnable, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Enable App Resources

        **Permission Required:** `kelvin.permission.app.update`.

        ``enableAppResources``: ``POST`` ``/api/v4/apps/{app_name}/resources/enable``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        data: requests.AppResourcesEnable, optional
        **kwargs:
            Extra parameters for requests.AppResourcesEnable
              - enable_app_resources: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/resources/enable",
            {"app_name": app_name},
            {},
            {},
            {},
            data,
            "requests.AppResourcesEnable",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_app_resources(
        cls,
        app_name: str,
        search: Optional[Sequence[str]] = None,
        resources: Optional[Sequence[str]] = None,
        app_versions: Optional[Sequence[str]] = None,
        workload_names: Optional[Sequence[str]] = None,
        enabled: Optional[bool] = None,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.AppResource], responses.AppResourcesListPaginatedResponseCursor]:
        """
        List App Resources

        **Permission Required:** `kelvin.permission.app.read`.

        ``listAppResources``: ``GET`` ``/api/v4/apps/{app_name}/resources/list``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        search : :obj:`Sequence[str]`
        resources : :obj:`Sequence[str]`
        app_versions : :obj:`Sequence[str]`
        workload_names : :obj:`Sequence[str]`
        enabled : :obj:`bool`
        sort_by : :obj:`Sequence[str]`
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

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/{app_name}/resources/list",
            {"app_name": app_name},
            {
                "search": search,
                "resources": resources,
                "app_versions": app_versions,
                "workload_names": workload_names,
                "enabled": enabled,
                "sort_by": sort_by,
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.AppResourcesListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.AppResource], responses.AppResourcesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/{app_name}/resources/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_app_version(cls, app_name: str, app_version: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete App Version

        **Permission Required:** `kelvin.permission.app.delete`.

        ``deleteAppVersion``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/delete``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/delete",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            None,
            None,
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def deploy_app_version(
        cls,
        app_name: str,
        app_version: str,
        data: Optional[Union[requests.AppVersionDeploy, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionDeploy:
        """
        Deploy App Version

        Issues the deployment of workloads based on the specified instructions.

        The `deployment` section defines the strategy to deploy the application to
        resources (i.e. assets) by creating the necessary workloads based on the
        maximum number of resources each instance can handle, as well as the target
        cluster where the workloads will be deployed.

        Each resource (i.e. asset) is defined in the `runtime` section, which
        includes defining its parameters and data stream mappings.

        The `parameters` section is optional. If provided, it will update all
        parameters for that resource with the provided values, otherwise, the
        current ones will be injected into the new workloads. If `parameters` is
        set and a parameter is not defined, the current value will be deleted,
        effectively setting it to the default value. This behaviour means that
        setting `parameters` to an empty object (`{}`) will reset all parameters of
        that resource to their default values.

        **Permission Required:** `kelvin.permission.app.deploy`.

        ``deployAppVersion``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/deploy``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        data: requests.AppVersionDeploy, optional
        **kwargs:
            Extra parameters for requests.AppVersionDeploy
              - deploy_app_version: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/deploy",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            data,
            "requests.AppVersionDeploy",
            False,
            {"200": responses.AppVersionDeploy, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_app_version(
        cls, app_name: str, app_version: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.AppVersionGet:
        """
        Get App Version

        **Permission Required:** `kelvin.permission.app.read`.

        ``getAppVersion``: ``GET`` ``/api/v4/apps/{app_name}/v/{app_version}/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/{app_name}/v/{app_version}/get",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.AppVersionGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def patch_app_version(
        cls,
        app_name: str,
        app_version: str,
        data: Optional[Union[requests.AppVersionPatch, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionPatch:
        """
        Update App Version

        Partially update the default settings and schemas for an App Version. The
        following keys can be updated individually. If a key is not specified, its
        existing value will remain unchanged. If a key is specified, it will
        completely overwrite the current value for that key and its nested fields.

        - `defaults.deployment.max_resources`
        - `defaults.deployment.deployment_type`
        - `defaults.deployment.target`
        - `defaults.app.configuration`
        - `defaults.app.io_datastream_mapping`
        - `defaults.system`
        - `schemas.parameters`
        - `schemas.configuration`
        - `schemas.io_configuration`

        **Permission Required:** `kelvin.permission.app.update`.

        ``patchAppVersion``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/patch``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        data: requests.AppVersionPatch, optional
        **kwargs:
            Extra parameters for requests.AppVersionPatch
              - patch_app_version: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/patch",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            data,
            "requests.AppVersionPatch",
            False,
            {"200": responses.AppVersionPatch, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def update_app_version(
        cls,
        app_name: str,
        app_version: str,
        data: Optional[Union[requests.AppVersionUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionUpdate:
        """
        Update App Version

        Update the default settings and schemas for an App Version.

        **Permission Required:** `kelvin.permission.app.update`.

        ``updateAppVersion``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        data: requests.AppVersionUpdate, optional
        **kwargs:
            Extra parameters for requests.AppVersionUpdate
              - update_app_version: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/update",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            data,
            "requests.AppVersionUpdate",
            False,
            {"200": responses.AppVersionUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
