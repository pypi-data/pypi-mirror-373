"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class DeprecatedParameters(ApiServiceModel):
    @classmethod
    def update_parameters_app_version(
        cls,
        app_name: str,
        version: str,
        data: Optional[Union[requests.ParametersAppVersionUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Bulk update Parameters for multiple resources of a given App Version.
        Parameters belonging to the App Version but not specified in the payload
        will **not** be changed. Setting a value to `null` will cause the parameter
        to be unset.  Additionally, it's also possible to set a comment for each
        parameter change.

        The source of the change will, by default, be the user making the API
        request. If the user making the request is a Service Account, it can,
        optionally, set its own source KRN.

        ``updateParametersAppVersion``: ``POST`` ``/api/v4/parameters/app/{app_name}/versions/{version}/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            Application key `name` to associate with Assets (resources) to perform
            the required actions.
        version : :obj:`str`, optional
            Version of Application.
        data: requests.ParametersAppVersionUpdate, optional
        **kwargs:
            Extra parameters for requests.ParametersAppVersionUpdate
              - update_parameters_app_version: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/app/{app_name}/versions/{version}/update",
            {"app_name": app_name, "version": version},
            {},
            {},
            {},
            data,
            "requests.ParametersAppVersionUpdate",
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_parameters_definitions(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ParametersDefinitionsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ParameterDefinitionItem], responses.ParametersDefinitionsListPaginatedResponseCursor]:
        """
        Returns a list of Parameters and its definition in each App. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listParametersDefinitions``: ``POST`` ``/api/v4/parameters/definitions/list``

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
            Sort the results by one or more enumerators.
        data: requests.ParametersDefinitionsList, optional
        **kwargs:
            Extra parameters for requests.ParametersDefinitionsList
              - list_parameters_definitions: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/definitions/list",
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
            "requests.ParametersDefinitionsList",
            False,
            {
                "200": responses.ParametersDefinitionsListPaginatedResponseCursor,
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
                Union[
                    KList[responses.ParameterDefinitionItem], responses.ParametersDefinitionsListPaginatedResponseCursor
                ],
                cls.fetch(_client, "/api/v4/parameters/definitions/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_resource_parameters(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ResourceParametersList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ParameterValueHistorianItem], responses.ResourceParametersListPaginatedResponseCursor]:
        """
        Returns a list of Parameters and all values for each Resource. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listResourceParameters``: ``POST`` ``/api/v4/parameters/resources/list``

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
            Sort the results by one or more enumerators.
        data: requests.ResourceParametersList, optional
        **kwargs:
            Extra parameters for requests.ResourceParametersList
              - list_resource_parameters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/resources/list",
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
            "requests.ResourceParametersList",
            False,
            {
                "200": responses.ResourceParametersListPaginatedResponseCursor,
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
                Union[
                    KList[responses.ParameterValueHistorianItem],
                    responses.ResourceParametersListPaginatedResponseCursor,
                ],
                cls.fetch(_client, "/api/v4/parameters/resources/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_parameters_values(
        cls,
        data: Optional[Union[requests.ParametersValuesGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ParametersValuesGet:
        """
        Returns a list of all unique values for each Parameter. Default values will not be shown. If the App is not specified, then the response will be grouped by App Name.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getParametersValues``: ``POST`` ``/api/v4/parameters/values/get``

        Parameters
        ----------
        data: requests.ParametersValuesGet, optional
        **kwargs:
            Extra parameters for requests.ParametersValuesGet
              - get_parameters_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/values/get",
            {},
            {},
            {},
            {},
            data,
            "requests.ParametersValuesGet",
            False,
            {"200": responses.ParametersValuesGet, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
