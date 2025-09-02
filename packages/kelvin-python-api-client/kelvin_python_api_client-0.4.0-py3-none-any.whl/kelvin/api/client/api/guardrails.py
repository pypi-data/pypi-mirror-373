"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Guardrails(ApiServiceModel):
    @classmethod
    def create_bulk_guardrails(
        cls,
        data: Optional[Union[requests.BulkGuardrailsCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.BulkGuardrailsCreate:
        """
        Create multiple guardrails at once.

        **Permission Required:** `kelvin.permission.guardrails.create`.

        ``createBulkGuardrails``: ``POST`` ``/api/v4/guardrails/bulk/create``

        Parameters
        ----------
        data: requests.BulkGuardrailsCreate, optional
        **kwargs:
            Extra parameters for requests.BulkGuardrailsCreate
              - create_bulk_guardrails: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/bulk/create",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkGuardrailsCreate",
            False,
            {
                "201": responses.BulkGuardrailsCreate,
                "207": None,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
                "409": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_bulk_guardrails(
        cls,
        data: Optional[Union[requests.BulkGuardrailsDelete, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Deletes multiple guardrails.

        **Permission Required:** `kelvin.permission.guardrails.delete`.

        ``deleteBulkGuardrails``: ``POST`` ``/api/v4/guardrails/bulk/delete``

        Parameters
        ----------
        data: requests.BulkGuardrailsDelete, optional
        **kwargs:
            Extra parameters for requests.BulkGuardrailsDelete
              - delete_bulk_guardrails: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/bulk/delete",
            {},
            {},
            {},
            {},
            data,
            "requests.BulkGuardrailsDelete",
            False,
            {
                "200": None,
                "207": None,
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

    @classmethod
    def create_guardrail(
        cls,
        data: Optional[Union[requests.GuardrailCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.GuardrailCreate:
        """
        Create a new Guardrail.

        A Guardrail is a configuration that defines a range of values, absolute or
        relative, that a control change must stay within. If the control change is
        outside of the defined range, it will be blocked and marked as rejected.

        All configurations are optional. There are no validations done regarding a
        `min` being higher than a `max` or vice versa.

        Additionally, a Guardrail value may be set by a data stream.

        **Permission Required:** `kelvin.permission.guardrails.create`.

        ``createGuardrail``: ``POST`` ``/api/v4/guardrails/create``

        Parameters
        ----------
        data: requests.GuardrailCreate, optional
        **kwargs:
            Extra parameters for requests.GuardrailCreate
              - create_guardrail: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/create",
            {},
            {},
            {},
            {},
            data,
            "requests.GuardrailCreate",
            False,
            {
                "201": responses.GuardrailCreate,
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
    def list_guardrails(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        search: Optional[Sequence[str]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.GuardrailsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.Guardrail], responses.GuardrailsListPaginatedResponseCursor]:
        """
        List guardrails based on the provided filters.

        **Permission Required:** `kelvin.permission.guardrails.read`.

        ``listGuardrails``: ``POST`` ``/api/v4/guardrails/list``

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
        search : :obj:`Sequence[str]`
            Search for guardrails with `resources` matching the search term.
        sort_by : :obj:`Sequence[str]`
        data: requests.GuardrailsList, optional
        **kwargs:
            Extra parameters for requests.GuardrailsList
              - list_guardrails: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/list",
            {},
            {
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "search": search,
                "sort_by": sort_by,
            },
            {},
            {},
            data,
            "requests.GuardrailsList",
            False,
            {
                "200": responses.GuardrailsListPaginatedResponseCursor,
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
                Union[KList[type.Guardrail], responses.GuardrailsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/guardrails/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_guardrail(cls, resource: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete a Guardrail by ID.

        **Permission Required:** `kelvin.permission.guardrails.delete`.

        ``deleteGuardrail``: ``POST`` ``/api/v4/guardrails/{resource}/delete``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset/Data Stream pair for deleting the associated Guardrail
            configurations. (example: `krn:ad:asset1/setpoint`).

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/{resource}/delete",
            {"resource": resource},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "401": response.Error, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_guardrail(cls, resource: str, _dry_run: bool = False, _client: Any = None) -> responses.GuardrailGet:
        """
        Get a Guardrail by ID.

        **Permission Required:** `kelvin.permission.guardrails.read`.

        ``getGuardrail``: ``GET`` ``/api/v4/guardrails/{resource}/get``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset/Data Stream pair to retrieve the associated Guardrail
            configurations. (example: `krn:ad:asset1/setpoint`).

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/guardrails/{resource}/get",
            {"resource": resource},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.GuardrailGet,
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
    def update_guardrail(
        cls,
        resource: str,
        data: Optional[Union[requests.GuardrailUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.GuardrailUpdate:
        """
        Update a Guardrail by providing the Guardrail ID and the fields to update.
        This request changes the whole Guardrail.

        **Permission Required:** `kelvin.permission.guardrails.update`.

        ``updateGuardrail``: ``POST`` ``/api/v4/guardrails/{resource}/update``

        Parameters
        ----------
        resource : :obj:`str`, optional
            Asset/Data Stream pair to update the associated Guardrail
            configurations. (example: `krn:ad:asset1/setpoint`).
        data: requests.GuardrailUpdate, optional
        **kwargs:
            Extra parameters for requests.GuardrailUpdate
              - update_guardrail: str

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/guardrails/{resource}/update",
            {"resource": resource},
            {},
            {},
            {},
            data,
            "requests.GuardrailUpdate",
            False,
            {
                "200": responses.GuardrailUpdate,
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
