"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class ControlChange(ApiServiceModel):
    @classmethod
    def get_control_change_clustering(
        cls,
        data: Optional[Union[requests.ControlChangeClusteringGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> KList[responses.ControlChangeClustering]:
        """
        Retrieve the total count of Control Changes matching an array of `resources` and filter options between two dates grouped by the parameter `time_bucket`. Will also return a list of all the Control Change `id`s counted.

        **Permission Required:** `kelvin.permission.control_change.read`.

        ``getControlChangeClustering``: ``POST`` ``/api/v4/control-changes/clustering/get``

        Parameters
        ----------
        data: requests.ControlChangeClusteringGet, optional
        **kwargs:
            Extra parameters for requests.ControlChangeClusteringGet
              - get_control_change_clustering: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/clustering/get",
            {},
            {},
            {},
            {},
            data,
            "requests.ControlChangeClusteringGet",
            False,
            {
                "200": List[responses.ControlChangeClustering],
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_control_change(
        cls,
        data: Optional[Union[requests.ControlChangeCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ControlChangeCreate:
        """
        Send a new value to be written to an Asset / Data Stream pair. The Control Change Manager will automatically find which Cluster and Bridge to communicate the change to.

        **Permission Required:** `kelvin.permission.control_change.create`.

        ``createControlChange``: ``POST`` ``/api/v4/control-changes/create``

        Parameters
        ----------
        data: requests.ControlChangeCreate, optional
        **kwargs:
            Extra parameters for requests.ControlChangeCreate
              - create_control_change: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/create",
            {},
            {},
            {},
            {},
            data,
            "requests.ControlChangeCreate",
            False,
            {"201": responses.ControlChangeCreate, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_control_change_last(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ControlChangeLastGet, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ControlChangeGet], responses.ControlChangeLastGetPaginatedResponseCursor]:
        """
        Returns a dictionary with a data property containing an array of latest Control Change objects. Only the latest Control Changes for each `resource` in the request filters will be returned.

        **Permission Required:** `kelvin.permission.control_change.read`.

        ``getControlChangeLast``: ``POST`` ``/api/v4/control-changes/last/get``

        Parameters
        ----------
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
        data: requests.ControlChangeLastGet, optional
        **kwargs:
            Extra parameters for requests.ControlChangeLastGet
              - get_control_change_last: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/last/get",
            {},
            {
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
            data,
            "requests.ControlChangeLastGet",
            False,
            {
                "200": responses.ControlChangeLastGetPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.ControlChangeGet], responses.ControlChangeLastGetPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/control-changes/last/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_control_changes(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ControlChangesList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ControlChangeGet], responses.ControlChangesListPaginatedResponseCursor]:
        """
        Returns a list of Control Change objects for specific Asset / Data Stream pairs or Control Change IDs. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.control_change.read`.

        ``listControlChanges``: ``POST`` ``/api/v4/control-changes/list``

        Parameters
        ----------
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
        data: requests.ControlChangesList, optional
        **kwargs:
            Extra parameters for requests.ControlChangesList
              - list_control_changes: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/list",
            {},
            {
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
            data,
            "requests.ControlChangesList",
            False,
            {"200": responses.ControlChangesListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.ControlChangeGet], responses.ControlChangesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/control-changes/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_control_change_range(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ControlChangeRangeGet, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ControlChangeGet], responses.ControlChangeRangeGetPaginatedResponseCursor]:
        """
        Returns a dictionary with a data property containing an array of Control Changes within a specified time range for all of the `resources` in the `resources` array that match the filter options.

        **Permission Required:** `kelvin.permission.control_change.read`.

        ``getControlChangeRange``: ``POST`` ``/api/v4/control-changes/range/get``

        Parameters
        ----------
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
        data: requests.ControlChangeRangeGet, optional
        **kwargs:
            Extra parameters for requests.ControlChangeRangeGet
              - get_control_change_range: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/range/get",
            {},
            {
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
            data,
            "requests.ControlChangeRangeGet",
            False,
            {
                "200": responses.ControlChangeRangeGetPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.ControlChangeGet], responses.ControlChangeRangeGetPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/control-changes/range/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_control_change(cls, control_change_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Deletes a control change

        **Permission Required:** `kelvin.permission.control_change.delete`.

        ``deleteControlChange``: ``POST`` ``/api/v4/control-changes/{control_change_id}/delete``

        Parameters
        ----------
        control_change_id : :obj:`str`, optional
            A unique randomly generated UUID as the key `id` for the Control
            Change.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/control-changes/{control_change_id}/delete",
            {"control_change_id": control_change_id},
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
    def get_control_change(
        cls, control_change_id: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.ControlChangeGet:
        """
        Retrieves the properties, status and all associated logs of a Control Change.

        **Permission Required:** `kelvin.permission.control_change.read`.

        ``getControlChange``: ``GET`` ``/api/v4/control-changes/{control_change_id}/get``

        Parameters
        ----------
        control_change_id : :obj:`str`, optional
            A unique randomly generated UUID as the key `id` for the Control
            Change.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/control-changes/{control_change_id}/get",
            {"control_change_id": control_change_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ControlChangeGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result
