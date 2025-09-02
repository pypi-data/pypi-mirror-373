"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class User(ApiServiceModel):
    @classmethod
    def list_users(
        cls,
        username: Optional[Sequence[str]] = None,
        email: Optional[Sequence[str]] = None,
        name: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.UserItem], responses.UsersListPaginatedResponseCursor]:
        """
        Returns a list of Users and its parameters. The list can be optionally filtered and sorted on the server before being returned.
        **Permission Required:** `kelvin.permission.users.read`.

        ``listUsers``: ``GET`` ``/api/v4/users/list``

        Parameters
        ----------
        username : :obj:`Sequence[str]`
            A filter on the list based on the key `username`. The filter is on the
            full name only. All values in array will be filtered as `OR`. The
            string can only contain lowercase alphanumeric characters and `.`, `_`
            or `-` characters.
        email : :obj:`Sequence[str]`
            A filter on the list based on the key `email`. The search is case
            insensitive and will find partial matches as well. All values in array
            will be filtered as `OR`.
        name : :obj:`Sequence[str]`
            A filter on the list based on the User's `first_name` and `last_name`
            separated by a space. The filter is on exact matches only and is case
            sensitive. All values in array will be filtered as `OR`.
        search : :obj:`Sequence[str]`
            Search Users by key `first_name`, `last_name` or `email`. All values
            in array will be filtered as `OR`. The search is case insensitive and
            will find partial matches as well.
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
            "/api/v4/users/list",
            {},
            {
                "username": username,
                "email": email,
                "name": name,
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
            {"200": responses.UsersListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.UserItem], responses.UsersListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/users/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_user_me(cls, _dry_run: bool = False, _client: Any = None) -> responses.UserMeGet:
        """
        Get Current User

        **Permission Required:** `n/a`.

        ``getUserMe``: ``GET`` ``/api/v4/users/me``

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/users/me",
            {},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.UserMeGet, "400": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def list_user_settings(
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
    ) -> Union[KList[type.UserSetting], responses.UserSettingsListPaginatedResponseCursor]:
        """
        Returns a list of User Settings and its parameters. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.users.read`.

        ``listUserSettings``: ``GET`` ``/api/v4/users/settings/list``

        Parameters
        ----------
        names : :obj:`Sequence[str]`
            Filter User Setting list based on the key `setting_name`.
        search : :obj:`Sequence[str]`
            Search User Setting by key `setting_name`. All values in array will be
            filtered as `OR`. The search is case insensitive and will find partial
            matches as well.
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
            "/api/v4/users/settings/list",
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
            {"200": responses.UserSettingsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.UserSetting], responses.UserSettingsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/users/settings/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_user_settings(cls, setting_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing User Setting. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.users.delete`.

        ``deleteUserSettings``: ``POST`` ``/api/v4/users/settings/{setting_name}/delete``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The User Setting key `setting_name` to delete. The string can only
            contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/users/settings/{setting_name}/delete",
            {"setting_name": setting_name},
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
    def get_user_settings(
        cls, setting_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.UserSettingsGet:
        """
        Retrieve the parameters of a User Setting.

        **Permission Required:** `kelvin.permission.users.read`.

        ``getUserSettings``: ``GET`` ``/api/v4/users/settings/{setting_name}/get``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The User Setting key `setting_name` to get. The string can only
            contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/users/settings/{setting_name}/get",
            {"setting_name": setting_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.UserSettingsGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_user_settings(
        cls,
        setting_name: str,
        data: Optional[Union[requests.UserSettingsUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.UserSettingsUpdate:
        """
        Updates an existing User Setting  `payload` with any new values.

        **Permission Required:** `kelvin.permission.users.update`.

        ``updateUserSettings``: ``POST`` ``/api/v4/users/settings/{setting_name}/update``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The User Setting key `setting_name`. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.UserSettingsUpdate, optional
        **kwargs:
            Extra parameters for requests.UserSettingsUpdate
              - update_user_settings: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/users/settings/{setting_name}/update",
            {"setting_name": setting_name},
            {},
            {},
            {},
            data,
            "requests.UserSettingsUpdate",
            False,
            {"200": responses.UserSettingsUpdate, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_shared_settings(
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
    ) -> Union[KList[type.SharedSetting], responses.SharedSettingsListPaginatedResponseCursor]:
        """
        Returns a list of Shared Settings and its parameters. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.users.read`.

        ``listSharedSettings``: ``GET`` ``/api/v4/users/shared/settings/list``

        Parameters
        ----------
        names : :obj:`Sequence[str]`
            Filter Shared Setting list based on the key `setting_name`.
        search : :obj:`Sequence[str]`
            Search Shared Setting by key `setting_name`. All values in array will
            be filtered as `OR`. The search is case insensitive and will find
            partial matches as well.
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
            "/api/v4/users/shared/settings/list",
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
            {"200": responses.SharedSettingsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.SharedSetting], responses.SharedSettingsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/users/shared/settings/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_shared_settings(cls, setting_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Shared Setting. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.users.delete`.

        ``deleteSharedSettings``: ``POST`` ``/api/v4/users/shared/settings/{setting_name}/delete``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The Shared Setting key `setting_name` to delete. The string can only
            contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/users/shared/settings/{setting_name}/delete",
            {"setting_name": setting_name},
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
    def get_shared_settings(
        cls, setting_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.SharedSettingsGet:
        """
        Retrieve the parameters of a Shared Setting.

        **Permission Required:** `kelvin.permission.users.read`.

        ``getSharedSettings``: ``GET`` ``/api/v4/users/shared/settings/{setting_name}/get``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The Shared Setting key `setting_name` to get. The string can only
            contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/users/shared/settings/{setting_name}/get",
            {"setting_name": setting_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.SharedSettingsGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_shared_settings(
        cls,
        setting_name: str,
        data: Optional[Union[requests.SharedSettingsUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.SharedSettingsUpdate:
        """
        Updates an existing Shared Setting  `payload` with any new values.

        **Permission Required:** `kelvin.permission.users.update`.

        ``updateSharedSettings``: ``POST`` ``/api/v4/users/shared/settings/{setting_name}/update``

        Parameters
        ----------
        setting_name : :obj:`str`, optional
            The Shared Setting key `setting_name`. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.SharedSettingsUpdate, optional
        **kwargs:
            Extra parameters for requests.SharedSettingsUpdate
              - update_shared_settings: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/users/shared/settings/{setting_name}/update",
            {"setting_name": setting_name},
            {},
            {},
            {},
            data,
            "requests.SharedSettingsUpdate",
            False,
            {"200": responses.SharedSettingsUpdate, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_user(cls, user_id: str, _dry_run: bool = False, _client: Any = None) -> responses.UserGet:
        """
        Retrieve the parameters of a User.

        **Permission Required:** `kelvin.permission.users.read`.

        ``getUser``: ``GET`` ``/api/v4/users/{user_id}/get``

        Parameters
        ----------
        user_id : :obj:`str`, optional
            The generated UUID for the User to get.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/users/{user_id}/get",
            {"user_id": user_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.UserGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result
