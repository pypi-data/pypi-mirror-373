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


class AppWorkloads(ApiServiceModel):
    @classmethod
    def apply_workloads(
        cls,
        data: Optional[Union[requests.WorkloadsApply, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Initiate final deploy action for the downloaded Workloads. Only valid for Workloads that were previously deployed with the keys `staged` set to true and `instantly_apply` set to false.

        **Permission Required:** `kelvin.permission.workload.update`.

        ``applyWorkloads``: ``POST`` ``/api/v4/apps/workloads/apply``

        Parameters
        ----------
        data: requests.WorkloadsApply, optional
        **kwargs:
            Extra parameters for requests.WorkloadsApply
              - apply_workloads: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/apply",
            {},
            {},
            {},
            {},
            data,
            "requests.WorkloadsApply",
            False,
            {
                "204": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def update_workloads_bulk(
        cls,
        data: Optional[Union[requests.WorkloadsBulkUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update Workloads Bulk

        **Permission Required:** `kelvin.permission.workload.update`.

        ``updateWorkloadsBulk``: ``POST`` ``/api/v4/apps/workloads/bulk/update``

        Parameters
        ----------
        data: requests.WorkloadsBulkUpdate, optional
        **kwargs:
            Extra parameters for requests.WorkloadsBulkUpdate
              - update_workloads_bulk: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/bulk/update",
            {},
            {},
            {},
            {},
            data,
            "requests.WorkloadsBulkUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_workload(
        cls,
        stopped: Optional[bool] = None,
        data: Optional[Union[requests.WorkloadCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.WorkloadCreate:
        """
        Create Workload

        **Permission Required:** `kelvin.permission.workload.create`.

        ``createWorkload``: ``POST`` ``/api/v4/apps/workloads/create``

        Parameters
        ----------
        stopped : :obj:`bool`
            If set to `true`, the workload created will be deployed in a stopped
            state.
        data: requests.WorkloadCreate, optional
        **kwargs:
            Extra parameters for requests.WorkloadCreate
              - create_workload: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/create",
            {},
            {"stopped": stopped},
            {},
            {},
            data,
            "requests.WorkloadCreate",
            False,
            {"201": responses.WorkloadCreate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_workloads(
        cls,
        staged: Optional[bool] = None,
        data: Optional[Union[requests.WorkloadsDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete Workload

        **Permission Required:** `kelvin.permission.workload.delete`.

        ``deleteWorkloads``: ``POST`` ``/api/v4/apps/workloads/delete``

        Parameters
        ----------
        staged : :obj:`bool`
        data: requests.WorkloadsDelete, optional
        **kwargs:
            Extra parameters for requests.WorkloadsDelete
              - delete_workloads: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/delete",
            {},
            {"staged": staged},
            {},
            {},
            data,
            "requests.WorkloadsDelete",
            False,
            {
                "204": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_workloads(
        cls,
        search: Optional[Sequence[str]] = None,
        app_names: Optional[Sequence[str]] = None,
        app_versions: Optional[Sequence[str]] = None,
        app_types: Optional[Sequence[str]] = None,
        cluster_names: Optional[Sequence[str]] = None,
        node_names: Optional[Sequence[str]] = None,
        workload_names: Optional[Sequence[str]] = None,
        resources: Optional[str] = None,
        staged: Optional[bool] = None,
        statuses: Optional[Sequence[str]] = None,
        download_statuses: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[type.WorkloadSummary], responses.WorkloadsListPaginatedResponseCursor]:
        """
        List Workloads

        **Permission Required:** `kelvin.permission.workload.read`.

        ``listWorkloads``: ``GET`` ``/api/v4/apps/workloads/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the keys `name`, `title`
            (Display Name), `app_name` and `cluster_name`. All strings in the
            array are treated as _OR_. The search is case insensitive and will
            find partial matches as well.
        app_names : :obj:`Sequence[str]`
            A filter on the list based on the key `app_name`. The filter is on the
            full name only.
        app_versions : :obj:`Sequence[str]`
            A filter on the list based on the key `app_version`. The filter is on
            the full value only.
        app_types : :obj:`Sequence[str]`
            Filter Workloads by their application types.
        cluster_names : :obj:`Sequence[str]`
            A filter on the list based on the key `cluster_name`. The filter is on
            the full name only.
        node_names : :obj:`Sequence[str]`
            A filter on the list based on the key `node_name`. The filter is on
            the full name only.
        workload_names : :obj:`Sequence[str]`
            A filter on the list based on the key `name`. The filter is on the
            full name only.
        resources : :obj:`str`
            Filter based on Resource (KRN format) associated with the Workload.
            Supported KRNs: `asset`.
        staged : :obj:`bool`
            A filter on the key staged. Using true will only show staged
            workloads, false will show all workloads.
        statuses : :obj:`Sequence[str]`
        download_statuses : :obj:`Sequence[str]`
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
            "/api/v4/apps/workloads/list",
            {},
            {
                "search": search,
                "app_names": app_names,
                "app_versions": app_versions,
                "app_types": app_types,
                "cluster_names": cluster_names,
                "node_names": node_names,
                "workload_names": workload_names,
                "resources": resources,
                "staged": staged,
                "statuses": statuses,
                "download_statuses": download_statuses,
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
            {"200": responses.WorkloadsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.WorkloadSummary], responses.WorkloadsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/workloads/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def start_workloads(
        cls,
        data: Optional[Union[requests.WorkloadsStart, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """

        **Permission Required:** `kelvin.permission.workload.update`.

        ``startWorkloads``: ``POST`` ``/api/v4/apps/workloads/start``

        Parameters
        ----------
        data: requests.WorkloadsStart, optional
        **kwargs:
            Extra parameters for requests.WorkloadsStart
              - start_workloads: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/start",
            {},
            {},
            {},
            {},
            data,
            "requests.WorkloadsStart",
            False,
            {
                "204": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def stop_workloads(
        cls,
        data: Optional[Union[requests.WorkloadsStop, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """

        **Permission Required:** `kelvin.permission.workload.update`.

        ``stopWorkloads``: ``POST`` ``/api/v4/apps/workloads/stop``

        Parameters
        ----------
        data: requests.WorkloadsStop, optional
        **kwargs:
            Extra parameters for requests.WorkloadsStop
              - stop_workloads: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/stop",
            {},
            {},
            {},
            {},
            data,
            "requests.WorkloadsStop",
            False,
            {
                "204": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def download_workload(
        cls, workload_name: str, address: Optional[bool] = None, _dry_run: bool = False, _client: Any = None
    ) -> str:
        """
        Download the Workload package file for offline installation on the Edge
        System. The system automatically generates the file for download if the
        package is not already available.

        **Permission Required:** `kelvin.permission.workload.read`.

        ``downloadWorkload``: ``GET`` ``/api/v4/apps/workloads/{workload_name}/download``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
            Unique identifier `name` of the Workload.
        address : :obj:`bool`
            If true, the endpoint will return a direct URL to the workload package
            file.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/workloads/{workload_name}/download",
            {"workload_name": workload_name},
            {"address": address},
            {},
            {},
            None,
            None,
            False,
            {
                "200": str,
                "202": None,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "409": response.Error,
                "412": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_workload(cls, workload_name: str, _dry_run: bool = False, _client: Any = None) -> responses.WorkloadGet:
        """
        Retrieve the parameters of a Workload.

        **Permission Required:** `kelvin.permission.workload.read`.

        ``getWorkload``: ``GET`` ``/api/v4/apps/workloads/{workload_name}/get``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
            Unique identifier `name` of the Workload.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/workloads/{workload_name}/get",
            {"workload_name": workload_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.WorkloadGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_workload_logs(
        cls,
        workload_name: str,
        tail_lines: Optional[int] = None,
        since_time: Optional[datetime] = None,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> responses.WorkloadLogsGet:
        """
        Get Workload Logs

        **Permission Required:** `kelvin.permission.workload.read`.

        ``getWorkloadLogs``: ``GET`` ``/api/v4/apps/workloads/{workload_name}/logs/get``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
            Unique identifier `name` of the Workload.
        tail_lines : :obj:`int`
            Specify the number of the most recent log lines to retrieve, counting
            backwards from the latest entry.
        since_time : :obj:`datetime`
            UTC time of the starting point for log retrieval, formatted in RFC
            3339.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/workloads/{workload_name}/logs/get",
            {"workload_name": workload_name},
            {"tail_lines": tail_lines, "since_time": since_time},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.WorkloadLogsGet,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "424": response.Error,
                "500": response.Error,
                "501": None,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_workload(
        cls,
        workload_name: str,
        data: Optional[Union[requests.WorkloadUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.WorkloadUpdate:
        """
        Update Workload

        Update the modifiable components of a Workload. The following keys can be
        updated individually. If a key is not specified, its existing value will
        remain unchanged. If a key is specified, it will completely overwrite the
        current value for that key and its nested fields.

        - `app_version`
        - `cluster_name`
        - `node_name`
        - `workload_title`
        - `runtime.resources`
        - `runtime.configuration`
        - `system`

        **Permission Required:** `kelvin.permission.workload.update`.

        ``updateWorkload``: ``POST`` ``/api/v4/apps/workloads/{workload_name}/patch``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
        data: requests.WorkloadUpdate, optional
        **kwargs:
            Extra parameters for requests.WorkloadUpdate
              - update_workload: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/{workload_name}/patch",
            {"workload_name": workload_name},
            {},
            {},
            {},
            data,
            "requests.WorkloadUpdate",
            False,
            {"200": responses.WorkloadUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def add_workload_resources(
        cls,
        workload_name: str,
        data: Optional[Union[requests.WorkloadResourcesAdd, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.WorkloadResourcesAdd:
        """
        Add WorkloadResources

        **Permission Required:** `kelvin.permission.workload.update`.

        ``addWorkloadResources``: ``POST`` ``/api/v4/apps/workloads/{workload_name}/resources/add``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
        data: requests.WorkloadResourcesAdd, optional
        **kwargs:
            Extra parameters for requests.WorkloadResourcesAdd
              - add_workload_resources: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/{workload_name}/resources/add",
            {"workload_name": workload_name},
            {},
            {},
            {},
            data,
            "requests.WorkloadResourcesAdd",
            False,
            {
                "200": responses.WorkloadResourcesAdd,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "409": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def remove_workload_resources(
        cls,
        workload_name: str,
        data: Optional[Union[requests.WorkloadResourcesRemove, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Remove WorkloadResources

        **Permission Required:** `kelvin.permission.workload.update`.

        ``removeWorkloadResources``: ``POST`` ``/api/v4/apps/workloads/{workload_name}/resources/remove``

        Parameters
        ----------
        workload_name : :obj:`str`, optional
        data: requests.WorkloadResourcesRemove, optional
        **kwargs:
            Extra parameters for requests.WorkloadResourcesRemove
              - remove_workload_resources: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/workloads/{workload_name}/resources/remove",
            {"workload_name": workload_name},
            {},
            {},
            {},
            data,
            "requests.WorkloadResourcesRemove",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
