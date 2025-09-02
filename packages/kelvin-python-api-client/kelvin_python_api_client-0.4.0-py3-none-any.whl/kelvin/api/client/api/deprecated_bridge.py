"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class DeprecatedBridge(ApiServiceModel):
    @classmethod
    def deploy_bridge(
        cls,
        data: Optional[Union[requests.BridgeDeploy, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.BridgeDeploy:
        """
        Deploy a Bridge (Connection) from the App Registry as a Workload to a Cluster/Node.

        **Permission Required:** `kelvin.permission.bridge.create`.

        ``deployBridge``: ``POST`` ``/api/v4/bridges/deploy``

        Parameters
        ----------
        data: requests.BridgeDeploy, optional
        **kwargs:
            Extra parameters for requests.BridgeDeploy
              - deploy_bridge: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/bridges/deploy",
            {},
            {},
            {},
            {},
            data,
            "requests.BridgeDeploy",
            False,
            {
                "201": responses.BridgeDeploy,
                "400": response.Error,
                "401": response.Error,
                "409": response.Error,
                "424": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_bridges(
        cls,
        names: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        cluster_name: Optional[Sequence[str]] = None,
        workload_name: Optional[Sequence[str]] = None,
        status_state: Optional[Sequence[str]] = None,
        app_name: Optional[Sequence[str]] = None,
        app_version: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.BridgeItem], responses.BridgesListPaginatedResponseCursor]:
        """
        Returns a list of Bridges (also known as Connections) and its parameters. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.bridge.read`.

        ``listBridges``: ``GET`` ``/api/v4/bridges/list``

        Parameters
        ----------
        names : :obj:`Sequence[str]`
            A filter on the list based on the key `name`. The filter is on the
            full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the keys `name`, `title`
            (Display Name), `cluster_name`, `node_name` and `workload_name`. All
            strings in the array are treated as `OR`. The search is case
            insensitive and will find partial matches as well.
        cluster_name : :obj:`Sequence[str]`
            A filter on the list based on the key `cluster_name`. The filter is on
            the full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters. If set, it will override
            acp_name
        workload_name : :obj:`Sequence[str]`
            A filter on the list based on the key `workload_name`. The filter is
            on the full name only. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        status_state : :obj:`Sequence[str]`
            A filter on the list based on the key `state` in the `status` object.
            The filter is on the full name only. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        app_name : :obj:`Sequence[str]`
            Unique identifier `name` of the App. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        app_version : :obj:`Sequence[str]`
            App version
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
            "/api/v4/bridges/list",
            {},
            {
                "names": names,
                "search": search,
                "cluster_name": cluster_name,
                "workload_name": workload_name,
                "status_state": status_state,
                "app_name": app_name,
                "app_version": app_version,
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
                "200": responses.BridgesListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.BridgeItem], responses.BridgesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/bridges/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_bridge(cls, bridge_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Bridge (Connection). You will no longer receieve Asset / Data Stream data from the assets associated with the Bridge (Connection). This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.bridge.delete`.

        ``deleteBridge``: ``POST`` ``/api/v4/bridges/{bridge_name}/delete``

        Parameters
        ----------
        bridge_name : :obj:`str`, optional
            Unique identifier `name` of the Bridge (Connection).

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/bridges/{bridge_name}/delete",
            {"bridge_name": bridge_name},
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
                "404": response.Error,
                "500": response.Error,
                "501": None,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_bridge(cls, bridge_name: str, _dry_run: bool = False, _client: Any = None) -> responses.BridgeGet:
        """
        Retrieve the parameters of a Bridge (Connection).

        **Permission Required:** `kelvin.permission.bridge.read`.

        ``getBridge``: ``GET`` ``/api/v4/bridges/{bridge_name}/get``

        Parameters
        ----------
        bridge_name : :obj:`str`, optional
            Unique identifier `name` of the Bridge (Connection).

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/bridges/{bridge_name}/get",
            {"bridge_name": bridge_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.BridgeGet, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def start_bridge(cls, bridge_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Start running the Bridge (Connection).

        **Permission Required:** `kelvin.permission.bridge.update`.

        ``startBridge``: ``GET`` ``/api/v4/bridges/{bridge_name}/start``

        Parameters
        ----------
        bridge_name : :obj:`str`, optional
            Unique identifier `name` of the Bridge (Connection).

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/bridges/{bridge_name}/start",
            {"bridge_name": bridge_name},
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
                "404": response.Error,
                "500": response.Error,
                "501": None,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def stop_bridge(cls, bridge_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Stop running the Bridge (Connection).
        **Permission Required:** `kelvin.permission.bridge.update`.

        ``stopBridge``: ``GET`` ``/api/v4/bridges/{bridge_name}/stop``

        Parameters
        ----------
        bridge_name : :obj:`str`, optional
            Unique identifier `name` of the Bridge (Connection).

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/bridges/{bridge_name}/stop",
            {"bridge_name": bridge_name},
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
                "404": response.Error,
                "500": response.Error,
                "501": None,
            },
            False,
            _dry_run,
        )
        return result
