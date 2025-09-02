"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Properties(ApiServiceModel):
    @classmethod
    def create_property(
        cls,
        data: Optional[Union[requests.PropertyCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.PropertyCreate:
        """
        Create a new Property Definition

        **Permission Required:** `kelvin.permission.property.create`.

        ``createProperty``: ``POST`` ``/api/v4/properties/create``

        Parameters
        ----------
        data: requests.PropertyCreate, optional
        **kwargs:
            Extra parameters for requests.PropertyCreate
              - create_property: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/create",
            {},
            {},
            {},
            {},
            data,
            "requests.PropertyCreate",
            False,
            {"201": responses.PropertyCreate, "400": response.Error, "401": response.Error, "409": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_properties(
        cls,
        search: Optional[Sequence[str]] = None,
        primitive_type: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[type.PropertyDefinition], responses.PropertiesListPaginatedResponseCursor]:
        """
        Returns a list of Property Definitions. The Properties can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.property.read`.

        ``listProperties``: ``GET`` ``/api/v4/properties/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the keys `title` (Display Name)
            or `name`. All values in array will be filtered as `OR`. The search is
            case insensitive and will find partial matches as well.
        primitive_type : :obj:`Sequence[str]`
            A filter on the list based on the key `primitive_type`. The filter is
            on the full name only. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
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
            "/api/v4/properties/list",
            {},
            {
                "search": search,
                "primitive_type": primitive_type,
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
            {"200": responses.PropertiesListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.PropertyDefinition], responses.PropertiesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/properties/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_property_unique_values(
        cls,
        data: Optional[Union[requests.PropertyUniqueValuesGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.PropertyUniqueValuesGet:
        """
        Fetch the unique values for each property.

        **Permission Required:** `kelvin.permission.property.read`.

        ``getPropertyUniqueValues``: ``POST`` ``/api/v4/properties/unique/values/get``

        Parameters
        ----------
        data: requests.PropertyUniqueValuesGet, optional
        **kwargs:
            Extra parameters for requests.PropertyUniqueValuesGet
              - get_property_unique_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/unique/values/get",
            {},
            {},
            {},
            {},
            data,
            "requests.PropertyUniqueValuesGet",
            False,
            {
                "200": responses.PropertyUniqueValuesGet,
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
    def delete_property(cls, property_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Property. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.property.delete`.

        ``deleteProperty``: ``POST`` ``/api/v4/properties/{property_name}/delete``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property `name`, also known as `property_name`, to delete. The string
            can only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/{property_name}/delete",
            {"property_name": property_name},
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
    def get_property(cls, property_name: str, _dry_run: bool = False, _client: Any = None) -> responses.PropertyGet:
        """
        Retrieve a Property Definition.

        **Permission Required:** `kelvin.permission.property.read`.

        ``getProperty``: ``GET`` ``/api/v4/properties/{property_name}/get``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property Definition `name` to fetch. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/properties/{property_name}/get",
            {"property_name": property_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.PropertyGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def delete_property_values(
        cls,
        property_name: str,
        data: Optional[Union[requests.PropertyValuesDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Permanently delete existing property Values. This cannot be undone once the API request has been submitted.
        **Permission Required:** `kelvin.permission.property.delete`.

        ``deletePropertyValues``: ``POST`` ``/api/v4/properties/{property_name}/values/delete``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property `name` for which the values are to be deleted. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        data: requests.PropertyValuesDelete, optional
        **kwargs:
            Extra parameters for requests.PropertyValuesDelete
              - delete_property_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/{property_name}/values/delete",
            {"property_name": property_name},
            {},
            {},
            {},
            data,
            "requests.PropertyValuesDelete",
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_property_values(
        cls,
        property_name: str,
        resource_type: Optional[Sequence[str]] = None,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> responses.PropertyValuesGet:
        """
        Fetch property values belonging to a particular property definition.

        **Permission Required:** `kelvin.permission.property.read`.

        ``getPropertyValues``: ``GET`` ``/api/v4/properties/{property_name}/values/get``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property `name` for which the values are to be fetched. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        resource_type : :obj:`Sequence[str]`
            Array of resource types to filter the list of Property values
            returned.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/properties/{property_name}/values/get",
            {"property_name": property_name},
            {"resource_type": resource_type},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.PropertyValuesGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def property_range_get(
        cls,
        property_name: str,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.RangeGetPropertyValues, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.PropertyValueHistory], responses.RangeGetPropertyPaginatedResponseCursor]:
        """
        Fetch the value history for a property given a time range.

        **Permission Required:** `kelvin.permission.property.read`.

        ``propertyRangeGet``: ``POST`` ``/api/v4/properties/{property_name}/values/range/get``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property `name` for which the values are to be updated. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
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
        data: requests.RangeGetPropertyValues, optional
        **kwargs:
            Extra parameters for requests.RangeGetPropertyValues
              - property_range_get: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/{property_name}/values/range/get",
            {"property_name": property_name},
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
            "requests.RangeGetPropertyValues",
            False,
            {
                "200": responses.RangeGetPropertyPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.PropertyValueHistory], responses.RangeGetPropertyPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/properties/{property_name}/values/range/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def update_property_values(
        cls,
        property_name: str,
        data: Optional[Union[requests.PropertyValuesUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create or update Property Values.

        **Permission Required:** `kelvin.permission.property.create`.

        ``updatePropertyValues``: ``POST`` ``/api/v4/properties/{property_name}/values/update``

        Parameters
        ----------
        property_name : :obj:`str`, optional
            Property `name` for which the values are to be updated. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        data: requests.PropertyValuesUpdate, optional
        **kwargs:
            Extra parameters for requests.PropertyValuesUpdate
              - update_property_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/properties/{property_name}/values/update",
            {"property_name": property_name},
            {},
            {},
            {},
            data,
            "requests.PropertyValuesUpdate",
            False,
            {"201": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
