"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class Secret(ApiServiceModel):
    @classmethod
    def create_secret(
        cls,
        data: Optional[Union[requests.SecretCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.SecretCreate:
        """
        Create a new Secret.

        Once this is created you can not change or see the value itself from Kelvin API. Retrieval of the value can only be done through an App.

        **Permission Required:** `kelvin.permission.secret.create`.

        ``createSecret``: ``POST`` ``/api/v4/secrets/create``

        Parameters
        ----------
        data: requests.SecretCreate, optional
        **kwargs:
            Extra parameters for requests.SecretCreate
              - create_secret: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/secrets/create",
            {},
            {},
            {},
            {},
            data,
            "requests.SecretCreate",
            False,
            {"201": responses.SecretCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_secrets(
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
    ) -> Union[KList[responses.SecretItem], responses.SecretsListPaginatedResponseCursor]:
        """
        Returns a list of Secrets. The actual Secret itself can not be retrieved here and is only available from an App.

        **Permission Required:** `kelvin.permission.secret.read`.

        ``listSecrets``: ``GET`` ``/api/v4/secrets/list``

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
            "/api/v4/secrets/list",
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
            {"200": responses.SecretsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.SecretItem], responses.SecretsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/secrets/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_secret(cls, secret_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete a Secret. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.secret.delete`.

        ``deleteSecret``: ``POST`` ``/api/v4/secrets/{secret_name}/delete``

        Parameters
        ----------
        secret_name : :obj:`str`, optional
            Secret key `name` to delete. The string can only contain lowercase
            alphanumeric characters and `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/secrets/{secret_name}/delete",
            {"secret_name": secret_name},
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
    def update_secret(
        cls,
        secret_name: str,
        data: Optional[Union[requests.SecretUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.SecretUpdate:
        """
        Update an existing Secret with a new 'value'. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.secret.update`.

        ``updateSecret``: ``POST`` ``/api/v4/secrets/{secret_name}/update``

        Parameters
        ----------
        secret_name : :obj:`str`, optional
            Secret key `name` to update. The string can only contain lowercase
            alphanumeric characters and `-` characters.
        data: requests.SecretUpdate, optional
        **kwargs:
            Extra parameters for requests.SecretUpdate
              - update_secret: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/secrets/{secret_name}/update",
            {"secret_name": secret_name},
            {},
            {},
            {},
            data,
            "requests.SecretUpdate",
            False,
            {"200": responses.SecretUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
