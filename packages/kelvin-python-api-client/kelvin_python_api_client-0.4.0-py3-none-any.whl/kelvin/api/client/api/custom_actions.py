"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class CustomActions(ApiServiceModel):
    @classmethod
    def create_custom_action(
        cls,
        data: Optional[Union[requests.CustomActionCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.CustomActionCreate:
        """
        Create Custom Action

        **Permission Required:** `kelvin.permission.custom-actions.create`.

        ``createCustomAction``: ``POST`` ``/api/v4/custom-actions/create``

        Parameters
        ----------
        data: requests.CustomActionCreate, optional
        **kwargs:
            Extra parameters for requests.CustomActionCreate
              - create_custom_action: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/create",
            {},
            {},
            {},
            {},
            data,
            "requests.CustomActionCreate",
            False,
            {
                "201": responses.CustomActionCreate,
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
    def list_custom_actions(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.CustomActionsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.CustomAction], responses.CustomActionsListPaginatedResponseCursor]:
        """
        Returns a list of Custom Action objects. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.custom-actions.read`.

        ``listCustomActions``: ``POST`` ``/api/v4/custom-actions/list``

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
        data: requests.CustomActionsList, optional
        **kwargs:
            Extra parameters for requests.CustomActionsList
              - list_custom_actions: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/list",
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
            "requests.CustomActionsList",
            False,
            {"200": responses.CustomActionsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.CustomAction], responses.CustomActionsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/custom-actions/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_custom_actions_type(
        cls,
        data: Optional[Union[requests.CustomActionsTypeCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.CustomActionsTypeCreate:
        """
        Create a new Custom Action Type.

        **Permission Required:** `kelvin.permission.custom-actions.create`.

        ``createCustomActionsType``: ``POST`` ``/api/v4/custom-actions/types/create``

        Parameters
        ----------
        data: requests.CustomActionsTypeCreate, optional
        **kwargs:
            Extra parameters for requests.CustomActionsTypeCreate
              - create_custom_actions_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/types/create",
            {},
            {},
            {},
            {},
            data,
            "requests.CustomActionsTypeCreate",
            False,
            {
                "201": responses.CustomActionsTypeCreate,
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
    def list_custom_actions_types(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        app_names: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[KList[type.CustomActionType], responses.CustomActionsTypesListPaginatedCursor]:
        """
        Returns a list of Custom Action Type objects. The list can be optionally filtered and sorted on the server before being returned.
        **Permission Required:** `kelvin.permission.custom-actions.read`.

        ``listCustomActionsTypes``: ``GET`` ``/api/v4/custom-actions/types/list``

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
            Search and filter on the list based on the key `name` and `title`. The
            search is case insensitive and will find partial matches as well.
        app_names : :obj:`Sequence[str]`
            Filter the list of custom action types to include only those that are
            currently in use by the specified applications.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/custom-actions/types/list",
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
                "app_names": app_names,
            },
            {},
            {},
            None,
            None,
            False,
            {"200": responses.CustomActionsTypesListPaginatedCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.CustomActionType], responses.CustomActionsTypesListPaginatedCursor],
                cls.fetch(_client, "/api/v4/custom-actions/types/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_custom_action_type(cls, name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Custom Action Type. An error will be returned if there are any current Custom Action linked to the Custom Action Type. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.custom-actions.delete`.

        ``deleteCustomActionType``: ``POST`` ``/api/v4/custom-actions/types/{name}/delete``

        Parameters
        ----------
        name : :obj:`str`, optional
            Custom Action Type key `name` to delete. Case sensitive name.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/types/{name}/delete",
            {"name": name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error, "409": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_custom_actions_type(
        cls, name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.CustomActionsTypeGet:
        """
        Retrieves the parameters of a Custom Action Type.

        **Permission Required:** `kelvin.permission.custom-actions.read`.

        ``getCustomActionsType``: ``GET`` ``/api/v4/custom-actions/types/{name}/get``

        Parameters
        ----------
        name : :obj:`str`, optional
            Custom Action Type key `name` to get. Case sensitive name.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/custom-actions/types/{name}/get",
            {"name": name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.CustomActionsTypeGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_custom_actions_type(
        cls,
        name: str,
        data: Optional[Union[requests.CustomActionsTypeUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.CustomActionsTypeUpdate:
        """
        Updates an existing Custom Action Type with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged. Only the unique identifier `name` can not be changed.

        **Permission Required:** `kelvin.permission.custom-actions.update`.

        ``updateCustomActionsType``: ``POST`` ``/api/v4/custom-actions/types/{name}/update``

        Parameters
        ----------
        name : :obj:`str`, optional
            Custom Action Type key `name` to update. Case sensitive name.
        data: requests.CustomActionsTypeUpdate, optional
        **kwargs:
            Extra parameters for requests.CustomActionsTypeUpdate
              - update_custom_actions_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/types/{name}/update",
            {"name": name},
            {},
            {},
            {},
            data,
            "requests.CustomActionsTypeUpdate",
            False,
            {
                "200": responses.CustomActionsTypeUpdate,
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
    def delete_custom_action(cls, action_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Custom Action.

        **Permission Required:** `kelvin.permission.custom-actions.delete`.

        ``deleteCustomAction``: ``POST`` ``/api/v4/custom-actions/{action_id}/delete``

        Parameters
        ----------
        action_id : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/custom-actions/{action_id}/delete",
            {"action_id": action_id},
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
    def get_custom_action(
        cls, action_id: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.CustomActionGet:
        """
        Get Custom Action

        **Permission Required:** `kelvin.permission.custom-actions.read`.

        ``getCustomAction``: ``GET`` ``/api/v4/custom-actions/{action_id}/get``

        Parameters
        ----------
        action_id : :obj:`str`, optional

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/custom-actions/{action_id}/get",
            {"action_id": action_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.CustomActionGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result
