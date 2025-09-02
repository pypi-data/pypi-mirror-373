"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class AssetInsights(ApiServiceModel):
    @classmethod
    def get_asset_insights(
        cls,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        data: Optional[Union[requests.AssetInsightsGet, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[KList[responses.AssetInsightsItem], responses.AssetInsightsGetPaginated]:
        """
        Advanced Asset Insights collates Asset data and optional custom defined fields and returns a structured array of Asset related objects. Ideal for generating UI lists, it accommodates a range of search, filter, and optional data on Data Streams, Parameters, Control Changes, Recommendations, etc. related to the Asset.

        **Permission Required:** `kelvin.permission.asset_insights.read`.

        ``getAssetInsights``: ``POST`` ``/api/v4/asset-insights/get``

        Parameters
        ----------
        page_size : :obj:`int`
            Number of Asset objects to be returned.
        page : :obj:`int`
            Return the list of Asset objects on requested page using the
            `page_size` as a page calculation reference.
        data: requests.AssetInsightsGet, optional
        **kwargs:
            Extra parameters for requests.AssetInsightsGet
              - get_asset_insights: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/asset-insights/get",
            {},
            {"page_size": page_size, "page": page},
            {},
            {},
            data,
            "requests.AssetInsightsGet",
            False,
            {
                "200": responses.AssetInsightsGetPaginated,
                "400": response.Error,
                "401": response.Error,
                "424": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
            kwargs,
        )
        return (
            cast(
                Union[KList[responses.AssetInsightsItem], responses.AssetInsightsGetPaginated],
                cls.fetch(_client, "/api/v4/asset-insights/get", result, "POST", data),
            )
            if fetch and not _dry_run
            else result
        )
