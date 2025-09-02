"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, Mapping, Optional, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Filestorage(ApiServiceModel):
    @classmethod
    def list_files(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        data: Optional[Union[requests.FilesList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.FileStorage], responses.FilesListPaginatedCursor]:
        """
        List the files currently present in the filestorage

        **Permission Required:** `kelvin.permission.filestorage.read`.

        ``listFiles``: ``POST`` ``/api/v4/filestorage/list``

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
        data: requests.FilesList, optional
        **kwargs:
            Extra parameters for requests.FilesList
              - list_files: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/filestorage/list",
            {},
            {
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
            "requests.FilesList",
            False,
            {"200": responses.FilesListPaginatedCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.FileStorage], responses.FilesListPaginatedCursor],
                cls.fetch(_client, "/api/v4/filestorage/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def upload_file(
        cls, file: str, metadata: Optional[Dict[str, Any]] = None, _dry_run: bool = False, _client: Any = None
    ) -> responses.FileUpload:
        """
        Upload a file

        **Permission Required:** `kelvin.permission.filestorage.upload`.

        ``uploadFile``: ``POST`` ``/api/v4/filestorage/upload``

        Parameters
        ----------
        file : :obj:`str`, optional
        metadata : :obj:`Dict[str, Any]`

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/filestorage/upload",
            {},
            {},
            {"file": file, "metadata": metadata},
            {},
            None,
            None,
            False,
            {"201": responses.FileUpload, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def delete_file(cls, file_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Deletes the requested file from filestorage

        **Permission Required:** `kelvin.permission.filestorage.delete`.

        ``deleteFile``: ``POST`` ``/api/v4/filestorage/{file_id}/delete``

        Parameters
        ----------
        file_id : :obj:`str`, optional
            UUID of the desired file

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/filestorage/{file_id}/delete",
            {"file_id": file_id},
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
    def download_file(cls, file_id: str, _dry_run: bool = False, _client: Any = None) -> Iterator[bytes]:
        """
        Downloads the requested file

        **Permission Required:** `kelvin.permission.filestorage.download`.

        ``downloadFile``: ``GET`` ``/api/v4/filestorage/{file_id}/download``

        Parameters
        ----------
        file_id : :obj:`str`, optional
            UUID of the desired file

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/filestorage/{file_id}/download",
            {"file_id": file_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": bytes, "400": response.Error, "401": response.Error, "404": response.Error},
            True,
            _dry_run,
        )
        return result

    @classmethod
    def get_file(cls, file_id: str, _dry_run: bool = False, _client: Any = None) -> responses.FileGet:
        """
        Fetches the information for a specific file

        **Permission Required:** `kelvin.permission.filestorage.read`.

        ``getFile``: ``GET`` ``/api/v4/filestorage/{file_id}/get``

        Parameters
        ----------
        file_id : :obj:`str`, optional
            UUID of the desired file

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/filestorage/{file_id}/get",
            {"file_id": file_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.FileGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result
