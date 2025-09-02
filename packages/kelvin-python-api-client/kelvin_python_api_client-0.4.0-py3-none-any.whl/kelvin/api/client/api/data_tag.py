"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class DataTag(ApiServiceModel):
    @classmethod
    def create_data_tag(
        cls,
        data: Optional[Union[requests.DataTagCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataTagCreate:
        """
        Create a new Data Tag event.

        **Permission Required:** `kelvin.permission.datatag.create`.

        ``createDataTag``: ``POST`` ``/api/v4/datatags/create``

        Parameters
        ----------
        data: requests.DataTagCreate, optional
        **kwargs:
            Extra parameters for requests.DataTagCreate
              - create_data_tag: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataTagCreate",
            False,
            {"201": responses.DataTagCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_tag(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.DataTagList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.DataTag], responses.DataTagListPaginatedResponseCursor]:
        """
        Returns a list of Data Tags. The Data Tags can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datatag.read`.

        ``listDataTag``: ``POST`` ``/api/v4/datatags/list``

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
        data: requests.DataTagList, optional
        **kwargs:
            Extra parameters for requests.DataTagList
              - list_data_tag: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/list",
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
            "requests.DataTagList",
            False,
            {"200": responses.DataTagListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.DataTag], responses.DataTagListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datatags/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_tag(
        cls,
        data: Optional[Union[requests.TagCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.TagCreate:
        """
        Create a new Tag.

        **Permission Required:** `kelvin.permission.datatag.create`.

        ``createTag``: ``POST`` ``/api/v4/datatags/tags/create``

        Parameters
        ----------
        data: requests.TagCreate, optional
        **kwargs:
            Extra parameters for requests.TagCreate
              - create_tag: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/create",
            {},
            {},
            {},
            {},
            data,
            "requests.TagCreate",
            False,
            {"201": responses.TagCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_tag(
        cls,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[type.Tag], responses.TagListPaginatedResponseCursor]:
        """
        Returns a list of Tags. The Tags can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.datatag.read`.

        ``listTag``: ``GET`` ``/api/v4/datatags/tags/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the key `name` (Tag Name). All
            values in array will be filtered as `OR`. The search is case
            insensitive and will find partial matches as well.
        names : :obj:`Sequence[str]`
            Filter on the list based on the key `name` (Tag Name). All values in
            array will be filtered as `OR`. The search is case insensitive and is
            on the full Tags `name` only.
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
            "/api/v4/datatags/tags/list",
            {},
            {
                "search": search,
                "names": names,
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
            {"200": responses.TagListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.Tag], responses.TagListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/datatags/tags/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_tag(cls, tag_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Tag. An error will be returned if there are any current links to a DataTag and the Tag will not be deleted.
        **Permission Required:** `kelvin.permission.datatag.delete`.

        ``deleteTag``: ``POST`` ``/api/v4/datatags/tags/{tag_name}/delete``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/{tag_name}/delete",
            {"tag_name": tag_name},
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
    def get_tag(cls, tag_name: str, _dry_run: bool = False, _client: Any = None) -> responses.TagGet:
        """
        Retrieves a Tag.

        **Permission Required:** `kelvin.permission.datatag.read`.

        ``getTag``: ``GET`` ``/api/v4/datatags/tags/{tag_name}/get``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datatags/tags/{tag_name}/get",
            {"tag_name": tag_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.TagGet, "400": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_tag(
        cls,
        tag_name: str,
        data: Optional[Union[requests.TagUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.TagUpdate:
        """
        Update an existing Tag. The Tag key `name` can not be updated.

        **Permission Required:** `kelvin.permission.datatag.update`.

        ``updateTag``: ``POST`` ``/api/v4/datatags/tags/{tag_name}/update``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.
        data: requests.TagUpdate, optional
        **kwargs:
            Extra parameters for requests.TagUpdate
              - update_tag: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/{tag_name}/update",
            {"tag_name": tag_name},
            {},
            {},
            {},
            data,
            "requests.TagUpdate",
            False,
            {"200": responses.TagUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_data_tag(cls, datatag_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Data Tag.
        **Permission Required:** `kelvin.permission.datatag.delete`.

        ``deleteDataTag``: ``POST`` ``/api/v4/datatags/{datatag_id}/delete``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/{datatag_id}/delete",
            {"datatag_id": datatag_id},
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
    def get_data_tag(cls, datatag_id: str, _dry_run: bool = False, _client: Any = None) -> responses.DataTagGet:
        """
        Retrieves a Data Tag.

        **Permission Required:** `kelvin.permission.datatag.read`.

        ``getDataTag``: ``GET`` ``/api/v4/datatags/{datatag_id}/get``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datatags/{datatag_id}/get",
            {"datatag_id": datatag_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.DataTagGet, "400": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_data_tag(
        cls,
        datatag_id: str,
        data: Optional[Union[requests.DataTagUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataTagUpdate:
        """
        Update an existing Data Tag. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.datatag.update`.

        ``updateDataTag``: ``POST`` ``/api/v4/datatags/{datatag_id}/update``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.
        data: requests.DataTagUpdate, optional
        **kwargs:
            Extra parameters for requests.DataTagUpdate
              - update_data_tag: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/{datatag_id}/update",
            {"datatag_id": datatag_id},
            {},
            {},
            {},
            data,
            "requests.DataTagUpdate",
            False,
            {"200": responses.DataTagUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
