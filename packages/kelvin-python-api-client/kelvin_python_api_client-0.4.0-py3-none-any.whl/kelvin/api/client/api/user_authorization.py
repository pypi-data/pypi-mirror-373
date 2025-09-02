"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class UserAuthorization(ApiServiceModel):
    @classmethod
    def create_group(
        cls,
        data: Optional[Union[requests.GroupCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.GroupCreate:
        """
        Creates a group

        **Permission Required:** `kelvin.permission.authorization.create`.

        ``createGroup``: ``POST`` ``/api/v4/authorization/groups/create``

        Parameters
        ----------
        data: requests.GroupCreate, optional
        **kwargs:
            Extra parameters for requests.GroupCreate
              - create_group: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/groups/create",
            {},
            {},
            {},
            {},
            data,
            "requests.GroupCreate",
            False,
            {
                "200": responses.GroupCreate,
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
    def list_groups(
        cls,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
        role_names: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.GroupItem], responses.GroupsListPaginatedResponseCursor]:
        """
        Returns a list of Groups and its parameters. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``listGroups``: ``GET`` ``/api/v4/authorization/groups/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search groups by key `name` or `title`. All values in array will be
            filtered as `OR`. The search is case insensitive and will find partial
            matches as well.
        names : :obj:`Sequence[str]`
            Filter Group list based on the key `name`.
        role_names : :obj:`Sequence[str]`
            Filter Group list based on the key `role_name`.
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
            "/api/v4/authorization/groups/list",
            {},
            {
                "search": search,
                "names": names,
                "role_names": role_names,
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
            {"200": responses.GroupsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.GroupItem], responses.GroupsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/authorization/groups/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_group(cls, group_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a group.

        **Permission Required:** `kelvin.permission.authorization.delete`.

        ``deleteGroup``: ``POST`` ``/api/v4/authorization/groups/{group_name}/delete``

        Parameters
        ----------
        group_name : :obj:`str`, optional
            Fill the group name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/groups/{group_name}/delete",
            {"group_name": group_name},
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
    def get_group(cls, group_name: str, _dry_run: bool = False, _client: Any = None) -> responses.GroupGet:
        """
        Retrieve a Group.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``getGroup``: ``GET`` ``/api/v4/authorization/groups/{group_name}/get``

        Parameters
        ----------
        group_name : :obj:`str`, optional
            Fill the group name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/authorization/groups/{group_name}/get",
            {"group_name": group_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.GroupGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_group(
        cls,
        group_name: str,
        data: Optional[Union[requests.GroupUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.GroupUpdate:
        """
        Update a group.

        **Permission Required:** `kelvin.permission.authorization.update`.

        ``updateGroup``: ``POST`` ``/api/v4/authorization/groups/{group_name}/update``

        Parameters
        ----------
        group_name : :obj:`str`, optional
            Fill the group name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.GroupUpdate, optional
        **kwargs:
            Extra parameters for requests.GroupUpdate
              - update_group: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/groups/{group_name}/update",
            {"group_name": group_name},
            {},
            {},
            {},
            data,
            "requests.GroupUpdate",
            False,
            {"200": responses.GroupUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_role(
        cls,
        data: Optional[Union[requests.RoleCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RoleCreate:
        """
        Creates a role

        **Permission Required:** `kelvin.permission.authorization.create`.

        ``createRole``: ``POST`` ``/api/v4/authorization/roles/create``

        Parameters
        ----------
        data: requests.RoleCreate, optional
        **kwargs:
            Extra parameters for requests.RoleCreate
              - create_role: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/create",
            {},
            {},
            {},
            {},
            data,
            "requests.RoleCreate",
            False,
            {
                "201": responses.RoleCreate,
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
    def list_roles(
        cls,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
        group_names: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.RoleItem], responses.RolesListPaginatedResponseCursor]:
        """
        Returns a list of Roles. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``listRoles``: ``GET`` ``/api/v4/authorization/roles/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search roles by key `name` or `title`. All values in array will be
            filtered as `OR`. The search is case insensitive and will find partial
            matches as well.
        names : :obj:`Sequence[str]`
            Filter Role list based on the key `name`.
        group_names : :obj:`Sequence[str]`
            Filter Role list based on the key `group_name`.
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
            "/api/v4/authorization/roles/list",
            {},
            {
                "search": search,
                "names": names,
                "group_names": group_names,
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
            {"200": responses.RolesListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.RoleItem], responses.RolesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/authorization/roles/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_role(cls, role_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a role.

        **Permission Required:** `kelvin.permission.authorization.delete`.

        ``deleteRole``: ``POST`` ``/api/v4/authorization/roles/{role_name}/delete``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/{role_name}/delete",
            {"role_name": role_name},
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
    def get_role(cls, role_name: str, _dry_run: bool = False, _client: Any = None) -> responses.RoleGet:
        """
        Retrieve a Role.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``getRole``: ``GET`` ``/api/v4/authorization/roles/{role_name}/get``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/authorization/roles/{role_name}/get",
            {"role_name": role_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.RoleGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def create_role_policy(
        cls,
        role_name: str,
        data: Optional[Union[requests.RolePolicyCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RolePolicyCreate:
        """
        Creates a role policy

        **Permission Required:** `kelvin.permission.authorization.create`.

        ``createRolePolicy``: ``POST`` ``/api/v4/authorization/roles/{role_name}/policies/create``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        data: requests.RolePolicyCreate, optional
        **kwargs:
            Extra parameters for requests.RolePolicyCreate
              - create_role_policy: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/{role_name}/policies/create",
            {"role_name": role_name},
            {},
            {},
            {},
            data,
            "requests.RolePolicyCreate",
            False,
            {
                "201": responses.RolePolicyCreate,
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
    def list_role_policies(
        cls,
        role_name: str,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
        resource_types: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.RolePolicy], responses.RolePoliciesListPaginatedResponseCursor]:
        """
        Returns a list of policies for a role. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``listRolePolicies``: ``GET`` ``/api/v4/authorization/roles/{role_name}/policies/list``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        search : :obj:`Sequence[str]`
            Search policies by key `name` or `title`. All values in array will be
            filtered as `OR`. The search is case insensitive and will find partial
            matches as well.
        names : :obj:`Sequence[str]`
            Filter policies list based on the key `name`.
        resource_types : :obj:`Sequence[str]`
            Filter policies list based on the key `resource_types`.
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
            "/api/v4/authorization/roles/{role_name}/policies/list",
            {"role_name": role_name},
            {
                "search": search,
                "names": names,
                "resource_types": resource_types,
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
            {"200": responses.RolePoliciesListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.RolePolicy], responses.RolePoliciesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/authorization/roles/{role_name}/policies/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_role_policy(cls, role_name: str, policy_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a role policy.

        **Permission Required:** `kelvin.permission.authorization.delete`.

        ``deleteRolePolicy``: ``POST`` ``/api/v4/authorization/roles/{role_name}/policies/{policy_name}/delete``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name related to the policy. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        policy_name : :obj:`str`, optional
            Fill the policy name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/{role_name}/policies/{policy_name}/delete",
            {"role_name": role_name, "policy_name": policy_name},
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
    def get_role_policy(
        cls, role_name: str, policy_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.RolePolicyGet:
        """
        Retrieve a Role Policy.

        **Permission Required:** `kelvin.permission.authorization.read`.

        ``getRolePolicy``: ``GET`` ``/api/v4/authorization/roles/{role_name}/policies/{policy_name}/get``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name related to the policy. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        policy_name : :obj:`str`, optional
            Fill the policy name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/authorization/roles/{role_name}/policies/{policy_name}/get",
            {"role_name": role_name, "policy_name": policy_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.RolePolicyGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_role_policy(
        cls,
        role_name: str,
        policy_name: str,
        data: Optional[Union[requests.RolePolicyUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RolePolicyUpdate:
        """
        Update a role policy.

        **Permission Required:** `kelvin.permission.authorization.update`.

        ``updateRolePolicy``: ``POST`` ``/api/v4/authorization/roles/{role_name}/policies/{policy_name}/update``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name related to the policy. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        policy_name : :obj:`str`, optional
            Fill the policy name. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.RolePolicyUpdate, optional
        **kwargs:
            Extra parameters for requests.RolePolicyUpdate
              - update_role_policy: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/{role_name}/policies/{policy_name}/update",
            {"role_name": role_name, "policy_name": policy_name},
            {},
            {},
            {},
            data,
            "requests.RolePolicyUpdate",
            False,
            {"200": responses.RolePolicyUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def update_role(
        cls,
        role_name: str,
        data: Optional[Union[requests.RoleUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RoleUpdate:
        """
        Update a role.

        **Permission Required:** `kelvin.permission.authorization.update`.

        ``updateRole``: ``POST`` ``/api/v4/authorization/roles/{role_name}/update``

        Parameters
        ----------
        role_name : :obj:`str`, optional
            Fill the role name. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        data: requests.RoleUpdate, optional
        **kwargs:
            Extra parameters for requests.RoleUpdate
              - update_role: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/authorization/roles/{role_name}/update",
            {"role_name": role_name},
            {},
            {},
            {},
            data,
            "requests.RoleUpdate",
            False,
            {"200": responses.RoleUpdate, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
