"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class DataQuality(ApiServiceModel):
    @classmethod
    def create_bulk_data_quality(
        cls,
        data: Optional[Union[requests.BulkDataQualityCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Create multiple data qualities at once.

        **Permission Required:** `kelvin.permission.data-quality.create`.

        ``createBulkDataQuality``: ``POST`` ``/api/v4/data-quality/bulk/create``

        Parameters
        ----------
        data: requests.BulkDataQualityCreate, optional
        **kwargs:
            Extra parameters for requests.BulkDataQualityCreate
              - create_bulk_data_quality: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/bulk/create",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataQualityCreate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "409": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_bulk_data_quality(
        cls,
        data: Optional[Union[requests.BulkDataQualityDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Deletes multiple data qualities.

        **Permission Required:** `kelvin.permission.data-quality.delete`.

        ``deleteBulkDataQuality``: ``POST`` ``/api/v4/data-quality/bulk/delete``

        Parameters
        ----------
        data: requests.BulkDataQualityDelete, optional
        **kwargs:
            Extra parameters for requests.BulkDataQualityDelete
              - delete_bulk_data_quality: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/bulk/delete",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataQualityDelete",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def update_bulk_data_quality(
        cls,
        data: Optional[Union[requests.BulkDataQualityUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update multiple data qualities at once.

        **Permission Required:** `kelvin.permission.data-quality.update`.

        ``updateBulkDataQuality``: ``POST`` ``/api/v4/data-quality/bulk/update``

        Parameters
        ----------
        data: requests.BulkDataQualityUpdate, optional
        **kwargs:
            Extra parameters for requests.BulkDataQualityUpdate
              - update_bulk_data_quality: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/bulk/update",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkDataQualityUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "409": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_data_quality(
        cls,
        data: Optional[Union[requests.DataQualityCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataQualityCreate:
        """
        Create a new Data Quality Configuration.

        A data Quality is a configuration that defines all the algorithms being used to monitor a resource data quality.

        All configurations are optional. There are no validations done regarding each configuration content.

        **Permission Required:** `kelvin.permission.data-quality.create`.

        ``createDataQuality``: ``POST`` ``/api/v4/data-quality/create``

        Parameters
        ----------
        data: requests.DataQualityCreate, optional
        **kwargs:
            Extra parameters for requests.DataQualityCreate
              - create_data_quality: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataQualityCreate",
            False,
            {
                "201": responses.DataQualityCreate,
                "400": response.Error,
                "401": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_quality(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.DataQualityList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.DataQuality], responses.DataQualityListPaginatedResponseCursor]:
        """
        List data qualities based on the provided filters.

        **Permission Required:** `kelvin.permission.data-quality.read`.

        ``listDataQuality``: ``POST`` ``/api/v4/data-quality/list``

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
        data: requests.DataQualityList, optional
        **kwargs:
            Extra parameters for requests.DataQualityList
              - list_data_quality: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/list",
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
            "requests.DataQualityList",
            False,
            {
                "200": responses.DataQualityListPaginatedResponseCursor,
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
                Union[KList[type.DataQuality], responses.DataQualityListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/data-quality/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def data_quality_simulate(
        cls,
        data: Optional[Union[requests.DataQualitySimulate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataQualitySimulate:
        """
        Simulate the effect of data quality updates without making permanent changes.

        **Permission Required:** `kelvin.permission.data-quality.read`.

        ``DataQualitySimulate``: ``POST`` ``/api/v4/data-quality/simulate``

        Parameters
        ----------
        data: requests.DataQualitySimulate, optional
        **kwargs:
            Extra parameters for requests.DataQualitySimulate
              - data_quality_simulate: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/simulate",
            {},
            {},
            {},
            {},
            data,
            "requests.DataQualitySimulate",
            False,
            {"200": responses.DataQualitySimulate, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_data_quality(cls, resource: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a Data Quality by resource.

        **Permission Required:** `kelvin.permission.data-quality.delete`.

        ``deleteDataQuality``: ``POST`` ``/api/v4/data-quality/{resource}/delete``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset or Asset/Data Stream pair for deleting the associated
            DataQuality configurations. (example: `krn:ad:asset1/setpoint`).

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/{resource}/delete",
            {"resource": resource},
            {},
            {},
            {},
            None,
            None,
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_data_quality(cls, resource: str, _dry_run: bool = False, _client: Any = None) -> responses.DataQualityGet:
        """
        Get a Data Quality by resource.

        **Permission Required:** `kelvin.permission.data-quality.read`.

        ``getDataQuality``: ``GET`` ``/api/v4/data-quality/{resource}/get``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset/Data Stream pair to retrieve the associated DataQuality
            configurations. (example: `krn:ad:asset1/setpoint`).

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/data-quality/{resource}/get",
            {"resource": resource},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.DataQualityGet,
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
    def update_data_quality(
        cls,
        resource: str,
        data: Optional[Union[requests.DataQualityUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataQualityUpdate:
        """
        Update a Data Quality by providing the new configuration.
        This request changes the whole Data Quality Configuration.

        **Permission Required:** `kelvin.permission.data-quality.update`.

        ``updateDataQuality``: ``POST`` ``/api/v4/data-quality/{resource}/update``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset or Asset/Data Stream pair to update the associated Data Quality
            configurations. (example: `krn:ad:asset1/setpoint`).
        data: requests.DataQualityUpdate, optional
        **kwargs:
            Extra parameters for requests.DataQualityUpdate
              - update_data_quality: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/data-quality/{resource}/update",
            {"resource": resource},
            {},
            {},
            {},
            data,
            "requests.DataQualityUpdate",
            False,
            {
                "200": responses.DataQualityUpdate,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result
