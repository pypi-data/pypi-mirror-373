"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class AppParameters(ApiServiceModel):
    @classmethod
    def list_app_version_parameters_history(
        cls,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        data: Optional[Union[requests.AppVersionParametersHistoryList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.AppVersionParameter], responses.AppVersionParametersHistoryListPaginatedResponseCursor]:
        """
        List App Version Parameters History

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listAppVersionParametersHistory``: ``POST`` ``/api/v4/apps/parameters/history/list``

        Parameters
        ----------
        sort_by : :obj:`Sequence[str]`
            Sort the results by one or more enumerators.
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
        data: requests.AppVersionParametersHistoryList, optional
        **kwargs:
            Extra parameters for requests.AppVersionParametersHistoryList
              - list_app_version_parameters_history: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/history/list",
            {},
            {
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
            data,
            "requests.AppVersionParametersHistoryList",
            False,
            {
                "200": responses.AppVersionParametersHistoryListPaginatedResponseCursor,
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
                    KList[type.AppVersionParameter], responses.AppVersionParametersHistoryListPaginatedResponseCursor
                ],
                cls.fetch(_client, "/api/v4/apps/parameters/history/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_app_parameters(
        cls,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        data: Optional[Union[requests.AppParametersList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.AppParameter], responses.AppParametersListPaginatedResponseCursor]:
        """
        List App Parameters

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listAppParameters``: ``POST`` ``/api/v4/apps/parameters/list``

        Parameters
        ----------
        sort_by : :obj:`Sequence[str]`
            Sort the results by one or more enumerators.
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
        data: requests.AppParametersList, optional
        **kwargs:
            Extra parameters for requests.AppParametersList
              - list_app_parameters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/list",
            {},
            {
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
            data,
            "requests.AppParametersList",
            False,
            {
                "200": responses.AppParametersListPaginatedResponseCursor,
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
                Union[KList[type.AppParameter], responses.AppParametersListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/parameters/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_parameters_schedule(
        cls,
        data: Optional[Union[requests.ParametersScheduleCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ParametersScheduleCreate:
        """
        Create a new schedule to apply parameters to an application.

        Schedules are sets of application parameter values that are applied to a
        group of assets at a given time.

        Optionally, those values can be reverted to the desired value. When doing
        so, parameter values are defined for each asset individually, and the
        assets and parameters must match the original schedule. For example, if 2
        parameters were changed for 2 assets and a revert operation is requested,
        then the revert parameters must have 2 assets and 2 parameters for each
        asset.

        The schedule must be created in the future and, if a revert operation is
        requested, the revert date must be after the scheduled date.

        Upon creation, the current values of the parameters are stored in the
        `original_resource_parameters` field.


        **Permission Required:** `kelvin.permission.parameter.update`.

        ``createParametersSchedule``: ``POST`` ``/api/v4/apps/parameters/schedules/create``

        Parameters
        ----------
        data: requests.ParametersScheduleCreate, optional
        **kwargs:
            Extra parameters for requests.ParametersScheduleCreate
              - create_parameters_schedule: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/schedules/create",
            {},
            {},
            {},
            {},
            data,
            "requests.ParametersScheduleCreate",
            False,
            {
                "201": responses.ParametersScheduleCreate,
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
    def list_parameters_schedule(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ParametersScheduleList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.ParametersScheduleGet], responses.ParametersScheduleListPaginatedResponseCursor]:
        """
        Returns a list of Parameter Schedules and its parameters. The Parameter Schedules can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listParametersSchedule``: ``POST`` ``/api/v4/apps/parameters/schedules/list``

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
        data: requests.ParametersScheduleList, optional
        **kwargs:
            Extra parameters for requests.ParametersScheduleList
              - list_parameters_schedule: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/schedules/list",
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
            "requests.ParametersScheduleList",
            False,
            {
                "200": responses.ParametersScheduleListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.ParametersScheduleGet], responses.ParametersScheduleListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/parameters/schedules/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def apply_parameters_schedule(
        cls,
        schedule_id: str,
        data: Optional[Union[requests.ParametersScheduleApply, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Apply the scheduled or reverted parameters of a specific schedule.

        There are 2 types of the "apply" action:

        - `schedule`: Applies the scheduled parameters if the schedule is in the
        `scheduled` state.
        - `schedule-revert`: Applies the revert parameters if the schedule is in the
        `scheduled-revert` state.

        If the schedule is not in the supported state for the selected type, the
        API will return an error.

        Errors encountered when calling this API will not affect the schedule
        state.

        **Permission Required:** `kelvin.permission.parameter.update`.

        ``applyParametersSchedule``: ``POST`` ``/api/v4/apps/parameters/schedules/{schedule_id}/apply``

        Parameters
        ----------
        schedule_id : :obj:`str`, optional
            The parameter schedule key `id` to be applied immediately.
        data: requests.ParametersScheduleApply, optional
        **kwargs:
            Extra parameters for requests.ParametersScheduleApply
              - apply_parameters_schedule: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/schedules/{schedule_id}/apply",
            {"schedule_id": schedule_id},
            {},
            {},
            {},
            data,
            "requests.ParametersScheduleApply",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_parameters_schedule(cls, schedule_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a specific schedule.

        **Permission Required:** `kelvin.permission.parameter.update`.

        ``deleteParametersSchedule``: ``POST`` ``/api/v4/apps/parameters/schedules/{schedule_id}/delete``

        Parameters
        ----------
        schedule_id : :obj:`str`, optional
            The parameter schedule key `id` to be delete.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/schedules/{schedule_id}/delete",
            {"schedule_id": schedule_id},
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
    def get_parameters_schedule(
        cls, schedule_id: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.ParametersScheduleGet:
        """
        Get a specific schedule.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getParametersSchedule``: ``GET`` ``/api/v4/apps/parameters/schedules/{schedule_id}/get``

        Parameters
        ----------
        schedule_id : :obj:`str`, optional
            The parameter schedule key `id` to be retrieved.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/apps/parameters/schedules/{schedule_id}/get",
            {"schedule_id": schedule_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.ParametersScheduleGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_app_version_parameters_unique_values(
        cls,
        data: Optional[Union[requests.AppVersionParametersUniqueValuesGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionParametersUniqueValuesGet:
        """
        Get App Version Parameters Unique Values

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getAppVersionParametersUniqueValues``: ``POST`` ``/api/v4/apps/parameters/unique-values/get``

        Parameters
        ----------
        data: requests.AppVersionParametersUniqueValuesGet, optional
        **kwargs:
            Extra parameters for requests.AppVersionParametersUniqueValuesGet
              - get_app_version_parameters_unique_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/unique-values/get",
            {},
            {},
            {},
            {},
            data,
            "requests.AppVersionParametersUniqueValuesGet",
            False,
            {
                "200": responses.AppVersionParametersUniqueValuesGet,
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
    def list_app_version_parameter_values(
        cls,
        sort_by: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        data: Optional[Union[requests.AppVersionParameterValuesList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.AppVersionParameter], responses.AppVersionParameterValuesListPaginatedResponseCursor]:
        """
        List App Version Parameter Values

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listAppVersionParameterValues``: ``POST`` ``/api/v4/apps/parameters/values/list``

        Parameters
        ----------
        sort_by : :obj:`Sequence[str]`
            Sort the results by one or more enumerators.
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
        data: requests.AppVersionParameterValuesList, optional
        **kwargs:
            Extra parameters for requests.AppVersionParameterValuesList
              - list_app_version_parameter_values: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/parameters/values/list",
            {},
            {
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
            data,
            "requests.AppVersionParameterValuesList",
            False,
            {
                "200": responses.AppVersionParameterValuesListPaginatedResponseCursor,
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
                Union[KList[type.AppVersionParameter], responses.AppVersionParameterValuesListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/apps/parameters/values/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def update_app_version_parameters_defaults(
        cls,
        app_name: str,
        app_version: str,
        patch: Optional[bool] = None,
        data: Optional[Union[requests.AppVersionParametersDefaultsUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update App Version Parameters Defaults

        **Permission Required:** `kelvin.permission.app.update`.

        ``updateAppVersionParametersDefaults``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/parameters/defaults/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        patch : :obj:`bool`
            If set to `true`, it only updates the parameters that are explicitly
            defined in the request.
        data: requests.AppVersionParametersDefaultsUpdate, optional
        **kwargs:
            Extra parameters for requests.AppVersionParametersDefaultsUpdate
              - update_app_version_parameters_defaults: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/parameters/defaults/update",
            {"app_name": app_name, "app_version": app_version},
            {"patch": patch},
            {},
            {},
            data,
            "requests.AppVersionParametersDefaultsUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_app_version_parameters_fallback_values(
        cls,
        app_name: str,
        app_version: str,
        data: Optional[Union[requests.AppVersionParametersFallbackValuesGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.AppVersionParametersFallbackValuesGet:
        """
        Get App Version Parameters Fallback Values

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getAppVersionParametersFallbackValues``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/parameters/fallback-values/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        data: requests.AppVersionParametersFallbackValuesGet, optional
        **kwargs:
            Extra parameters for requests.AppVersionParametersFallbackValuesGet
              - get_app_version_parameters_fallback_values: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/parameters/fallback-values/get",
            {"app_name": app_name, "app_version": app_version},
            {},
            {},
            {},
            data,
            "requests.AppVersionParametersFallbackValuesGet",
            False,
            {
                "200": responses.AppVersionParametersFallbackValuesGet,
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
    def update_app_version_parameters(
        cls,
        app_name: str,
        app_version: str,
        patch: Optional[bool] = None,
        data: Optional[Union[requests.AppVersionParametersUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update App Version Parameters

        **Permission Required:** `kelvin.permission.parameter.update`.

        ``updateAppVersionParameters``: ``POST`` ``/api/v4/apps/{app_name}/v/{app_version}/parameters/values/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
        app_version : :obj:`str`, optional
        patch : :obj:`bool`
            If set to `true`, it only updates the parameters that are explicitly
            defined in the request.
        data: requests.AppVersionParametersUpdate, optional
        **kwargs:
            Extra parameters for requests.AppVersionParametersUpdate
              - update_app_version_parameters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/apps/{app_name}/v/{app_version}/parameters/values/update",
            {"app_name": app_name, "app_version": app_version},
            {"patch": patch},
            {},
            {},
            data,
            "requests.AppVersionParametersUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
