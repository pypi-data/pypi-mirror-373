"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Iterator, List, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KIterator, KList

from ..model import requests, response, responses, type


class Timeseries(ApiServiceModel):
    @classmethod
    def create_timeseries(
        cls,
        publish: Optional[bool] = None,
        data: Optional[Union[requests.TimeseriesCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create Time Series Data individually or in bulk for one or more Asset / Data Stream resources.

        <span style="color: #ff0000;font-weight: bold;">WARNING</span> : If a value already
        exists at the defined time, then it will be overwritten with the new payload value.
        The old value will be lost and is not recoverable !

        **Permission Required:** `kelvin.permission.storage.create`.

        ``createTimeseries``: ``POST`` ``/api/v4/timeseries/create``

        Parameters
        ----------
        publish : :obj:`bool`
        data: requests.TimeseriesCreate, optional
        **kwargs:
            Extra parameters for requests.TimeseriesCreate
              - create_timeseries: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/timeseries/create",
            {},
            {"publish": publish},
            {},
            {},
            data,
            "requests.TimeseriesCreate",
            False,
            {"201": None, "207": None, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_timeseries_last(
        cls,
        data: Optional[Union[requests.TimeseriesLastGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> KList[responses.TimeseriesLastGet]:
        """
        Returns a list of Time Series objects and its latest value. The list returned must be filtered by one or more `resources` and optionally on `fields`. This list is not pageable.

        **Permission Required:** `kelvin.permission.storage.read`.

        ``getTimeseriesLast``: ``POST`` ``/api/v4/timeseries/last/get``

        Parameters
        ----------
        data: requests.TimeseriesLastGet, optional
        **kwargs:
            Extra parameters for requests.TimeseriesLastGet
              - get_timeseries_last: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/timeseries/last/get",
            {},
            {},
            {},
            {},
            data,
            "requests.TimeseriesLastGet",
            False,
            {
                "200": List[responses.TimeseriesLastGet],
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
    def list_timeseries(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.TimeseriesList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.TimeseriesData], responses.TimeseriesListPaginatedResponseCursor]:
        """
        Returns a list of Time Series objects and its latest value. The list returned can be optionally restricted to one or more resources and/or sources.

        **Permission Required:** `kelvin.permission.storage.read`.

        ``listTimeseries``: ``POST`` ``/api/v4/timeseries/list``

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
        data: requests.TimeseriesList, optional
        **kwargs:
            Extra parameters for requests.TimeseriesList
              - list_timeseries: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/timeseries/list",
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
            "requests.TimeseriesList",
            False,
            {
                "200": responses.TimeseriesListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.TimeseriesData], responses.TimeseriesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/timeseries/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def download_timeseries_range(
        cls,
        data: Optional[Union[requests.TimeseriesRangeDownload, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Iterator[None]:
        """
        Returns a **CSV file** with Time Series data within the specified time range one or more resources (Asset /Data Stream pairs). Optional to preprocess and aggregate the data on the server using `agg` and `time_bucket` before downloading.

        **Permission Required:** `kelvin.permission.storage.read`'.

        ``downloadTimeseriesRange``: ``POST`` ``/api/v4/timeseries/range/download``

        Parameters
        ----------
        data: requests.TimeseriesRangeDownload, optional
        **kwargs:
            Extra parameters for requests.TimeseriesRangeDownload
              - download_timeseries_range: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/timeseries/range/download",
            {},
            {},
            {},
            {},
            data,
            "requests.TimeseriesRangeDownload",
            False,
            {"200": None, "400": response.Error, "401": response.Error, "500": response.Error},
            True,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_timeseries_range(
        cls,
        data: Optional[Union[requests.TimeseriesRangeGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> KIterator[responses.TimeseriesRangeGet]:
        """
        Returns an array with Time Series data within the specified time range for one or more resources (Asset /Data Stream pairs). Optional to preprocess and aggregate the data on the server using `agg` and `time_bucket` before downloading.

        **Permission Required:** `kelvin.permission.storage.read`.

        ``getTimeseriesRange``: ``POST`` ``/api/v4/timeseries/range/get``

        Parameters
        ----------
        data: requests.TimeseriesRangeGet, optional
        **kwargs:
            Extra parameters for requests.TimeseriesRangeGet
              - get_timeseries_range: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/timeseries/range/get",
            {},
            {},
            {},
            {},
            data,
            "requests.TimeseriesRangeGet",
            False,
            {"200": responses.TimeseriesRangeGet, "400": response.Error, "401": response.Error, "500": response.Error},
            True,
            _dry_run,
            kwargs,
        )
        return result
