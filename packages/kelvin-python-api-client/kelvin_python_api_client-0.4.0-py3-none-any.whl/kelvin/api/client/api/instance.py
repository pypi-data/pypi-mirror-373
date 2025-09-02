"""
Kelvin API Client.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Instance(ApiServiceModel):
    @classmethod
    def list_instance_audit_logs(
        cls,
        action: Optional[Sequence[str]] = None,
        user_id: Optional[Sequence[str]] = None,
        namespace: Optional[Sequence[str]] = None,
        identifier: Optional[Sequence[str]] = None,
        username: Optional[Sequence[str]] = None,
        request_id: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        from_date_time: Optional[datetime] = None,
        to_date_time: Optional[datetime] = None,
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
    ) -> Union[KList[responses.InstanceAuditLogGetItem], responses.InstanceAuditLogsListPaginatedResponseCursor]:
        """
        List Audit Log
        **Permission Required:** `kelvin.permission.audit_log.read`.

        ``listInstanceAuditLogs``: ``GET`` ``/api/v4/instance/auditlog/list``

        Parameters
        ----------
        action : :obj:`Sequence[str]`
            A filter on the list based on the key `action`. The filter is on the
            full name only.
        user_id : :obj:`Sequence[str]`
            A filter on the list based on the key `user_id`. The filter is on the
            full name only.
        namespace : :obj:`Sequence[str]`
            A filter on the list based on the key `namespace`. The filter is on
            the full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters. If set, it will override
            acp_name
        identifier : :obj:`Sequence[str]`
            A filter on the list based on the key `identifier`. The filter is on
            the full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters. If set, it will override
            acp_name
        username : :obj:`Sequence[str]`
            A filter on the list based on the key `username`. The filter is on the
            full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters. If set, it will override
            acp_name
        request_id : :obj:`Sequence[str]`
            A filter on the list based on the key `request_id`. The filter is on
            the full name only.
        search : :obj:`Sequence[str]`
            Search Audit Logs by key `action`, `username` or `namespace`. All
            values in array will be filtered as `OR`. The search is case
            insensitive and will find partial matches as well.
        from_date_time : :obj:`datetime`
            Filter actions that occurred at or after this UTC time, formatted in
            RFC 3339.
        to_date_time : :obj:`datetime`
            Filter actions that occurred until or at this UTC time, formatted in
            RFC 3339.
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
            "/api/v4/instance/auditlog/list",
            {},
            {
                "action": action,
                "user_id": user_id,
                "namespace": namespace,
                "identifier": identifier,
                "username": username,
                "request_id": request_id,
                "search": search,
                "from_date_time": from_date_time,
                "to_date_time": to_date_time,
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
                "200": responses.InstanceAuditLogsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.InstanceAuditLogGetItem], responses.InstanceAuditLogsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/instance/auditlog/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_instance_audit_log(
        cls, audit_logger_id: int, _dry_run: bool = False, _client: Any = None
    ) -> responses.InstanceAuditLogGet:
        """
        Get Audit Log

        **Permission Required:** `kelvin.permission.audit_log.read`.

        ``getInstanceAuditLog``: ``GET`` ``/api/v4/instance/auditlog/{audit_logger_id}/get``

        Parameters
        ----------
        audit_logger_id : :obj:`int`, optional
            Unique ID of the Audit Log entry to get.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/instance/auditlog/{audit_logger_id}/get",
            {"audit_logger_id": audit_logger_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.InstanceAuditLogGet, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_instance_settings_kelvin_cluster(
        cls, _dry_run: bool = False, _client: Any = None
    ) -> responses.InstanceSettingsKelvinClusterGet:
        """
        Retrieve the Cluster Instance Settings.

        **Permission Required:** `kelvin.permission.instance.read`.

        ``getInstanceSettingsKelvinCluster``: ``GET`` ``/api/v4/instance/settings/kelvin-cluster/get``

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/instance/settings/kelvin-cluster/get",
            {},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.InstanceSettingsKelvinClusterGet, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_instance_settings_kelvin_cluster(
        cls,
        data: Optional[Union[requests.InstanceSettingsKelvinClusterUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.InstanceSettingsKelvinClusterUpdate:
        """
        Updates an existing Kelvin Cluster Instance Settings with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.instance.update`.

        ``updateInstanceSettingsKelvinCluster``: ``POST`` ``/api/v4/instance/settings/kelvin-cluster/update``

        Parameters
        ----------
        data: requests.InstanceSettingsKelvinClusterUpdate, optional
        **kwargs:
            Extra parameters for requests.InstanceSettingsKelvinClusterUpdate
              - update_instance_settings_kelvin_cluster: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/instance/settings/kelvin-cluster/update",
            {},
            {},
            {},
            {},
            data,
            "requests.InstanceSettingsKelvinClusterUpdate",
            False,
            {
                "200": responses.InstanceSettingsKelvinClusterUpdate,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_instance_settings(
        cls,
        names: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[type.InstanceSettings], responses.InstanceSettingsListPaginatedResponseCursor]:
        """
        List Instance Settings

        **Permission Required:** `kelvin.permission.instance.read`.

        ``listInstanceSettings``: ``GET`` ``/api/v4/instance/settings/list``

        Parameters
        ----------
        names : :obj:`Sequence[str]`
            Filter Instance Setting list based on the key `name`.
        search : :obj:`Sequence[str]`
            Search and filter on the Instance Setting list based on the key
            `name`. The search is case sensitive but will find partial matches
            anywhere in the `name`.
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
            "/api/v4/instance/settings/list",
            {},
            {
                "names": names,
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
                "200": responses.InstanceSettingsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.InstanceSettings], responses.InstanceSettingsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/instance/settings/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_instance_setting(cls, setting_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Instance Setting. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.instance.delete`.

        ``deleteInstanceSetting``: ``POST`` ``/api/v4/instance/settings/{setting_name}/delete``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            Unique identifier `name` of the Instance Setting to delete.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/instance/settings/{setting_name}/delete",
            {"setting_name": setting_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_instance_settings(
        cls, setting_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.InstanceSettingsGet:
        """
        Retrieve the parameters of an Instance Setting.

        **Permission Required:** `kelvin.permission.instance.read`.

        ``getInstanceSettings``: ``GET`` ``/api/v4/instance/settings/{setting_name}/get``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            Unique identifier `name` of the Instance Setting to get.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/instance/settings/{setting_name}/get",
            {"setting_name": setting_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.InstanceSettingsGet, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_instance_settings(
        cls,
        setting_name: str,
        data: Optional[Union[requests.InstanceSettingsUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.InstanceSettingsUpdate:
        """
        Update an existing Instance Settings. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.instance.update`.

        ``updateInstanceSettings``: ``POST`` ``/api/v4/instance/settings/{setting_name}/update``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            Unique identifier `name` of the Instance Setting to update.
        data: requests.InstanceSettingsUpdate, optional
        **kwargs:
            Extra parameters for requests.InstanceSettingsUpdate
              - update_instance_settings: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/instance/settings/{setting_name}/update",
            {"setting_name": setting_name},
            {},
            {},
            {},
            data,
            "requests.InstanceSettingsUpdate",
            False,
            {
                "200": responses.InstanceSettingsUpdate,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_instance_status(cls, _dry_run: bool = False, _client: Any = None) -> responses.InstanceStatusGet:
        """
        Retrieve the Health Status of all services on the Instance

        **Permission Required:** `n/a`.

        ``getInstanceStatus``: ``GET`` ``/api/v4/instance/status/get``

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/instance/status/get",
            {},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "201": responses.InstanceStatusGet,
                "400": response.Error,
                "500": response.Error,
                "503": responses.InstanceStatusGet,
            },
            False,
            _dry_run,
        )
        return result
