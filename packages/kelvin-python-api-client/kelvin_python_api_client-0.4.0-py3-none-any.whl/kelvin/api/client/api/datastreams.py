"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Datastreams(ApiServiceModel):
    @classmethod
    def create_bulk_data_stream(
        cls,
        data: Optional[Union[requests.BulkDataStreamCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a list of new Data Streams.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``createBulkDataStream``: ``POST`` ``/api/v4/datastreams/bulk/create``

        Parameters
        ----------
        data: requests.BulkDataStreamCreate, optional
        **kwargs:
            Extra parameters for requests.BulkDataStreamCreate
              - create_bulk_data_stream: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/bulk/create",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataStreamCreate",
            False,
            {
                "201": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_bulk_data_stream(
        cls,
        data: Optional[Union[requests.BulkDataStreamDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete a list of Data Streams.

        **Permission Required:** `kelvin.permission.datastreams.delete`.

        ``deleteBulkDataStream``: ``POST`` ``/api/v4/datastreams/bulk/delete``

        Parameters
        ----------
        data: requests.BulkDataStreamDelete, optional
        **kwargs:
            Extra parameters for requests.BulkDataStreamDelete
              - delete_bulk_data_stream: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/bulk/delete",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataStreamDelete",
            False,
            {
                "200": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_stream_contexts(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.DataStreamContextsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.DataStreamContext], responses.DataStreamContextsListPaginatedResponseCursor]:
        """
        Returns a list of Data Streams, where each stream includes an array of its associated Assets and respective data sources. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``listDataStreamContexts``: ``POST`` ``/api/v4/datastreams/context/list``

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
        data: requests.DataStreamContextsList, optional
        **kwargs:
            Extra parameters for requests.DataStreamContextsList
              - list_data_stream_contexts: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/context/list",
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
            "requests.DataStreamContextsList",
            False,
            {
                "200": responses.DataStreamContextsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.DataStreamContext], responses.DataStreamContextsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datastreams/context/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_data_stream(
        cls,
        data: Optional[Union[requests.DataStreamCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamCreate:
        """
        Create a new Data Stream.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``createDataStream``: ``POST`` ``/api/v4/datastreams/create``

        Parameters
        ----------
        data: requests.DataStreamCreate, optional
        **kwargs:
            Extra parameters for requests.DataStreamCreate
              - create_data_stream: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataStreamCreate",
            False,
            {"201": responses.DataStreamCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_streams_data_types(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.DataStreamDataType], responses.DataStreamsDataTypesListPaginatedResponseCursor]:
        """
        Returns a list of Data Types and its parameters. The Data Types can be optionally filtered and sorted on the server before being returned.

        **Pagination Sortable Columns:** `name`, `title`, `created`, `updated`

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``listDataStreamsDataTypes``: ``GET`` ``/api/v4/datastreams/data-types/list``

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
        search : :obj:`Sequence[str]`

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/data-types/list",
            {},
            {
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
                "search": search,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataStreamsDataTypesListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.DataStreamDataType], responses.DataStreamsDataTypesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datastreams/data-types/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_data_streams(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.DataStreamsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.DataStream], responses.DataStreamsListPaginatedResponseCursor]:
        """
        Returns a list of Data Streams and its parameters. The Data Streams can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``listDataStreams``: ``POST`` ``/api/v4/datastreams/list``

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
        data: requests.DataStreamsList, optional
        **kwargs:
            Extra parameters for requests.DataStreamsList
              - list_data_streams: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/list",
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
            "requests.DataStreamsList",
            False,
            {"200": responses.DataStreamsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.DataStream], responses.DataStreamsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datastreams/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_data_stream_semantic_type(
        cls,
        data: Optional[Union[requests.DataStreamSemanticTypeCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamSemanticTypeCreate:
        """
        Create a new Semantic Type.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``createDataStreamSemanticType``: ``POST`` ``/api/v4/datastreams/semantic-types/create``

        Parameters
        ----------
        data: requests.DataStreamSemanticTypeCreate, optional
        **kwargs:
            Extra parameters for requests.DataStreamSemanticTypeCreate
              - create_data_stream_semantic_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/semantic-types/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataStreamSemanticTypeCreate",
            False,
            {
                "201": responses.DataStreamSemanticTypeCreate,
                "400": response.Error,
                "401": response.Error,
                "409": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_streams_semantic_types(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.DataStreamSemanticType], responses.DataStreamsSemanticTypesListPaginatedResponseCursor]:
        """
        Returns a list of Semantic Types and its parameters. The Semantic Types can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``listDataStreamsSemanticTypes``: ``GET`` ``/api/v4/datastreams/semantic-types/list``

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
        search : :obj:`Sequence[str]`

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/semantic-types/list",
            {},
            {
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
                "search": search,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataStreamsSemanticTypesListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[
                    KList[type.DataStreamSemanticType], responses.DataStreamsSemanticTypesListPaginatedResponseCursor
                ],
                cls.fetch(_client, "/api/v4/datastreams/semantic-types/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_data_stream_semantic_type(
        cls, semantic_type_name: str, _dry_run: bool = False, _client: Any = None
    ) -> None:
        """
        Permanently delete an existing Semantic Type. An error will be returned if there are any current links to a Semantic Type. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``deleteDataStreamSemanticType``: ``POST`` ``/api/v4/datastreams/semantic-types/{semantic_type_name}/delete``

        Parameters
        ----------
        semantic_type_name : :obj:`str`, optional
            Semantic Type key `name` to delete. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/semantic-types/{semantic_type_name}/delete",
            {"semantic_type_name": semantic_type_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error, "409": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_data_stream_semantic_type(
        cls, semantic_type_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.DataStreamSemanticTypeGet:
        """
        Retrieve the parameters of a Semantic Type.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``getDataStreamSemanticType``: ``GET`` ``/api/v4/datastreams/semantic-types/{semantic_type_name}/get``

        Parameters
        ----------
        semantic_type_name : :obj:`str`, optional
            Semantic Type key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/semantic-types/{semantic_type_name}/get",
            {"semantic_type_name": semantic_type_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataStreamSemanticTypeGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_data_stream_semantic_type(
        cls,
        semantic_type_name: str,
        data: Optional[Union[requests.DataStreamSemanticTypeUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamSemanticTypeUpdate:
        """
        Updates an existing Semantic Type with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``updateDataStreamSemanticType``: ``POST`` ``/api/v4/datastreams/semantic-types/{semantic_type_name}/update``

        Parameters
        ----------
        semantic_type_name : :obj:`str`, optional
            Semantic Type key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.DataStreamSemanticTypeUpdate, optional
        **kwargs:
            Extra parameters for requests.DataStreamSemanticTypeUpdate
              - update_data_stream_semantic_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/semantic-types/{semantic_type_name}/update",
            {"semantic_type_name": semantic_type_name},
            {},
            {},
            {},
            data,
            "requests.DataStreamSemanticTypeUpdate",
            False,
            {
                "201": responses.DataStreamSemanticTypeUpdate,
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
    def create_bulk_data_stream_unit(
        cls,
        data: Optional[Union[requests.BulkDataStreamUnitCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a list of new Units.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``createBulkDataStreamUnit``: ``POST`` ``/api/v4/datastreams/units/bulk/create``

        Parameters
        ----------
        data: requests.BulkDataStreamUnitCreate, optional
        **kwargs:
            Extra parameters for requests.BulkDataStreamUnitCreate
              - create_bulk_data_stream_unit: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/units/bulk/create",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataStreamUnitCreate",
            False,
            {"201": None, "207": None, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_data_stream_unit(
        cls,
        data: Optional[Union[requests.DataStreamUnitCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamUnitCreate:
        """
        Create a new Unit.

        **Permission Required:** `kelvin.permission.datastreams.create`.

        ``createDataStreamUnit``: ``POST`` ``/api/v4/datastreams/units/create``

        Parameters
        ----------
        data: requests.DataStreamUnitCreate, optional
        **kwargs:
            Extra parameters for requests.DataStreamUnitCreate
              - create_data_stream_unit: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/units/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataStreamUnitCreate",
            False,
            {
                "201": responses.DataStreamUnitCreate,
                "400": response.Error,
                "401": response.Error,
                "409": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_streams_units(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.Unit], responses.DataStreamsUnitsListPaginatedResponseCursor]:
        """
        Returns a list of Units and its parameters. The Units can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``listDataStreamsUnits``: ``GET`` ``/api/v4/datastreams/units/list``

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
        search : :obj:`Sequence[str]`

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/units/list",
            {},
            {
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
                "search": search,
            },
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataStreamsUnitsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.Unit], responses.DataStreamsUnitsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datastreams/units/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_data_stream_unit(cls, unit_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Unit. An error will be returned if there are any current links to a Unit. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.datastreams.delete`.

        ``deleteDataStreamUnit``: ``POST`` ``/api/v4/datastreams/units/{unit_name}/delete``

        Parameters
        ----------
        unit_name : :obj:`str`, optional
            Unit key `name` to delete. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/units/{unit_name}/delete",
            {"unit_name": unit_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error, "409": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_data_stream_unit(
        cls, unit_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.DataStreamUnitGet:
        """
        Retrieve the parameters of a Unit.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``getDataStreamUnit``: ``GET`` ``/api/v4/datastreams/units/{unit_name}/get``

        Parameters
        ----------
        unit_name : :obj:`str`, optional
            Unit parameter `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/units/{unit_name}/get",
            {"unit_name": unit_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.DataStreamUnitGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_data_stream_unit(
        cls,
        unit_name: str,
        data: Optional[Union[requests.DataStreamUnitUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamUnitUpdate:
        """
        Updates an existing Unit with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.datastreams.update`.

        ``updateDataStreamUnit``: ``POST`` ``/api/v4/datastreams/units/{unit_name}/update``

        Parameters
        ----------
        unit_name : :obj:`str`, optional
            Unit parameter `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.DataStreamUnitUpdate, optional
        **kwargs:
            Extra parameters for requests.DataStreamUnitUpdate
              - update_data_stream_unit: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/units/{unit_name}/update",
            {"unit_name": unit_name},
            {},
            {},
            {},
            data,
            "requests.DataStreamUnitUpdate",
            False,
            {
                "200": responses.DataStreamUnitUpdate,
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
    def get_data_stream_context(
        cls, datastream_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.DataStreamContextGet:
        """
        Retrieve an array of Assets and respective data sources contextualized within a specific Data Stream.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``getDataStreamContext``: ``GET`` ``/api/v4/datastreams/{datastream_name}/context/get``

        Parameters
        ----------
        datastream_name : :obj:`str`, optional
            Data Stream key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/{datastream_name}/context/get",
            {"datastream_name": datastream_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataStreamContextGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def delete_data_stream(cls, datastream_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Data Stream. You will no longer be able to access any data saved in Asset / Data Stream pairs. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.datastreams.delete`.

        ``deleteDataStream``: ``POST`` ``/api/v4/datastreams/{datastream_name}/delete``

        Parameters
        ----------
        datastream_name : :obj:`str`, optional
            Data Stream key `name` to delete. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/{datastream_name}/delete",
            {"datastream_name": datastream_name},
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
    def get_data_stream(
        cls, datastream_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.DataStreamGet:
        """
        Retrieve the parameters of a Data Stream.

        **Permission Required:** `kelvin.permission.datastreams.read`.

        ``getDataStream``: ``GET`` ``/api/v4/datastreams/{datastream_name}/get``

        Parameters
        ----------
        datastream_name : :obj:`str`, optional
            Data Stream key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datastreams/{datastream_name}/get",
            {"datastream_name": datastream_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.DataStreamGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_data_stream(
        cls,
        datastream_name: str,
        data: Optional[Union[requests.DataStreamUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataStreamUpdate:
        """
        Update an existing Data Stream with a new 'title' and/or 'description' and/or 'type' and/or 'semantic_type_name' and/or 'unit_name'. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.datastreams.update`.

        ``updateDataStream``: ``POST`` ``/api/v4/datastreams/{datastream_name}/update``

        Parameters
        ----------
        datastream_name : :obj:`str`, optional
            Data Stream key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.DataStreamUpdate, optional
        **kwargs:
            Extra parameters for requests.DataStreamUpdate
              - update_data_stream: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datastreams/{datastream_name}/update",
            {"datastream_name": datastream_name},
            {},
            {},
            {},
            data,
            "requests.DataStreamUpdate",
            False,
            {"200": responses.DataStreamUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
