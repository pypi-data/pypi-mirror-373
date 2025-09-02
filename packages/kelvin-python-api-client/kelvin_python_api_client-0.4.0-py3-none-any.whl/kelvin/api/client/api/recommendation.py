"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses, type


class Recommendation(ApiServiceModel):
    @classmethod
    def get_recommendation_clustering(
        cls,
        data: Optional[Union[requests.RecommendationClusteringGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> KList[responses.RecommendationClustering]:
        """
        Retrieve the total count of Recommendations matching an array of `resources` and filter options between two dates grouped by the parameter `time_bucket`. Will also return a list of all the Recommendation `id`s counted.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``getRecommendationClustering``: ``POST`` ``/api/v4/recommendations/clustering/get``

        Parameters
        ----------
        data: requests.RecommendationClusteringGet, optional
        **kwargs:
            Extra parameters for requests.RecommendationClusteringGet
              - get_recommendation_clustering: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/clustering/get",
            {},
            {},
            {},
            {},
            data,
            "requests.RecommendationClusteringGet",
            False,
            {"200": List[responses.RecommendationClustering], "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def create_recommendation(
        cls,
        data: Optional[Union[requests.RecommendationCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RecommendationCreate:
        """
        Create a new Recommendation. The new recommendation will automatically inherit the state `pending`.

        **Permission Required:** `kelvin.permission.recommendation.create`.

        ``createRecommendation``: ``POST`` ``/api/v4/recommendations/create``

        Parameters
        ----------
        data: requests.RecommendationCreate, optional
        **kwargs:
            Extra parameters for requests.RecommendationCreate
              - create_recommendation: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/create",
            {},
            {},
            {},
            {},
            data,
            "requests.RecommendationCreate",
            False,
            {"201": responses.RecommendationCreate, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_recommendation_last(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.RecommendationLastGet, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.Recommendation], responses.RecommendationLastGetPaginatedResponseCursor]:
        """
        Returns a dictionary with a data property containing an array of latest Recommendations. Only the latest Recommendation for each `resource` in the request filters will be returned.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``getRecommendationLast``: ``POST`` ``/api/v4/recommendations/last/get``

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
        data: requests.RecommendationLastGet, optional
        **kwargs:
            Extra parameters for requests.RecommendationLastGet
              - get_recommendation_last: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/last/get",
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
            "requests.RecommendationLastGet",
            False,
            {
                "200": responses.RecommendationLastGetPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.Recommendation], responses.RecommendationLastGetPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/recommendations/last/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def list_recommendations(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.RecommendationsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.Recommendation], responses.RecommendationsListPaginatedResponseCursor]:
        """
        Returns a list of Recommendation objects. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``listRecommendations``: ``POST`` ``/api/v4/recommendations/list``

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
        data: requests.RecommendationsList, optional
        **kwargs:
            Extra parameters for requests.RecommendationsList
              - list_recommendations: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/list",
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
            "requests.RecommendationsList",
            False,
            {"200": responses.RecommendationsListPaginatedResponseCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.Recommendation], responses.RecommendationsListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/recommendations/list", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_recommendation_range(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.RecommendationRangeGet, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[type.Recommendation], responses.RecommendationRangeGetPaginatedResponseCursor]:
        """
        Returns a dictionary with a data property containing an array of Recommendations within a specified time range for all of the `resources` in the `resources` array that match the filter options.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``getRecommendationRange``: ``POST`` ``/api/v4/recommendations/range/get``

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
        data: requests.RecommendationRangeGet, optional
        **kwargs:
            Extra parameters for requests.RecommendationRangeGet
              - get_recommendation_range: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/range/get",
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
            "requests.RecommendationRangeGet",
            False,
            {
                "200": responses.RecommendationRangeGetPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[type.Recommendation], responses.RecommendationRangeGetPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/recommendations/range/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def create_recommendation_type(
        cls,
        data: Optional[Union[requests.RecommendationTypeCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RecommendationTypeCreate:
        """
        Create a new Recommendation Type.

        **Permission Required:** `kelvin.permission.recommendation.create`.

        ``createRecommendationType``: ``POST`` ``/api/v4/recommendations/types/create``

        Parameters
        ----------
        data: requests.RecommendationTypeCreate, optional
        **kwargs:
            Extra parameters for requests.RecommendationTypeCreate
              - create_recommendation_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/types/create",
            {},
            {},
            {},
            {},
            data,
            "requests.RecommendationTypeCreate",
            False,
            {
                "201": responses.RecommendationTypeCreate,
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
    def list_recommendation_types(
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
    ) -> Union[KList[type.RecommendationType], responses.RecommendationTypesListPaginatedCursor]:
        """
        Returns a list of Recommendation Type objects. The list can be optionally filtered and sorted on the server before being returned.
        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``listRecommendationTypes``: ``GET`` ``/api/v4/recommendations/types/list``

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

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/recommendations/types/list",
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
            {"200": responses.RecommendationTypesListPaginatedCursor, "400": response.Error, "401": response.Error},
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[type.RecommendationType], responses.RecommendationTypesListPaginatedCursor],
                cls.fetch(_client, "/api/v4/recommendations/types/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def delete_recommendation_type(cls, name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Recommendation Type. An error will be returned if there are any current Recommendations linked to the Recommendation Type. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.recommendation.delete`.

        ``deleteRecommendationType``: ``POST`` ``/api/v4/recommendations/types/{name}/delete``

        Parameters
        ----------
        name : :obj:`str`, optional
            Recommendation Type key `name` to delete. Case sensitive name.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/types/{name}/delete",
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
    def get_recommendation_type(
        cls, name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.RecommendationTypeGet:
        """
        Retrieves the parameters of a Recommendation Type.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``getRecommendationType``: ``GET`` ``/api/v4/recommendations/types/{name}/get``

        Parameters
        ----------
        name : :obj:`str`, optional
            Recommendation Type key `name` to get. Case sensitive name.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/recommendations/types/{name}/get",
            {"name": name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.RecommendationTypeGet,
                "400": response.Error,
                "401": response.Error,
                "404": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_recommendation_type(
        cls,
        name: str,
        data: Optional[Union[requests.RecommendationTypeUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.RecommendationTypeUpdate:
        """
        Updates an existing Recommendation Type with any new values passed through the body parameters. All body parameters are optional and if not provided will remain unchanged. Only the unique identifier `name` can not be changed.

        **Permission Required:** `kelvin.permission.recommendation.update`.

        ``updateRecommendationType``: ``POST`` ``/api/v4/recommendations/types/{name}/update``

        Parameters
        ----------
        name : :obj:`str`, optional
            Recommendation Type key `name` to update. Case sensitive name.
        data: requests.RecommendationTypeUpdate, optional
        **kwargs:
            Extra parameters for requests.RecommendationTypeUpdate
              - update_recommendation_type: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/types/{name}/update",
            {"name": name},
            {},
            {},
            {},
            data,
            "requests.RecommendationTypeUpdate",
            False,
            {
                "200": responses.RecommendationTypeUpdate,
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
    def update_recommendation_accept(
        cls,
        recommendation_id: str,
        data: Optional[Union[requests.RecommendationAcceptUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update a Recommendation `state` to `accepted`. This will trigger all objects in the `actions` parameter to be initiated. You will need to continue to monitor each action individually (for example a Control Change) to ensure it is completed successfully.

        **Permission Required:** `kelvin.permission.recommendation.update`.

        ``updateRecommendationAccept``: ``POST`` ``/api/v4/recommendations/{recommendation_id}/accept/update``

        Parameters
        ----------
        recommendation_id : :obj:`str`, optional
            Recommendation key `id` to accept. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.RecommendationAcceptUpdate, optional
        **kwargs:
            Extra parameters for requests.RecommendationAcceptUpdate
              - update_recommendation_accept: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/{recommendation_id}/accept/update",
            {"recommendation_id": recommendation_id},
            {},
            {},
            {},
            data,
            "requests.RecommendationAcceptUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_recommendation(cls, recommendation_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Recommendation. Recommendations with `states` tagged as `accepted`, `auto_accepted` or `error` can not be deleted. This action cannot be undone once the API request has been submitted.
        **Permission Required:** `kelvin.permission.recommendation.delete`.

        ``deleteRecommendation``: ``POST`` ``/api/v4/recommendations/{recommendation_id}/delete``

        Parameters
        ----------
        recommendation_id : :obj:`str`, optional
            Recommendation key `id` to delete. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/{recommendation_id}/delete",
            {"recommendation_id": recommendation_id},
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
    def get_recommendation(
        cls, recommendation_id: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.RecommendationGet:
        """
        Retrieves the properties, status and all associated actions of a Recommendation.

        **Permission Required:** `kelvin.permission.recommendation.read`.

        ``getRecommendation``: ``GET`` ``/api/v4/recommendations/{recommendation_id}/get``

        Parameters
        ----------
        recommendation_id : :obj:`str`, optional
            Recommendation key `id` of the Recommendation to get. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/recommendations/{recommendation_id}/get",
            {"recommendation_id": recommendation_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.RecommendationGet, "404": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_recommendation_reject(
        cls,
        recommendation_id: str,
        data: Optional[Union[requests.RecommendationRejectUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update a Recommendation `state` to `rejected`. All `actions` will only be archived and not implemented.

        **Permission Required:** `kelvin.permission.recommendation.update`.

        ``updateRecommendationReject``: ``POST`` ``/api/v4/recommendations/{recommendation_id}/reject/update``

        Parameters
        ----------
        recommendation_id : :obj:`str`, optional
            Recommendation key `id` to reject. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.RecommendationRejectUpdate, optional
        **kwargs:
            Extra parameters for requests.RecommendationRejectUpdate
              - update_recommendation_reject: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/recommendations/{recommendation_id}/reject/update",
            {"recommendation_id": recommendation_id},
            {},
            {},
            {},
            data,
            "requests.RecommendationRejectUpdate",
            False,
            {"204": None, "400": response.Error, "401": response.Error, "404": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
