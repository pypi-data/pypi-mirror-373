"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping, Optional, Sequence, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel
from kelvin.api.client.data_model import KList

from ..model import requests, response, responses


class Orchestration(ApiServiceModel):
    @classmethod
    def create_orchestration_clusters(
        cls,
        data: Optional[Union[requests.OrchestrationClustersCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.OrchestrationClustersCreate:
        """
        Create a new Cluster. This only creates the Cloud registration, the actual installation still needs to be manually performed on the server/kubernetes cluster. The provision script to run locally on the server for `type` registered as `k3s` or on an existing kubernetes cluster for `type` registered as `kubernetes` will be in the key `provision_script ` in the 201 response body.

        **Permission Required:** `kelvin.permission.cluster.create`.

        ``createOrchestrationClusters``: ``POST`` ``/api/v4/orchestration/clusters/create``

        Parameters
        ----------
        data: requests.OrchestrationClustersCreate, optional
        **kwargs:
            Extra parameters for requests.OrchestrationClustersCreate
              - create_orchestration_clusters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/orchestration/clusters/create",
            {},
            {},
            {},
            {},
            data,
            "requests.OrchestrationClustersCreate",
            False,
            {
                "201": responses.OrchestrationClustersCreate,
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
    def list_orchestration_clusters(
        cls,
        names: Optional[Sequence[str]] = None,
        search: Optional[Sequence[str]] = None,
        type: Optional[Sequence[str]] = None,
        ready: Optional[bool] = None,
        status: Optional[Sequence[str]] = None,
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
    ) -> Union[
        KList[responses.OrchestrationClustersCreateItem], responses.OrchestrationClustersListPaginatedResponseCursor
    ]:
        """
        Returns a list of Cluster objects. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``listOrchestrationClusters``: ``GET`` ``/api/v4/orchestration/clusters/list``

        Parameters
        ----------
        names : :obj:`Sequence[str]`
            A filter on the list based on the Cluster key `name`. The filter is on
            the full name only. All strings in the array are treated as `OR`. Can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the Cluster keys `title`
            (Display Name) or `name`. The search is case insensitive and will find
            partial matches as well.
        type : :obj:`Sequence[str]`
            A filter on the list based on the Cluster key `type`. The filter is on
            the full name only. All strings in the array are treated as `OR`.
            Options are `k3s` and `kubernetes`
        ready : :obj:`bool`
            A filter on the list based on the Cluster key `ready`. Options are
            `true` and `false`
        status : :obj:`Sequence[str]`
            A filter on the list based on the Cluster key `status`. The filter is
            on the full name only. All strings in the array are treated as `OR`.
            Options are `pending_provision`, `pending`, `online`, `unreachable`
            and `requires_attention`
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
            Sort the results by one of the Cluster parameters. Only one parameter
            can be selected. Options: `name`, `title`, `ready`, `type`, `status`,
            `last_seen`, `created`, `updated`, `kelvin_version`,
            `container_version`.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/list",
            {},
            {
                "names": names,
                "search": search,
                "type": type,
                "ready": ready,
                "status": status,
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
                "200": responses.OrchestrationClustersListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[
                    KList[responses.OrchestrationClustersCreateItem],
                    responses.OrchestrationClustersListPaginatedResponseCursor,
                ],
                cls.fetch(_client, "/api/v4/orchestration/clusters/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def download_orchestration_cluster_provision_binary(
        cls,
        arch: Optional[Literal["amd64", "arm64", "armv7"]] = None,
        type: Optional[Literal["kubernetes", "docker"]] = None,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Iterator[bytes]:
        """
        Download Cluster Provision Binary

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``downloadOrchestrationClusterProvisionBinary``: ``GET`` ``/api/v4/orchestration/clusters/provision/bin/download``

        Parameters
        ----------
        arch : :obj:`Literal['amd64', 'arm64', 'armv7']`
            Architecture of the binary to download. Options are `amd64`, `arm64`,
            `armv7` (default: `amd64`) ('amd64', 'arm64', 'armv7')
        type : :obj:`Literal['kubernetes', 'docker']`
            Type of the binary to download. Options are `kubernetes`, `docker`
            (default: `kubernetes`) ('kubernetes', 'docker')

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/provision/bin/download",
            {},
            {"arch": arch, "type": type},
            {},
            {},
            None,
            None,
            False,
            {"200": bytes, "400": response.Error, "401": response.Error, "500": response.Error},
            True,
            _dry_run,
        )
        return result

    @classmethod
    def delete_orchestration_clusters(cls, cluster_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Cluster and its Nodes. This will also delete Workloads, Bridges and Services residing on the Cluster. This cannot be undone once the API request has been submitted.

        **Permission Required:** `kelvin.permission.cluster.delete`.

        ``deleteOrchestrationClusters``: ``POST`` ``/api/v4/orchestration/clusters/{cluster_name}/delete``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to delete. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/orchestration/clusters/{cluster_name}/delete",
            {"cluster_name": cluster_name},
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
    def apply_orchestration_clusters_edge_apps_version(
        cls, cluster_name: str, _dry_run: bool = False, _client: Any = None
    ) -> None:
        """
        Initiates available cluster upgrades; requires cluster to be online and ready.

        **Permission Required:** `kelvin.permission.cluster.update`.

        ``applyOrchestrationClustersEdgeAppsVersion``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/edge-apps/version/apply``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to initiate upgrades. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/edge-apps/version/apply",
            {"cluster_name": cluster_name},
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
                "404": response.Error,
                "406": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_orchestration_clusters_edge_apps_version_force(
        cls, cluster_name: str, persist: Optional[bool] = None, _dry_run: bool = False, _client: Any = None
    ) -> None:
        """
        Force available updates to Cluster even if update setting is disabled. Optionally keep a force update action on standby if the Cluster is offline. This ensures the update is applied once the Cluster returns online.

        **Permission Required:** `kelvin.permission.cluster.update`.

        ``updateOrchestrationClustersEdgeAppsVersionForce``: ``POST`` ``/api/v4/orchestration/clusters/{cluster_name}/edge-apps/version/force-update``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to initiate upgrades. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        persist : :obj:`bool`
            Optional setting to wait if the Cluster is currently unreachable and
            force the update when the Cluster is next online.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/orchestration/clusters/{cluster_name}/edge-apps/version/force-update",
            {"cluster_name": cluster_name},
            {"persist": persist},
            {},
            {},
            None,
            None,
            False,
            {
                "200": None,
                "202": None,
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
    def get_orchestration_clusters(
        cls, cluster_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.OrchestrationClustersGet:
        """
        Retrieve the parameters and status of a Cluster.

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``getOrchestrationClusters``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/get``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/get",
            {"cluster_name": cluster_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.OrchestrationClustersGet,
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
    def get_orchestration_clusters_manifests(
        cls, cluster_name: str, version: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.OrchestrationClustersManifestsGet:
        """
        Get Cluster Manifests

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``getOrchestrationClustersManifests``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/manifests/get``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to retrieve provision yaml file. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        version : :obj:`str`, optional
            Current version of the key `kelvin_version` in `version` object of the
            Cluster parameters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/manifests/get",
            {"cluster_name": cluster_name},
            {"version": version},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.OrchestrationClustersManifestsGet,
                "204": None,
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
    def list_orchestration_clusters_node(
        cls,
        cluster_name: str,
        search: Optional[Sequence[str]] = None,
        status: Optional[Sequence[str]] = None,
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
    ) -> Union[
        KList[responses.OrchestrationClustersNodesGetItem],
        responses.OrchestrationClustersNodeListPaginatedResponseCursor,
    ]:
        """
        Returns a list of Node objects in a Cluster. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``listOrchestrationClustersNode``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/nodes/list``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` containing the Nodes to list. The filter is on the
            full name only. Can only contain lowercase alphanumeric characters and
            `.`, `_` or `-` characters.
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the Node `name`. The search is
            case insensitive and will find partial matches as well.
        status : :obj:`Sequence[str]`
            A filter on the list based on the Node key `status`. The filter is on
            the full name only. All strings in the array are treated as `OR`.
            Options are `online`, `unreachable` and `not_ready`
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
            Sort the results by one of the Cluster parameters. Only one parameter
            can be selected. Options: `id`, `name`, `status`, `last_seen`,
            `created` and `updated`.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/nodes/list",
            {"cluster_name": cluster_name},
            {
                "search": search,
                "status": status,
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
                "200": responses.OrchestrationClustersNodeListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[
                    KList[responses.OrchestrationClustersNodesGetItem],
                    responses.OrchestrationClustersNodeListPaginatedResponseCursor,
                ],
                cls.fetch(_client, "/api/v4/orchestration/clusters/{cluster_name}/nodes/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def get_orchestration_clusters_nodes(
        cls, cluster_name: str, node_name: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.OrchestrationClustersNodesGet:
        """
        Retrieve the parameters and status of a specific Node on a Cluster.

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``getOrchestrationClustersNodes``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/nodes/{node_name}/get``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to look for Node. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        node_name : :obj:`str`, optional
            Node key `name` to get. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/nodes/{node_name}/get",
            {"cluster_name": cluster_name, "node_name": node_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {
                "200": responses.OrchestrationClustersNodesGet,
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
    def get_orchestration_clusters_provision(
        cls, cluster_name: str, _dry_run: bool = False, _client: Any = None
    ) -> str:
        """
        Get Clusters Provision YAML Specifications

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``getOrchestrationClustersProvision``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/provision/get``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` to retrieve provision yaml file. The string can
            only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/provision/get",
            {"cluster_name": cluster_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": str, "400": response.Error, "401": response.Error, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def list_orchestration_clusters_service(
        cls,
        cluster_name: str,
        search: Optional[Sequence[str]] = None,
        workload_name: Optional[Sequence[str]] = None,
        service_type: Optional[Sequence[str]] = None,
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
    ) -> Union[KList[responses.ServiceItem], responses.OrchestrationClustersServiceListPaginatedResponseCursor]:
        """
        Returns a list of Service objects in a Cluster. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.cluster.read`.

        ``listOrchestrationClustersService``: ``GET`` ``/api/v4/orchestration/clusters/{cluster_name}/services/list``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` containing the Services to list. The filter is on
            the full name only. Can only contain lowercase alphanumeric characters
            and `.`, `_` or `-` characters.
        search : :obj:`Sequence[str]`
            Search and filter on the list based on any of the Service keys `name`,
            `workload_name`, `network_interface`, `address`, and `service_type`.
            The search is case insensitive and will find partial matches as well.
            All strings in the array are treated as `OR`.
        workload_name : :obj:`Sequence[str]`
            A filter on the list based on the Workload key `name`. The filter is
            on the full name only. All strings in the array are treated as `OR`.
        service_type : :obj:`Sequence[str]`
            A filter on the list based on the Service Type key `service_type`. The
            filter is on the full name only. All strings in the array are treated
            as `OR`. Options are `cluster_ip`, `node_port` and `host_port`.
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
            Sort the results by one of the Cluster parameters. Only one parameter
            can be selected. Options: `name`, `workload_name`,
            `network_interface`, `service_type`, `address`, `created` and
            `updated`.

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/orchestration/clusters/{cluster_name}/services/list",
            {"cluster_name": cluster_name},
            {
                "search": search,
                "workload_name": workload_name,
                "service_type": service_type,
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
                "200": responses.OrchestrationClustersServiceListPaginatedResponseCursor,
                "400": response.Error,
                "401": response.Error,
                "500": response.Error,
            },
            False,
            _dry_run,
        )
        return (
            cast(
                Union[KList[responses.ServiceItem], responses.OrchestrationClustersServiceListPaginatedResponseCursor],
                cls.fetch(_client, "/api/v4/orchestration/clusters/{cluster_name}/services/list", result, "GET"),
            )
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def update_orchestration_clusters(
        cls,
        cluster_name: str,
        data: Optional[Union[requests.OrchestrationClustersUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.OrchestrationClustersUpdate:
        """
        Update the configuration settings of the Cluster. Only key/values provided in the request body will be updated, all other settings will remain unchanged.

        **Permission Required:** `kelvin.permission.cluster.update`.

        ``updateOrchestrationClusters``: ``POST`` ``/api/v4/orchestration/clusters/{cluster_name}/update``

        Parameters
        ----------
        cluster_name : :obj:`str`, optional
            Cluster key `name` target for sending parameter updates. The string
            can only contain lowercase alphanumeric characters and `.`, `_` or `-`
            characters.
        data: requests.OrchestrationClustersUpdate, optional
        **kwargs:
            Extra parameters for requests.OrchestrationClustersUpdate
              - update_orchestration_clusters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/orchestration/clusters/{cluster_name}/update",
            {"cluster_name": cluster_name},
            {},
            {},
            {},
            data,
            "requests.OrchestrationClustersUpdate",
            False,
            {
                "200": responses.OrchestrationClustersUpdate,
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
