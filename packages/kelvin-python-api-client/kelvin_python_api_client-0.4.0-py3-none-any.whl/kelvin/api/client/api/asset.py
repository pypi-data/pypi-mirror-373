"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Asset(ApiServiceModel):
    @classmethod
    def create_asset_bulk(
        cls,
        dry_run: Optional[bool] = None,
        data: Optional[Union[requests.AssetBulkCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create new Assets.

        **Permission Required:** `kelvin.permission.asset.create`.

        ``createAssetBulk``: ``POST`` ``/api/v4/assets/bulk/create``

        Parameters
        ----------
        dry_run : :obj:`bool`
            Executes a simulated run when set to true, providing feedback without
            altering server data.
        data: requests.AssetBulkCreate, optional
        **kwargs:
            Extra parameters for requests.AssetBulkCreate
              - create_asset_bulk: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/bulk/create",
            {},
            {"dry_run": dry_run},
            {},
            {},
            data,
            "requests.AssetBulkCreate",
            False,
            {
                "201": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_asset_bulk(
        cls,
        data: Optional[Union[requests.AssetBulkDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete a list of existing Assets.

        Permanently delete a list of existing Kelvin Assets. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.asset.delete`.

        ``deleteAssetBulk``: ``POST`` ``/api/v4/assets/bulk/delete``

        Parameters
        ----------
        data: requests.AssetBulkDelete, optional
        **kwargs:
            Extra parameters for requests.AssetBulkDelete
              - delete_asset_bulk: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/bulk/delete",
            {},
            {},
            {},
            {},
            data,
            "requests.AssetBulkDelete",
            False,
            {
                "200": None,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_asset(
        cls,
        data: Optional[Union[requests.AssetCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AssetCreate:
        """
        Create a new Asset.

        **Permission Required:** `kelvin.permission.asset.create`.

        ``createAsset``: ``POST`` ``/api/v4/assets/create``

        Parameters
        ----------
        data: requests.AssetCreate, optional
        **kwargs:
            Extra parameters for requests.AssetCreate
              - create_asset: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/create",
            {},
            {},
            {},
            {},
            data,
            "requests.AssetCreate",
            False,
            {
                "201": responses.AssetCreate,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_assets(
        cls,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
        asset_type_name: Optional[Sequence[str]] = None,
        status_state: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[type.Asset], responses.AssetsListPaginatedResponseCursor]:
        """
        Returns a list of Assets and its parameters. The Assets can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.asset.read`.

        ``listAssets``: ``GET`` ``/api/v4/assets/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the keys `title` (Display Name)
            or `name`. All values in array will be filtered as `OR`. The search is
            case insensitive and will find partial matches as well.
        names : :obj:`Sequence[str]`
            A filter on the list based on the key `name`. The filter is on the
            full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        asset_type_name : :obj:`Sequence[str]`
            A filter on the list based on the key `asset_type_name`. The filter is
            on the full name only. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        status_state : :obj:`Sequence[str]`
            A filter on the list based on the key ['status']['state']. Multiple
            statuses can be given and will be filtered as `OR`. The allowed values
            are: `online`, `offline`, `unknown`.
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
            "/api/v4/assets/list",
            {},
            {
                "search": search,
                "names": names,
                "asset_type_name": asset_type_name,
                "status_state": status_state,
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
                "200": responses.AssetsListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.Asset], responses.AssetsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/assets/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_assets_advanced(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.AssetsAdvancedList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.Asset], responses.AssetsAdvancedListPaginatedResponseCursor]:
        """
        Returns a list of Assets and its parameters. The Assets can be filtered and sorted on the server before being returned. Advanced filter options available for more granular return list.

        **Permission Required:** `kelvin.permission.asset.read`.

        ``listAssetsAdvanced``: ``POST`` ``/api/v4/assets/list``

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
        data: requests.AssetsAdvancedList, optional
        **kwargs:
            Extra parameters for requests.AssetsAdvancedList
              - list_assets_advanced: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/list",
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
            "requests.AssetsAdvancedList",
            False,
            {
                "200": responses.AssetsAdvancedListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.Asset], responses.AssetsAdvancedListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/assets/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_asset_status_count(cls, _dry_run: bool = False, _client: Any = None) -> responses.AssetStatusCountGet:
        """
        Retrieve the total count of Assets grouped by the parameter `status`.

        **Permission Required:** `kelvin.permission.asset.read`.

        ``getAssetStatusCount``: ``GET`` ``/api/v4/assets/status/count/get``

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/assets/status/count/get",
            {},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.AssetStatusCountGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_asset_status_current(cls, _dry_run: bool = False, _client: Any = None) -> responses.AssetStatusCurrentGet:
        """
        Returns a list of all Assets and their current status (`state`).

        **Permission Required:** `kelvin.permission.asset.read`.

        ``getAssetStatusCurrent``: ``GET`` ``/api/v4/assets/status/current/get``

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/assets/status/current/get",
            {},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.AssetStatusCurrentGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def create_asset_type(
        cls,
        data: Optional[Union[requests.AssetTypeCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AssetTypeCreate:
        """
        Create a new Asset Type.

        **Permission Required:** `kelvin.permission.asset_type.create`.

        ``createAssetType``: ``POST`` ``/api/v4/assets/types/create``

        Parameters
        ----------
        data: requests.AssetTypeCreate, optional
        **kwargs:
            Extra parameters for requests.AssetTypeCreate
              - create_asset_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/types/create",
            {},
            {},
            {},
            {},
            data,
            "requests.AssetTypeCreate",
            False,
            {"201": responses.AssetTypeCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_asset_type_bulk(
        cls,
        data: Optional[Union[requests.AssetTypeBulkDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete a list of existing Asset Types.

        Permanently delete a list of existing Kelvin Asset Types. This cannot be undone once the API request has been submitted.

        This command can not delete Kelvin Asset Types that are currently linked to any Kelvin Assets and will return an error 409.

        **Permission Required:** `kelvin.permission.asset_type.delete`.

        ``deleteAssetTypeBulk``: ``POST`` ``/api/v4/assets/types/delete``

        Parameters
        ----------
        data: requests.AssetTypeBulkDelete, optional
        **kwargs:
            Extra parameters for requests.AssetTypeBulkDelete
              - delete_asset_type_bulk: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/types/delete",
            {},
            {},
            {},
            {},
            data,
            "requests.AssetTypeBulkDelete",
            False,
            {
                "200": None,
                "207": None,
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
    def list_asset_types(
        cls,
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
    ) -> Union[KList[type.AssetType], responses.AssetTypesListPaginatedResponseCursor]:
        """
        Returns a list of Asset Types and its parameters. The Asset Types can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.asset_type.read`.

        ``listAssetTypes``: ``GET`` ``/api/v4/assets/types/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the keys `title` (Display Name)
            or `name`. The search is case insensitive and will find partial
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
            "/api/v4/assets/types/list",
            {},
            {
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
            {"200": responses.AssetTypesListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.AssetType], responses.AssetTypesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/assets/types/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_asset_types_advanced(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.AssetTypesAdvancedList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.AssetType], responses.AssetTypesAdvancedListPaginatedResponseCursor]:
        """
        Returns a list of Asset Types and its parameters. The Asset Types can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.asset_type.read`.

        ``listAssetTypesAdvanced``: ``POST`` ``/api/v4/assets/types/list``

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
        data: requests.AssetTypesAdvancedList, optional
        **kwargs:
            Extra parameters for requests.AssetTypesAdvancedList
              - list_asset_types_advanced: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/types/list",
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
            "requests.AssetTypesAdvancedList",
            False,
            {
                "200": responses.AssetTypesAdvancedListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.AssetType], responses.AssetTypesAdvancedListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/assets/types/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_asset_type(cls, asset_type_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Asset Type. An error will be returned if there are any current links to an Asset. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.asset_type.delete`.

        ``deleteAssetType``: ``POST`` ``/api/v4/assets/types/{asset_type_name}/delete``

        Parameters
        ----------
        asset_type_name : :obj:`str`, optional
            Asset Type key `name` to delete. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/types/{asset_type_name}/delete",
            {"asset_type_name": asset_type_name},
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
                "403": response.Error,
                "404": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_asset_type(
        cls, asset_type_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.AssetTypeGet:
        """
        Retrieves the parameters of an Asset Type.
        **Permission Required:** `kelvin.permission.asset_type.read`.

        ``getAssetType``: ``GET`` ``/api/v4/assets/types/{asset_type_name}/get``

        Parameters
        ----------
        asset_type_name : :obj:`str`, optional
            Asset Type key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/assets/types/{asset_type_name}/get",
            {"asset_type_name": asset_type_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.AssetTypeGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_asset_type(
        cls,
        asset_type_name: str,
        data: Optional[Union[requests.AssetTypeUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AssetTypeUpdate:
        """
        Updates an existing Asset Type with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged. Only the unique identifier `name` can not be changed.

        **Permission Required:** `kelvin.permission.asset_type.update`.

        ``updateAssetType``: ``POST`` ``/api/v4/assets/types/{asset_type_name}/update``

        Parameters
        ----------
        asset_type_name : :obj:`str`, optional
            Asset Type key `name` to update. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.AssetTypeUpdate, optional
        **kwargs:
            Extra parameters for requests.AssetTypeUpdate
              - update_asset_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/types/{asset_type_name}/update",
            {"asset_type_name": asset_type_name},
            {},
            {},
            {},
            data,
            "requests.AssetTypeUpdate",
            False,
            {
                "200": responses.AssetTypeUpdate,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "409": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_asset(cls, asset_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Asset. This cannot be undone once the API request has been submitted.

        The data in the Asset /  Data Stream pairs is not deleted and can be recovered if you create the same Asset name again.

        **Permission Required:** `kelvin.permission.asset.delete`.

        ``deleteAsset``: ``POST`` ``/api/v4/assets/{asset_name}/delete``

        Parameters
        ----------
        asset_name : :obj:`str`, optional
            Asset key `name` to delete. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/{asset_name}/delete",
            {"asset_name": asset_name},
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
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_asset(cls, asset_name: str, _dry_run: bool = False, _client: Any = None) -> responses.AssetGet:
        """
        Retrieve the parameters of an Asset.

        **Permission Required:** `kelvin.permission.asset.read`.

        ``getAsset``: ``GET`` ``/api/v4/assets/{asset_name}/get``

        Parameters
        ----------
        asset_name : :obj:`str`, optional
            Asset key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/assets/{asset_name}/get",
            {"asset_name": asset_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.AssetGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_asset(
        cls,
        asset_name: str,
        data: Optional[Union[requests.AssetUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AssetUpdate:
        """
        Update an existing Asset with any new values passed through the body parameters. The minimum required in the body parameters is `title`. If this body parameter does not need to be changed, it should still have the original Display Name (`title``) given. Any other body parameters that are not required and not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.asset.update`.

        ``updateAsset``: ``POST`` ``/api/v4/assets/{asset_name}/update``

        Parameters
        ----------
        asset_name : :obj:`str`, optional
            Asset key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.AssetUpdate, optional
        **kwargs:
            Extra parameters for requests.AssetUpdate
              - update_asset: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/assets/{asset_name}/update",
            {"asset_name": asset_name},
            {},
            {},
            {},
            data,
            "requests.AssetUpdate",
            False,
            {
                "200": responses.AssetUpdate,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "403": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result
