from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, RootModel, StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.api.client.base_model import BaseModelRoot
from kelvin.api.client.data_model import DataModelBase
from kelvin.krn import KRN

from . import enum, manifest, type
from .manifest import AppManifest
from .postparams import AppVersionParameterListBase
from .type import (
    AppDeploymentRuntimeResources,
    CustomActionCreationFields,
    DataQualityCreationFields,
    GuardrailConfig,
    GuardrailConfigWithResource,
    ParameterScheduleBase,
    RecommendationBase,
    WorkloadModifiableFields,
    WorkloadNamesList,
)


class AppVersionCreate(AppManifest):
    """
    AppVersionCreate object.

    Parameters
    ----------

    """


class AppVersionPatch(DataModelBase):
    """
    AppVersionPatch object.

    Parameters
    ----------
        schemas: Optional[manifest.Schemas]
        defaults: Optional[manifest.Defaults]

    """

    schemas: Optional[manifest.Schemas] = None
    defaults: Optional[manifest.Defaults] = None


class AppVersionUpdate(DataModelBase):
    """
    AppVersionUpdate object.

    Parameters
    ----------
        schemas: Optional[manifest.Schemas]
        defaults: Optional[manifest.Defaults]

    """

    schemas: Optional[manifest.Schemas] = None
    defaults: Optional[manifest.Defaults] = None


class Deployment(DataModelBase):
    """
    Deployment object.

    Parameters
    ----------
        deployment_type: Optional[enum.DeploymentType]
        max_resources: Optional[StrictInt]
        target: Optional[manifest.DeploymentTarget]

    """

    deployment_type: Optional[enum.DeploymentType] = None
    max_resources: Optional[StrictInt] = Field(
        None,
        description="Maximum number of resources that a single workload handles when deploying the application. This is only relevant if the application supports multiple assets.",
    )
    target: Optional[manifest.DeploymentTarget] = None


class AppVersionDeploy(DataModelBase):
    """
    AppVersionDeploy object.

    Parameters
    ----------
        runtime: Optional[type.AppDeploymentRuntime]
        system: Optional[manifest.System]
        deployment: Optional[Deployment]

    """

    runtime: Optional[type.AppDeploymentRuntime] = None
    system: Optional[manifest.System] = None
    deployment: Optional[Deployment] = Field(None, description="Default rules for application deployment.")


class AppResourcesEnable(DataModelBase):
    """
    AppResourcesEnable object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = None


class AppResourcesDisable(DataModelBase):
    """
    AppResourcesDisable object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = None


class AppResourcesDelete(DataModelBase):
    """
    AppResourcesDelete object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = None


class AppPatch(DataModelBase):
    """
    AppPatch object.

    Parameters
    ----------
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        category: Optional[StrictStr]

    """

    title: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    category: Optional[StrictStr] = None


class AppsContextList(DataModelBase):
    """
    AppsContextList object.

    Parameters
    ----------
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = None
    sources: Optional[List[KRN]] = None


class AppVersionParameterValuesList(AppVersionParameterListBase):
    """
    AppVersionParameterValuesList object.

    Parameters
    ----------

    """


class AppVersionParametersHistoryList(AppVersionParameterListBase):
    """
    AppVersionParametersHistoryList object.

    Parameters
    ----------
        start_date: Optional[datetime]
        end_date: Optional[datetime]

    """

    start_date: Optional[datetime] = Field(
        None,
        description="Earliest `created` time for the list of Parameters. Time is based on UTC timezone, formatted in RFC 3339.",
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Most recent `created` time for the list of Parameters. Time is based on UTC timezone, formatted in RFC 3339.",
    )


class AppParametersList(DataModelBase):
    """
    AppParametersList object.

    Parameters
    ----------
        app_names: Optional[List[StrictStr]]
        names: Optional[List[StrictStr]]
        data_types: Optional[List[enum.ParameterType]]
        search: Optional[List[StrictStr]]

    """

    app_names: Optional[List[StrictStr]] = Field(
        None,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    names: Optional[List[StrictStr]] = Field(None, description="Unique identifier name for this Parameter.")
    data_types: Optional[List[enum.ParameterType]] = Field(
        None, description="Filter on the list based on the data type key `data_type` of the Parameter."
    )
    search: Optional[List[StrictStr]] = Field(
        None,
        description="Search and filter on the list based on the keys `parameter_name`. The search is case insensitive and will find partial matches as well. All strings in the array are treated as `OR`.",
    )


class AppVersionParametersUpdate(DataModelBase):
    """
    AppVersionParametersUpdate object.

    Parameters
    ----------
        source: Optional[KRN]
        resource_parameters: List[type.AppVersionResourceParameters]

    """

    source: Optional[KRN] = Field(None, description="The source of the change request (restricted to Service Accounts)")
    resource_parameters: List[type.AppVersionResourceParameters]


class AppVersionParametersDefaultsUpdate(DataModelBase):
    """
    AppVersionParametersDefaultsUpdate object.

    Parameters
    ----------
        parameters: Optional[List[type.ParameterItemNoComment]]

    """

    parameters: Optional[List[type.ParameterItemNoComment]] = None


class AppParameter(DataModelBase):
    """
    AppParameter object.

    Parameters
    ----------
        app_name: StrictStr
        parameters: Optional[List[StrictStr]]

    """

    app_name: StrictStr = Field(
        ...,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    parameters: Optional[List[StrictStr]] = Field(
        None, description="Array of Parameter `names` to fetch associated values for Apps."
    )


class AppVersionParametersUniqueValuesGet(DataModelBase):
    """
    AppVersionParametersUniqueValuesGet object.

    Parameters
    ----------
        app_parameters: Optional[List[AppParameter]]
        data_types: Optional[List[enum.ParameterType]]

    """

    app_parameters: Optional[List[AppParameter]] = Field(
        None,
        description="Filter on the list based on the key `app_name` and wanted Parameter `name` per App. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    data_types: Optional[List[enum.ParameterType]] = Field(
        None, description="Filter on the list based on the Parameter data type key `data_type` of the Parameter."
    )


class AppVersionParametersFallbackValuesGet(DataModelBase):
    """
    AppVersionParametersFallbackValuesGet object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = None


class ParametersScheduleCreate(ParameterScheduleBase):
    """
    ParametersScheduleCreate object.

    Parameters
    ----------

    """


class ParametersScheduleApply(DataModelBase):
    """
    ParametersScheduleApply object.

    Parameters
    ----------
        type: enum.ParameterScheduleApplyType

    """

    type: enum.ParameterScheduleApplyType


class App(DataModelBase):
    """
    App object.

    Parameters
    ----------
        name: StrictStr
        version: Optional[StrictStr]

    """

    name: StrictStr = Field(..., description="Application key `name` to filter the returned Parameter Schedule list.")
    version: Optional[StrictStr] = Field(None, description="Version of Application.")


class ParametersScheduleList(DataModelBase):
    """
    ParametersScheduleList object.

    Parameters
    ----------
        apps: Optional[List[App]]
        states: Optional[List[enum.ParameterScheduleState]]
        resources: Optional[List[KRN]]
        parameter_names: Optional[List[StrictStr]]

    """

    apps: Optional[List[App]] = Field(None, description="Array of Applications to filter.")
    states: Optional[List[enum.ParameterScheduleState]] = Field(
        None, description="Array of filtered states for the returned Parameter Schedule list."
    )
    resources: Optional[List[KRN]] = Field(
        None, description="Array of filtered Assets for the returned Parameter Schedule list."
    )
    parameter_names: Optional[List[StrictStr]] = Field(
        None, description="Array of filtered Parameter names for the returned Parameter Schedule list."
    )


class WorkloadCreate(WorkloadModifiableFields):
    """
    WorkloadCreate object.

    Parameters
    ----------
        name: StrictStr
        title: Optional[StrictStr]
        app_name: StrictStr

    """

    name: StrictStr
    title: Optional[StrictStr] = None
    app_name: StrictStr


class WorkloadUpdate(WorkloadModifiableFields):
    """
    WorkloadUpdate object.

    Parameters
    ----------

    """


class WorkloadsApply(WorkloadNamesList):
    """
    WorkloadsApply object.

    Parameters
    ----------

    """


class WorkloadsStart(WorkloadNamesList):
    """
    WorkloadsStart object.

    Parameters
    ----------

    """


class WorkloadsStop(WorkloadNamesList):
    """
    WorkloadsStop object.

    Parameters
    ----------

    """


class WorkloadsDelete(WorkloadNamesList):
    """
    WorkloadsDelete object.

    Parameters
    ----------

    """


class WorkloadResourcesAdd(AppDeploymentRuntimeResources):
    """
    WorkloadResourcesAdd object.

    Parameters
    ----------

    """


class WorkloadResourcesRemove(DataModelBase):
    """
    WorkloadResourcesRemove object.

    Parameters
    ----------
        resources: Optional[List[StrictStr]]

    """

    resources: Optional[List[StrictStr]] = None


class WorkloadsBulkUpdate(DataModelBase):
    """
    WorkloadsBulkUpdate object.

    Parameters
    ----------
        workload_names: Optional[List[StrictStr]]
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]
        runtime: Optional[type.AppDeploymentRuntime]
        system: Optional[manifest.System]
        deployment_type: Optional[enum.DeploymentType]

    """

    workload_names: Optional[List[StrictStr]] = None
    app_name: Optional[StrictStr] = None
    app_version: Optional[StrictStr] = None
    runtime: Optional[type.AppDeploymentRuntime] = None
    system: Optional[manifest.System] = None
    deployment_type: Optional[enum.DeploymentType] = None


class AppExtraField(DataModelBase):
    """
    AppExtraField object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        app_versions: Optional[List[StrictStr]]
        name: Optional[StrictStr]

    """

    app_name: Optional[StrictStr] = Field(
        None,
        description="App Name from the App Registry. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-optimization"],
    )
    app_versions: Optional[List[StrictStr]] = Field(
        None,
        description="Filter Apps by version number of the App. The filter is on the full version name only. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["1.2.0", "1.2.1"]],
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["app-motor-speed-optimization"],
    )


class AssetInsightsFilter(DataModelBase):
    """
    AssetInsightsFilter object.

    Parameters
    ----------
        operator: Optional[enum.AssetInsightsOperator]
        value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]

    """

    operator: Optional[enum.AssetInsightsOperator] = None
    value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None, description="Value to use in association with the `operator` for the filter of the field.", examples=[500]
    )


class AssetPropertyExtraField(DataModelBase):
    """
    AssetPropertyExtraField object.

    Parameters
    ----------
        filters: Optional[List[AssetInsightsFilter]]
        name: Optional[StrictStr]
        primitive_type: Optional[enum.PropertyType]
        property_name: Optional[StrictStr]

    """

    filters: Optional[List[AssetInsightsFilter]] = Field(
        None,
        description="Optional to filter the returned Asset List based on an array of operator / value criteria relating to the Asset Property. Each filter is treated as `AND`. This will remove Assets from the returned Asset list that do not meet this criteria.",
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["property-area"],
    )
    primitive_type: Optional[enum.PropertyType] = Field(
        None, description="Property data type of the new filtered Asset Property column."
    )
    property_name: Optional[StrictStr] = Field(
        None,
        description="Name of the Asset Property to include. This Asset Property column are custom filtered fields that can be created with the Asset listing.",
        examples=["area"],
    )


class Datastream(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=["motor-speed"])


class ControlChangeExtraField(DataModelBase):
    """
    ControlChangeExtraField object.

    Parameters
    ----------
        datastreams: Optional[List[Datastream]]
        name: Optional[StrictStr]
        since: Optional[datetime]
        statuses: Optional[List[enum.ControlChangeState]]

    """

    datastreams: Optional[List[Datastream]] = Field(
        None,
        description="Filter Control Change Field by Control Change Data Stream key `datastream_name`. The filter is on the full name only. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["last-control-change"],
    )
    since: Optional[datetime] = Field(
        None,
        description="UTC time for the earliest creation time of Control Changes associated with an Asset, formatted in RFC 3339. Control Changes before this time regardless of `state` will be ignored.",
        examples=["2025-11-13T12:00:00Z"],
    )
    statuses: Optional[List[enum.ControlChangeState]] = Field(
        None,
        description="Filter Control Change Field by the Control Change current `state`.",
        examples=[["pending", "sent"]],
    )


class CustomActionExtraField(DataModelBase):
    """
    CustomActionExtraField object.

    Parameters
    ----------
        name: Optional[StrictStr]
        type: Optional[StrictStr]
        since: Optional[datetime]
        statuses: Optional[List[enum.CustomActionState]]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["last-custom-action"],
    )
    type: Optional[StrictStr] = Field(
        None,
        description="Filter Custom Action Field by the Custom Action `type`. The filter is on the full name only.",
        examples=["Email"],
    )
    since: Optional[datetime] = Field(
        None,
        description="UTC time for the earliest creation time of Custom Actions associated with an Asset, formatted in RFC 3339. Custom Actions before this time regardless of `state` will be ignored.",
        examples=["2025-12-13T12:00:00Z"],
    )
    statuses: Optional[List[enum.CustomActionState]] = Field(
        None,
        description="Filter Custom Action Field by the Custom Action current `state`.",
        examples=[["pending", "completed"]],
    )


class DatastreamExtraFieldComputation(DataModelBase):
    """
    DatastreamExtraFieldComputation object.

    Parameters
    ----------
        agg: Optional[enum.AssetInsightsAgg]
        end_time: Optional[datetime]
        start_time: Optional[datetime]

    """

    agg: Optional[enum.AssetInsightsAgg] = None
    end_time: Optional[datetime] = Field(
        None,
        description="UTC time for the latest time in the time range used by `agg` of Data Streams related to an Asset, formatted in RFC 3339.",
        examples=["2023-11-13T12:00:00Z"],
    )
    start_time: Optional[datetime] = Field(
        None,
        description="UTC time for the earliest time in the time range used by `agg` of Data Streams related to an Asset, formatted in RFC 3339.",
        examples=["2023-11-13T12:00:00Z"],
    )


class DatastreamExtraField(DataModelBase):
    """
    DatastreamExtraField object.

    Parameters
    ----------
        computation: Optional[DatastreamExtraFieldComputation]
        datastream_name: Optional[StrictStr]
        name: Optional[StrictStr]
        filters: Optional[List[AssetInsightsFilter]]

    """

    computation: Optional[DatastreamExtraFieldComputation] = None
    datastream_name: Optional[StrictStr] = Field(
        None,
        description="Data Stream key `name`. Used in connection with the Asset `name` to retrieve the Asset / Data Stream pair's data",
        examples=["motor-speed"],
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["datastream-motor-speed"],
    )
    filters: Optional[List[AssetInsightsFilter]] = Field(
        None,
        description="Optional to filter the returned Asset List based on an array of operator / value criteria relating to the Datastream. Each filter is treated as `AND`. This will remove Assets from the returned Asset list that do not meet this criteria.",
    )


class ParameterExtraField(DataModelBase):
    """
    ParameterExtraField object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        filters: Optional[List[AssetInsightsFilter]]
        name: Optional[StrictStr]
        parameter_name: Optional[StrictStr]
        primitive_type: Optional[enum.ParameterType]

    """

    app_name: Optional[StrictStr] = Field(
        None,
        description="App Registry App key `name` to retrieve the Parameters. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-optimization"],
    )
    filters: Optional[List[AssetInsightsFilter]] = Field(
        None,
        description="Optional to filter the returned Asset List based on an array of operator / value criteria relating to the Parameters. Each filter is treated as `AND`. This will remove Assets from the returned Asset list that do not meet this criteria.",
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["motor-speed-set-point-low"],
    )
    parameter_name: Optional[StrictStr] = Field(
        None,
        description="Parameter key `name` to retrieve the Parameters from the App for the Assets. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-set-point"],
    )
    primitive_type: Optional[enum.ParameterType] = None


class Type(BaseModelRoot[StrictStr]):
    root: StrictStr


class RecommendationExtraField(DataModelBase):
    """
    RecommendationExtraField object.

    Parameters
    ----------
        name: Optional[StrictStr]
        since: Optional[datetime]
        source: Optional[KRN]
        states: Optional[List[enum.RecommendationState]]
        types: Optional[List[Type]]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["motor-speed-recommendations"],
    )
    since: Optional[datetime] = Field(
        None,
        description="UTC time for the earliest creation time of Recommendations associated with an Asset, formatted in RFC 3339. Recommendations before this time regardless of `state` will be ignored.",
        examples=["2023-11-13T12:00:00Z"],
    )
    source: Optional[KRN] = Field(
        None,
        description="KRN of the User or Service that created the Recommendation.",
        examples=["krn:user:richard.teo@kelvininc.com"],
    )
    states: Optional[List[enum.RecommendationState]] = Field(
        None,
        description="Only return Recommendations associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["pending", "auto_accepted"]],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="Only return Recommendations associated with one or more Recommendation Types. The filter is on the full Recommendation Type `name` only. All strings in the array are treated as `OR`.",
        examples=[["Decrease speed", "increase_speed"]],
    )


class ParametersScheduleExtraField(DataModelBase):
    """
    ParametersScheduleExtraField object.

    Parameters
    ----------
        name: Optional[StrictStr]
        schedule_type: Optional[enum.AssetInsightsParameterScheduleType]
        max_date: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier name for the key in the response, all keys in extra_fields object must be unique.",
        examples=["next-schedule"],
    )
    schedule_type: Optional[enum.AssetInsightsParameterScheduleType] = None
    max_date: Optional[datetime] = Field(
        None,
        description="UTC time for the latest time of a Schedule associated with an Asset, formatted in RFC 3339. Schedules after this time will be ignored.",
        examples=["2024-04-26T12:00:00Z"],
    )


class AssetInsightsExtraFields(DataModelBase):
    """
    AssetInsightsExtraFields object.

    Parameters
    ----------
        apps: Optional[List[AppExtraField]]
        asset_properties: Optional[List[AssetPropertyExtraField]]
        control_changes: Optional[List[ControlChangeExtraField]]
        custom_actions: Optional[List[CustomActionExtraField]]
        datastreams: Optional[List[DatastreamExtraField]]
        parameters: Optional[List[ParameterExtraField]]
        recommendations: Optional[List[RecommendationExtraField]]
        parameters_schedule: Optional[List[ParametersScheduleExtraField]]

    """

    apps: Optional[List[AppExtraField]] = Field(
        None,
        description="Create new columns based on Apps in the App Registry related to Assets. Multiple columns can be created, each with different App filter requirements.",
    )
    asset_properties: Optional[List[AssetPropertyExtraField]] = Field(
        None,
        description="Create new columns based on the `property` field in Assets. Multiple columns can be created, each with different `property` requirements. Separately, the `filter` option will remove Assets from the returned Asset list that do not meet the operator and value criteria.",
    )
    control_changes: Optional[List[ControlChangeExtraField]] = Field(
        None,
        description="Create new columns based on the Last Control Changes associated with the Asset. Multiple columns can be created, each with different Control Change filter requirements.",
    )
    custom_actions: Optional[List[CustomActionExtraField]] = Field(
        None,
        description="Create new columns based on the Last Custom Actions associated with the Asset. Multiple columns can be created, each with different Custom Action filter requirements.",
    )
    datastreams: Optional[List[DatastreamExtraField]] = Field(
        None,
        description="Create new columns based on mathematical calculations for a time range of a Data Stream associated with the Assets. Multiple columns can be created, each with its own mathematical formula and Asset / Data Stream pair.",
    )
    parameters: Optional[List[ParameterExtraField]] = Field(
        None,
        description="Create new columns based on Application Parameters associated with the Asset. Multiple columns can be created, each with different Application Parameters requirements. Separately, the `filter` option will remove Assets from the returned Asset list that do not meet the operator and value criteria.",
    )
    recommendations: Optional[List[RecommendationExtraField]] = Field(
        None,
        description="Create new columns based on Recommendations associated with the Asset. Multiple columns can be created, each with different Recommendation filter requirements.",
    )
    parameters_schedule: Optional[List[ParametersScheduleExtraField]] = Field(
        None,
        description="Create new columns based on the Parameters Schedule associated with the Asset. Multiple columns can be created, each with different Schedule filter requirements.",
    )


class AssetInsightsSortBy(DataModelBase):
    """
    AssetInsightsSortBy object.

    Parameters
    ----------
        direction: Optional[enum.AssetInsightsSortByDirection]
        field: Optional[StrictStr]
        sort_by_extra_field: Optional[StrictBool]

    """

    direction: Optional[enum.AssetInsightsSortByDirection] = enum.AssetInsightsSortByDirection.asc
    field: Optional[StrictStr] = Field(
        "name",
        description="Key name of the Asset or `extra_field` field `name` to sort by. Source of field will be determined by the `SortByExtraField` key. If sorting by Asset key, available options are; `name`, `title`, `asset_type_name`, `asset_type_title` and `state`.",
        examples=["title"],
    )
    sort_by_extra_field: Optional[StrictBool] = Field(
        None,
        description="Choose the `sort_by` source of the `field` parameter. If `false`, the source of the `field` name is an Asset key. If `true`, the source is a `extra_field[].name` key.",
        examples=[False],
    )


class AssetName(BaseModelRoot[StrictStr]):
    root: StrictStr


class AssetType(BaseModelRoot[StrictStr]):
    root: StrictStr


class PinnedAsset(BaseModelRoot[StrictStr]):
    root: StrictStr


class SearchItem(BaseModelRoot[StrictStr]):
    root: StrictStr


class AssetInsightsGet(DataModelBase):
    """
    AssetInsightsGet object.

    Parameters
    ----------
        asset_names: Optional[List[AssetName]]
        asset_states: Optional[List[enum.AssetState]]
        asset_types: Optional[List[AssetType]]
        extra_fields: Optional[AssetInsightsExtraFields]
        force_parameters_refresh: Optional[StrictBool]
        pinned_assets: Optional[List[PinnedAsset]]
        search: Optional[List[SearchItem]]
        sort_by: Optional[List[AssetInsightsSortBy]]

    """

    asset_names: Optional[List[AssetName]] = Field(
        None,
        description="Filter on the Asset parameter `name`. The filter is on the full name only. All strings in the array are treated as `OR`. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["beam", "MOTOR"]],
    )
    asset_states: Optional[List[enum.AssetState]] = Field(
        None,
        description="Filter by the asset `state`. The filter is on the full name only. All strings in the array are treated as `OR`.",
        examples=[["offline", "unknown"]],
    )
    asset_types: Optional[List[AssetType]] = Field(
        None,
        description="Filter on the Asset Type parameter `name`. The filter is on the full name only. All strings in the array are treated as `OR`. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["decrease_speed", "increase_speed"]],
    )
    extra_fields: Optional[AssetInsightsExtraFields] = None
    force_parameters_refresh: Optional[StrictBool] = Field(
        None, description="Force all parameters to be refreshed.", examples=[True]
    )
    pinned_assets: Optional[List[PinnedAsset]] = Field(
        None,
        description="List of Asset names that should always appear at the top of page 1 of any search results. The filter is on the full name only. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["beam_pump_01", "beam_pump_32"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter on the list based on the Asset keys `title` (Display Name) or `name`. The search is case insensitive and will find partial matches as well.",
        examples=[["beam", "Motor"]],
    )
    sort_by: Optional[List[AssetInsightsSortBy]] = Field(None, description="Options for sorting the returned results.")


class AssetPropertyCreate(DataModelBase):
    """
    AssetPropertyCreate object.

    Parameters
    ----------
        name: StrictStr
        title: Optional[StrictStr]
        value: Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]

    """

    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` for the Asset Property. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["water-line-pressure"],
    )
    title: Optional[StrictStr] = Field(
        None,
        description="Title for this property. This title is ignored if the property with this `name` already exists.",
        examples=["Water Line Pressure"],
    )
    value: Union[
        StrictInt,
        StrictFloat,
        StrictStr,
        StrictBool,
        List[StrictInt],
        List[StrictFloat],
        List[StrictStr],
        List[StrictBool],
    ]


class AssetCreate(DataModelBase):
    """
    AssetCreate object.

    Parameters
    ----------
        asset_type_name: StrictStr
        name: StrictStr
        properties: Optional[List[AssetPropertyCreate]]
        title: StrictStr

    """

    asset_type_name: StrictStr = Field(
        ...,
        description="Asset Type `name`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["beam_pump"],
    )
    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` for the Asset. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["well_01"],
    )
    properties: Optional[List[AssetPropertyCreate]] = Field(
        None,
        description="Array of custom properties. These properties are not used by the Kelvin Platform and are for end-user use only.",
    )
    title: StrictStr = Field(..., description="Asset display name (`title`).", examples=["Well 01"])


class AssetBulkCreate(DataModelBase):
    """
    AssetBulkCreate object.

    Parameters
    ----------
        assets: List[AssetCreate]

    """

    assets: List[AssetCreate] = Field(
        ..., description="Array of objects, each object in the array represents a new Asset.", min_length=1
    )


class Name(BaseModelRoot[StrictStr]):
    root: StrictStr


class AssetsAdvancedList(DataModelBase):
    """
    AssetsAdvancedList object.

    Parameters
    ----------
        asset_type_name: Optional[List[StrictStr]]
        names: Optional[List[Name]]
        search: Optional[List[SearchItem]]
        status_state: Optional[List[enum.AssetState]]

    """

    asset_type_name: Optional[List[StrictStr]] = Field(
        None,
        description="A filter on the list based on the key `asset_type_name`. The filter is on the full name only. All strings in the array are treated as `OR`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["beam_pump", "progressive_cavity_pump"]],
    )
    names: Optional[List[Name]] = Field(
        None,
        description="A filter on the list based on the key `name`. The filter is on the full name only. All strings in the array are treated as `OR`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["well_1", "well_5"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter on the list based on the keys `title` (Display Name) or `name`. All strings in the array are treated as `OR`. The search is case insensitive and will find partial matches as well.",
        examples=[["well_1", "Well 3"]],
    )
    status_state: Optional[List[enum.AssetState]] = Field(
        None,
        description="A filter on the list based on the key ['status']['state']. Multiple statuses can be given and will be filtered as `OR`.",
        examples=[["online"]],
    )


class AssetTypeCreate(DataModelBase):
    """
    AssetTypeCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr

    """

    name: StrictStr = Field(
        ...,
        description="Unique Asset Type name. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["beam_pump"],
    )
    title: StrictStr = Field(..., description="Asset Type display name (`title`).", examples=["Beam Pump"])


class AssetTypesAdvancedList(DataModelBase):
    """
    AssetTypesAdvancedList object.

    Parameters
    ----------
        names: Optional[List[Name]]
        search: Optional[List[SearchItem]]

    """

    names: Optional[List[Name]] = Field(
        None,
        description="A filter on the list based on the key `name`. The filter is on the full name only. All strings in the array are treated as `OR`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["pump", "centrifugal_pump"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter the Kelvin Asset Type list. Both the Display Name and the Name will be included in the search field criteria. This is given as an array, for example `[pump,fan]`. The search is case insensitive and will find partial matches as well. For example if a Kelvin Asset Type name is `centrifugal_pump`, then a match will be made if the search string is `pum` or `FUGaL`.",
        examples=[["pump", "fan"]],
    )


class NameModel(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=[["pump", "fan"]])


class AssetTypeBulkDelete(DataModelBase):
    """
    AssetTypeBulkDelete object.

    Parameters
    ----------
        names: List[NameModel]

    """

    names: List[NameModel] = Field(..., description="List of asset type names to be deleted.", min_length=1)


class AssetTypeUpdate(DataModelBase):
    """
    AssetTypeUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]

    """

    title: Optional[StrictStr] = Field(
        None, description="New Asset Type display name (`title`).", examples=["Beam Pump"]
    )


class NameModel1(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=[["well_1", "well_62"]])


class AssetBulkDelete(DataModelBase):
    """
    AssetBulkDelete object.

    Parameters
    ----------
        names: List[NameModel1]

    """

    names: List[NameModel1] = Field(..., description="List of asset names to be deleted.", min_length=1)


class AssetUpdate(DataModelBase):
    """
    AssetUpdate object.

    Parameters
    ----------
        asset_type_name: Optional[StrictStr]
        properties: Optional[List[AssetPropertyCreate]]
        title: StrictStr

    """

    asset_type_name: Optional[StrictStr] = Field(
        None,
        description="Asset Type `name`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["beam_pump"],
    )
    properties: Optional[List[AssetPropertyCreate]] = Field(
        None,
        description="Array of custom properties. These properties are not used by the Kelvin Platform and are for end-user use only.",
    )
    title: StrictStr = Field(..., description="Asset display name (`title`).", examples=["Well 01"])


class Resource(BaseModelRoot[StrictStr]):
    root: StrictStr


class Source(BaseModelRoot[StrictStr]):
    root: StrictStr


class ControlChangeClusteringGet(DataModelBase):
    """
    ControlChangeClusteringGet object.

    Parameters
    ----------
        end_date: datetime
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        start_date: datetime
        states: Optional[List[enum.ControlChangeState]]
        time_bucket: StrictStr

    """

    end_date: datetime = Field(
        ...,
        description="Most recent (end) creation time for counting the number of Control Changes. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="Filter Assets / Data Streams (`resources`) linked to Control Changes for inclusion in the count. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset and Data Stream name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:ad:bp_01/motor_speed_set_point", "krn:ad:bp_16/motor_speed_set_point"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="Filter to only count Control Changes from certain `sources`. The filter is on the full name only. All strings in the array are treated as `OR`. Each KRN name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:app:motor-speed-control"]],
    )
    start_date: datetime = Field(
        ...,
        description="Earliest (start) creation time for counting the  number of Control Changes. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    states: Optional[List[enum.ControlChangeState]] = Field(
        None,
        description="Filter to only count Control Changes associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["sent", "applied"]],
    )
    time_bucket: StrictStr = Field(
        ..., description="Defines the time range to use to group and count the Control Changes.", examples=["5m"]
    )


class ControlChangeCreate(DataModelBase):
    """
    ControlChangeCreate object.

    Parameters
    ----------
        expiration_date: datetime
        from_: Optional[type.ControlChangeFrom]
        payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]
        trace_id: Optional[StrictStr]
        resource: KRN
        retries: Optional[StrictInt]
        timeout: Optional[StrictInt]

    """

    expiration_date: datetime = Field(
        ...,
        description="UTC time when the Control Change will expire and the `status` automatically marked as `failed`, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    from_: Optional[type.ControlChangeFrom] = Field(None, alias="from")
    payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ...,
        description="The new value payload to be applied to the Asset / Data Stream pair in `resource`.",
        examples=[2000],
    )
    trace_id: Optional[StrictStr] = None
    resource: KRN = Field(
        ...,
        description="The asset / data stream pair that this Control Change will be applied to.",
        examples=["krn:ad:beam_pump_01/motor_speed_set_point"],
    )
    retries: Optional[StrictInt] = Field(
        None,
        description="How many times the Control Change Manager will try and send the same Control Change request to the Bridge before the change is tagged `failed` and no further attempts will be made. If the Bridge sends a `processed` acknowledgment, then the Control Change Manager will stop any further retries and wait for an `applied` response.",
        examples=[3],
    )
    timeout: Optional[StrictInt] = Field(
        None,
        description="How long the Control Change Manager will wait in seconds for the Bridge to send a `processed` acknowledgement before a retry will be attempted. If the total number of retries has reach its `retries` limit, then the change is tagged `failed` and no further attempts will be made.",
        examples=[150],
    )


class TraceId(BaseModelRoot[StrictStr]):
    root: StrictStr


class ControlChangeLastGet(DataModelBase):
    """
    ControlChangeLastGet object.

    Parameters
    ----------
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        states: Optional[List[enum.ControlChangeState]]
        trace_ids: Optional[List[TraceId]]

    """

    resources: Optional[List[KRN]] = Field(
        None,
        description="Filter on the list to show Control Change for requested Asset / Data Stream pairs only. The filter is on the full KRN name only. All strings in the array are treated as `OR`. Each Asset and Data Stream name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:ad:beam_pump_02/motor_speed_set_point", "krn:ad:beam_pump_16/motor_speed_set_point"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="Filter on the list to show Control Change for requested `sources` only. The filter is on the full KRN name only. All strings in the array are treated as `OR`. Each `source` name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:user:person@kelvin.ai", "krn:app:motor_speed_control"]],
    )
    states: Optional[List[enum.ControlChangeState]] = Field(
        None,
        description="Filter on the Control Change states wanted. This will only check and filter on the `last_state` and not in the `status_log` object.",
        examples=[["sent", "applied"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Control Changes associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )


class ControlChangesList(DataModelBase):
    """
    ControlChangesList object.

    Parameters
    ----------
        ids: Optional[List[UUID]]
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        states: Optional[List[enum.ControlChangeState]]
        trace_ids: Optional[List[TraceId]]

    """

    ids: Optional[List[UUID]] = Field(
        None,
        description="Filter on the list to show only specific Control Changes.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "89df1fa1-72b3-4ffa-aae6-1a3e5324ee2e"]],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="Filter list to display only Control Changes for specified Asset/Data Stream pairs. The filter is on the full KRN name only. All strings in the array are treated as `OR`. Each Asset and Data Stream name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:ad:beam_pump_02/motor_speed_set_point", "krn:ad:beam_pump_16/motor_speed_set_point"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="Filter list to display only Control Changes for specified `sources` only. The filter is on the full KRN name only. All strings in the array are treated as `OR`. Each `source` name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:user:person@kelvin.ai", "krn:app:motor_speed_control"]],
    )
    states: Optional[List[enum.ControlChangeState]] = Field(
        None,
        description="Filter list to display only Control Changes for specified `states` only. This will only check and filter on the `last_state` and not in the `status_log` object.",
        examples=[["sent", "applied"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Cusotm Actions associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )


class ControlChangeRangeGet(DataModelBase):
    """
    ControlChangeRangeGet object.

    Parameters
    ----------
        end_date: datetime
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        start_date: datetime
        states: Optional[List[enum.ControlChangeState]]
        trace_ids: Optional[List[TraceId]]

    """

    end_date: datetime = Field(
        ...,
        description="Most recent (end) creation time for the list of Control Changes. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="Filter Assets / Data Streams (`resources`) linked to Control Changes for inclusion in the count. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset and Data Stream name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:ad:bp_01/motor_speed_set_point", "krn:ad:bp_16/motor_speed_set_point"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="Filter to only count Control Changes from certain `sources`. The filter is on the full name only. All strings in the array are treated as `OR`. Each KRN name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:app:motor-speed-control"]],
    )
    start_date: datetime = Field(
        ...,
        description="Earliest (start) creation time for counting the  number of Control Changes. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    states: Optional[List[enum.ControlChangeState]] = Field(
        None,
        description="Filter to only count Control Changes associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["sent", "applied"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Control Changes associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )


class CustomActionCreate(CustomActionCreationFields):
    """
    CustomActionCreate object.

    Parameters
    ----------

    """


class CreatedByItem(BaseModelRoot[StrictStr]):
    root: StrictStr


class CustomActionsList(DataModelBase):
    """
    CustomActionsList object.

    Parameters
    ----------
        ids: Optional[List[UUID]]
        resources: Optional[List[KRN]]
        created_by: Optional[List[KRN]]
        states: Optional[List[enum.CustomActionState]]
        types: Optional[List[Type]]
        trace_ids: Optional[List[TraceId]]

    """

    ids: Optional[List[UUID]] = Field(
        None,
        description="Search and filter on the list based on the key `id`. The filter is on the full UUID `id` only. All strings in the array are treated as `OR`.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "00080f9e-d086-452d-b41d-c8aa8fb27c92"]],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with any Assets in the array. The filter is on the full KRN Asset name only. All strings in the array are treated as `OR`. Each Asset name must be in the KRN format.",
        examples=[["krn:asset:bp_16", "krn:asset:bp_21"]],
    )
    created_by: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Custom Action created by a certain source. The filter is on the full `source` KRN name only. All strings in the array are treated as `OR`.",
        examples=[["krn:wlappv:cluster1/app1/1.2.0", "krn:user:richard.teo@kelvininc.com"]],
    )
    states: Optional[List[enum.CustomActionState]] = Field(
        None,
        description="A filter on the list showing only Custom Action associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["ready", "pending"]],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="A filter on the list showing only Cusotm Actions associated with one or more Custom Action Types. The filter is on the full Custom Action Type `name` only. All strings in the array are treated as `OR`.",
        examples=[["Email"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Custom Actions associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )


class CustomActionsTypeCreate(DataModelBase):
    """
    CustomActionsTypeCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        metadata: Optional[Dict[str, Any]]

    """

    name: StrictStr = Field(..., description="Unique identifier `name` for the Custom Action Type.", examples=["Email"])
    title: StrictStr = Field(
        ..., description="Unique identifier `title` for the Custom Action Type.", examples=["Email"]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Custom Action Type. The structure of the `metadata` object can have any key/value structure.",
    )


class CustomActionsTypeUpdate(DataModelBase):
    """
    CustomActionsTypeUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]

    """

    title: Optional[StrictStr] = Field(None, examples=["Email"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Custom Action Type. The structure of the `metadata` object can have any key/value structure.",
    )


class DataQualityCreate(DataQualityCreationFields):
    """
    DataQualityCreate object.

    Parameters
    ----------

    """


class DataQualityUpdate(DataModelBase):
    """
    DataQualityUpdate object.

    Parameters
    ----------
        configurations: Optional[type.DataQualityConfigurations]

    """

    configurations: Optional[type.DataQualityConfigurations] = None


class DataQualityList(DataModelBase):
    """
    DataQualityList object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = Field(
        None,
        description="Array of Asset or Asset/Data Stream pairs to filter the Data Qualities list on server before returning. (example: `krn:ad:asset1/setpoint`).",
    )


class BulkDataQualityCreate(DataModelBase):
    """
    BulkDataQualityCreate object.

    Parameters
    ----------
        data_qualities: Optional[List[type.DataQualityCreationFields]]

    """

    data_qualities: Optional[List[type.DataQualityCreationFields]] = Field(
        None, description="An array of Data Quality configurations to create."
    )


class BulkDataQualityUpdate(DataModelBase):
    """
    BulkDataQualityUpdate object.

    Parameters
    ----------
        data_qualities: Optional[List[type.DataQualityCreationFields]]

    """

    data_qualities: Optional[List[type.DataQualityCreationFields]] = Field(
        None, description="An array of Data Quality configurations to update."
    )


class BulkDataQualityDelete(DataModelBase):
    """
    BulkDataQualityDelete object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = Field(
        None,
        description="An array of Asset/Data Stream pairs or Asset for deleting the associated Data Qualities configurations. (example: `krn:ad:asset1/setpoint`).",
    )


class Configurations(DataModelBase):
    """
    Configurations object.

    Parameters
    ----------
        kelvin_duplicate_detection: Optional[type.KelvinDuplicateDetection]
        kelvin_out_of_range_detection: Optional[type.KelvinOutOfRangeDetection]
        kelvin_outlier_detection: Optional[type.KelvinOutlierDetection]
        kelvin_data_availability: Optional[type.KelvinDataAvailability]

    """

    kelvin_duplicate_detection: Optional[type.KelvinDuplicateDetection] = None
    kelvin_out_of_range_detection: Optional[type.KelvinOutOfRangeDetection] = None
    kelvin_outlier_detection: Optional[type.KelvinOutlierDetection] = None
    kelvin_data_availability: Optional[type.KelvinDataAvailability] = None


class DataQualitySimulate(DataModelBase):
    """
    DataQualitySimulate object.

    Parameters
    ----------
        resource: Optional[KRN]
        configurations: Optional[Configurations]
        start_time: Optional[datetime]
        end_time: Optional[datetime]

    """

    resource: Optional[KRN] = Field(
        None,
        description="The Asset/Data Stream pair to simulate the Data Quality configurations on. (example: `krn:ad:asset1/setpoint`).",
    )
    configurations: Optional[Configurations] = Field(None, description="The Data Quality configurations.")
    start_time: Optional[datetime] = Field(
        None,
        description="The start timestamp for the simulation, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    end_time: Optional[datetime] = Field(
        None,
        description="The end timestamp for the simulation, formatted in RFC 3339.",
        examples=["2024-12-19T18:22:18.582724Z"],
    )


class DataStreamSemanticTypeCreate(DataModelBase):
    """
    DataStreamSemanticTypeCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr

    """

    name: StrictStr = Field(
        ..., description="Unique identifier `name` of the new Semantic Type.", examples=["mass_flow_rate"]
    )
    title: StrictStr = Field(
        ..., description="Display name (`title`) of the new Semantic Type.", examples=["Mass Flow Rate"]
    )


class DataStreamSemanticTypeUpdate(DataModelBase):
    """
    DataStreamSemanticTypeUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]

    """

    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Semantic Type.", examples=["Mass Flow Rate"]
    )


class DataStreamUnitCreate(DataModelBase):
    """
    DataStreamUnitCreate object.

    Parameters
    ----------
        name: StrictStr
        symbol: StrictStr
        title: StrictStr

    """

    name: StrictStr = Field(
        ..., description="Unique identifier `name` of the new Unit.", examples=["degree_fahrenheit"]
    )
    symbol: StrictStr = Field(
        ...,
        description="A brief and precise character or set of characters that symbolize a specific measurement of the new Unit.",
        examples=["°F"],
    )
    title: StrictStr = Field(..., description="Display name (`title`) of the new Unit.", examples=["Degree Fahrenheit"])


class BulkDataStreamUnitCreate(DataModelBase):
    """
    BulkDataStreamUnitCreate object.

    Parameters
    ----------
        units: List[DataStreamUnitCreate]

    """

    units: List[DataStreamUnitCreate] = Field(
        ..., description="Array of objects, each object in the array represents a new Unit.", min_length=1
    )


class DataStreamUnitUpdate(DataModelBase):
    """
    DataStreamUnitUpdate object.

    Parameters
    ----------
        symbol: Optional[StrictStr]
        title: Optional[StrictStr]

    """

    symbol: Optional[StrictStr] = Field(
        None,
        description="A brief and precise character or set of characters that symbolize a specific measurement of the Unit.",
        examples=["°F"],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Unit.", examples=["Degree Fahrenheit"]
    )


class DataStreamCreate(DataModelBase):
    """
    DataStreamCreate object.

    Parameters
    ----------
        description: Optional[StrictStr]
        name: StrictStr
        data_type_name: enum.DataType
        semantic_type_name: Optional[StrictStr]
        title: StrictStr
        type: enum.DataStreamType
        unit_name: Optional[StrictStr]

    """

    description: Optional[StrictStr] = Field(
        None,
        description="Detailed description of the new Data Stream.",
        examples=["The rate at which gas flows from the reservoir to the surface."],
    )
    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` for the new Data Stream. Can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["gas_flow_rate"],
    )
    data_type_name: enum.DataType = Field(..., description="Data type of the new Data Stream.")
    semantic_type_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Semantic Type that describes the nature, purpose or origin of the data.",
        examples=["volume_flow_rate"],
    )
    title: StrictStr = Field(..., description="Display name (`title`) of the Data Stream.", examples=["Gas Flow Rate"])
    type: enum.DataStreamType
    unit_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Units that describes the type or category of data represented by each unit.",
        examples=["litre_per_second"],
    )


class BulkDataStreamCreate(DataModelBase):
    """
    BulkDataStreamCreate object.

    Parameters
    ----------
        datastreams: List[DataStreamCreate]

    """

    datastreams: List[DataStreamCreate] = Field(
        ..., description="Array of objects, each object in the array represents a new Datastream.", min_length=1
    )


class DataStreamUpdate(DataModelBase):
    """
    DataStreamUpdate object.

    Parameters
    ----------
        description: Optional[StrictStr]
        title: Optional[StrictStr]
        type: Optional[enum.DataStreamType]
        semantic_type_name: Optional[StrictStr]
        unit_name: Optional[StrictStr]

    """

    description: Optional[StrictStr] = Field(
        None,
        description="Detailed description of the Data Stream.",
        examples=["The rate at which gas flows from the reservoir to the surface."],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Data Stream.", examples=["Gas Flow Rate"]
    )
    type: Optional[enum.DataStreamType] = None
    semantic_type_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Semantic Type that describes the nature, purpose or origin of the data.",
        examples=["volume_flow_rate"],
    )
    unit_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Units that describes the type or category of data represented by each unit.",
        examples=["litre_per_second"],
    )


class DataTypeName(BaseModelRoot[StrictStr]):
    root: StrictStr


class NameModel2(BaseModelRoot[StrictStr]):
    root: StrictStr


class SemanticTypeName(BaseModelRoot[StrictStr]):
    root: StrictStr


class UnitName(BaseModelRoot[StrictStr]):
    root: StrictStr


class DataStreamsList(DataModelBase):
    """
    DataStreamsList object.

    Parameters
    ----------
        data_type_names: Optional[List[DataTypeName]]
        names: Optional[List[NameModel2]]
        types: Optional[List[enum.DataStreamType]]
        search: Optional[List[SearchItem]]
        semantic_type_names: Optional[List[SemanticTypeName]]
        unit_names: Optional[List[UnitName]]

    """

    data_type_names: Optional[List[DataTypeName]] = Field(
        None,
        description="A filter on the list based on the key `data_type_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["number", "string"]],
    )
    names: Optional[List[NameModel2]] = Field(
        None,
        description="A filter on the list based on the  Data Stream key `name`. The filter is on the full name only. All strings in the array are treated as `OR`. Each string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["motor_temperature", "water_flow_rate"]],
    )
    types: Optional[List[enum.DataStreamType]] = Field(
        None,
        description="A filter on the list based on the Data Stream key `type`. The filter is on the full name only. All strings in the array are treated as `OR`.",
        examples=[["computed", "measurement"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter on the list based on the keys `title` (Display Name) or `name`. The search is case insensitive and will find partial matches as well. All strings in the array are treated as `OR`.",
        examples=[["motor", "water"]],
    )
    semantic_type_names: Optional[List[SemanticTypeName]] = Field(
        None,
        description="A filter on the list based on the key `semantic_type_name`. The filter is on the full name only. All strings in the array are treated as `OR`. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["sound_pressure", "volume"]],
    )
    unit_names: Optional[List[UnitName]] = Field(
        None,
        description="A filter on the list based on the key `unit_name`. The filter is on the full name only. All strings in the array are treated as `OR`. Each string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["kilogram", "litre_per_second"]],
    )


class DatastreamName(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=["gas_flow_rate"])


class BulkDataStreamDelete(DataModelBase):
    """
    BulkDataStreamDelete object.

    Parameters
    ----------
        datastream_names: List[DatastreamName]

    """

    datastream_names: List[DatastreamName] = Field(
        ...,
        description="Array of Data Stream key `name` to delete. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        min_length=1,
    )


class DatastreamNameModel(BaseModelRoot[StrictStr]):
    root: StrictStr


class DataStreamContextsList(DataModelBase):
    """
    DataStreamContextsList object.

    Parameters
    ----------
        datastream_names: Optional[List[DatastreamNameModel]]
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        writable: Optional[StrictBool]

    """

    datastream_names: Optional[List[DatastreamNameModel]] = Field(
        None,
        description="A filter on the list based on the Data Stream key `name`. The filter is on the full name only. All strings in the array are treated as `OR`. Each string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["motor_temperature", "water_flow_rate"]],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Streams associated with any Assets in the array. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:asset:bp_16", "krn:asset:bp_21"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Streams associated with any workloads in the array. The filter is on the full name only. All strings in the array are treated as `OR`. Each Workload name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:wlappv:cluster1/app1/1.2.0"]],
    )
    writable: Optional[StrictBool] = Field(
        None,
        description="A filter on the list showing only Data Streams that are writable or not. The filter is on the full name only. The value can be `true` or `false`.",
        examples=[True],
    )


class Context(BaseModelRoot[StrictStr]):
    root: StrictStr


class DataTagCreate(DataModelBase):
    """
    DataTagCreate object.

    Parameters
    ----------
        start_date: datetime
        end_date: datetime
        tag_name: StrictStr
        resource: KRN
        source: Optional[KRN]
        description: Optional[StrictStr]
        contexts: Optional[List[KRN]]

    """

    start_date: datetime = Field(
        ...,
        description="Start date for the Data Tag. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T18:22:18.582724Z"],
    )
    end_date: datetime = Field(
        ...,
        description="End date for the Data Tag. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )
    tag_name: StrictStr = Field(..., description="Tag name to categorize the Data Tag", examples=["Valve Change"])
    resource: KRN = Field(
        ..., description="The Asset that this Data Tag is related to.", examples=["krn:asset:well_01"]
    )
    source: Optional[KRN] = Field(
        None,
        description="The process that created this Data Tag. This can be a user or an automated process like a workload, application, etc.",
        examples=["krn:wlappv:cluster1/app1/1.2.0"],
    )
    description: Optional[StrictStr] = Field(
        None, description="Detailed description of the Data Tag.", examples=["A Valve was changed today."]
    )
    contexts: Optional[List[KRN]] = Field(
        None,
        description="A list of associated resources with this Data Tag. This can be a datastream, application or any other valid resource in the Kelvin Platform.",
        examples=[["krn:datastream:temperature", "krn:appversion:smart-pcp/2.0.0"]],
    )


class DataTagUpdate(DataModelBase):
    """
    DataTagUpdate object.

    Parameters
    ----------
        start_date: Optional[datetime]
        end_date: Optional[datetime]
        tag_name: Optional[StrictStr]
        resource: Optional[KRN]
        description: Optional[StrictStr]
        contexts: Optional[List[KRN]]

    """

    start_date: Optional[datetime] = Field(
        None,
        description="Start date for the Data Tag. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T18:22:18.582724Z"],
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for the Data Tag. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )
    tag_name: Optional[StrictStr] = Field(
        None, description="Tag name to categorize the Data Tag", examples=["Valve Change"]
    )
    resource: Optional[KRN] = Field(
        None, description="The Asset that this Data Tag is related to.", examples=["krn:asset:well_01"]
    )
    description: Optional[StrictStr] = Field(
        None, description="Detailed description of the Data Tag.", examples=["A Valve was changed today."]
    )
    contexts: Optional[List[KRN]] = Field(
        None,
        description="A list of associated resources with this Data Tag. This can be a datastream, application or any other valid resource in the Kelvin Platform.",
        examples=[["krn:datastream:temperature", "krn:appversion:smart-pcp/2.0.0"]],
    )


class TagName(BaseModelRoot[StrictStr]):
    root: StrictStr


class DataTagList(DataModelBase):
    """
    DataTagList object.

    Parameters
    ----------
        ids: Optional[List[UUID]]
        search: Optional[List[SearchItem]]
        tag_names: Optional[List[TagName]]
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        contexts: Optional[List[KRN]]
        start_date: Optional[datetime]
        end_date: Optional[datetime]

    """

    ids: Optional[List[UUID]] = Field(
        None,
        description="Search and filter on the list based on the key `id`. The filter is on the full UUID `id` only. All strings in the array are treated as `OR`.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "00080f9e-d086-452d-b41d-c8aa8fb27c92"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter on the list based on the key `tag_name`. The search is case insensitive and will find partial matches as well. All strings in the array are treated as `OR`.",
        examples=[["break", "change"]],
    )
    tag_names: Optional[List[TagName]] = Field(
        None,
        description="A filter on the list showing only Data Tags associated with one or more tags. The filter is on the full Data Tags `tag_name` only. All strings in the array are treated as `OR`.",
        examples=[["Breakdown", "Valve Change"]],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Tags associated with any Assets in the array. The filter is on the full KRN Asset name only. All strings in the array are treated as `OR`. Each Asset name must be in the KRN format.",
        examples=[["krn:asset:bp_16", "krn:asset:bp_21"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Tags created by a certain source. The filter is on the full `source` KRN name only. All strings in the array are treated as `OR`.",
        examples=[["krn:wlappv:cluster1/app1/1.2.0", "krn:user:richard.teo@kelvininc.com"]],
    )
    contexts: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Tags associated with any context resource. The filter is on the full `contexts` KRN only. All strings in the array are treated as `OR`.",
        examples=[["krn:datastream:temperature", "krn:appversion:smart-pcp/2.0.0"]],
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Earliest `end_date` time for the list of Data Tags. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T00:00:00.000000Z"],
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Most recent `start_date` time for the list of Data Tags. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-07T00:00:00.000000Z"],
    )


class TagCreate(DataModelBase):
    """
    TagCreate object.

    Parameters
    ----------
        name: StrictStr
        metadata: Optional[Dict[str, Any]]

    """

    name: StrictStr = Field(..., description="Case insensitive Tag name.", examples=["Valve Change"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Tag. The structure of the `metadata` object can have any key/value structure and will depend on the required properties of the Tag.",
    )


class TagUpdate(DataModelBase):
    """
    TagUpdate object.

    Parameters
    ----------
        metadata: Optional[Dict[str, Any]]

    """

    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Tag. The structure of the `metadata` object can have any key/value structure and will depend on the required properties of the Tag.",
    )


class FilesList(DataModelBase):
    """
    FilesList object.

    Parameters
    ----------
        file_names: Optional[List[StrictStr]]
        sources: Optional[List[StrictStr]]
        search: Optional[List[StrictStr]]

    """

    file_names: Optional[List[StrictStr]] = Field(
        None,
        description="Array of file names to filter. This filter only returns exact matches with the passed values.",
        examples=[["test.csv", "test.tar.gz"]],
    )
    sources: Optional[List[StrictStr]] = Field(
        None,
        description="Array of sources to filter. This filter only returns exact matches with the passed values. (Note that all sources are in the KRN format)",
        examples=[["krn:user:user1", "krn:user:user2"]],
    )
    search: Optional[List[StrictStr]] = Field(
        None,
        description="Search and filter based of file name. All values in array will be filtered as `OR`. The search is case insensitive and will find partial matches as well.",
        examples=[["test.csv", "test.tar.gz"]],
    )


class GuardrailCreate(GuardrailConfigWithResource):
    """
    GuardrailCreate object.

    Parameters
    ----------

    """


class GuardrailUpdate(GuardrailConfig):
    """
    GuardrailUpdate object.

    Parameters
    ----------

    """


class GuardrailsList(DataModelBase):
    """
    GuardrailsList object.

    Parameters
    ----------
        resources: Optional[List[KRN]]
        control_disabled: Optional[StrictBool]

    """

    resources: Optional[List[KRN]] = Field(
        None,
        description="Array of Asset/Data Stream pairs to filter the Guardrail list on server before returning. (example: `krn:ad:asset1/setpoint`).",
    )
    control_disabled: Optional[StrictBool] = Field(
        None, description="Filter current status indicating whether this Guardrail is active or disabled."
    )


class BulkGuardrailsCreate(DataModelBase):
    """
    BulkGuardrailsCreate object.

    Parameters
    ----------
        guardrails: Optional[List[type.GuardrailConfigWithResource]]

    """

    guardrails: Optional[List[type.GuardrailConfigWithResource]] = Field(
        None, description="An array of Guardrail configurations to create."
    )


class BulkGuardrailsDelete(DataModelBase):
    """
    BulkGuardrailsDelete object.

    Parameters
    ----------
        resources: Optional[List[KRN]]

    """

    resources: Optional[List[KRN]] = Field(
        None,
        description="An array of Asset/Data Stream pairs for deleting the associated Guardrail configurations. (example: `krn:ad:asset1/setpoint`).",
    )


class ClusterSettingAutoUpdate(DataModelBase):
    """
    ClusterSettingAutoUpdate object.

    Parameters
    ----------
        enabled: Optional[StrictBool]
        interval: Optional[StrictInt]

    """

    enabled: Optional[StrictBool] = Field(None, description="If the auto update is enabled.", examples=[True])
    interval: Optional[StrictInt] = Field(None, description="If the auto update is enabled.")


class ClusterSettingDeployOptions(DataModelBase):
    """
    ClusterSettingDeployOptions object.

    Parameters
    ----------
        instantly_apply: Optional[StrictBool]
        pre_download: Optional[StrictBool]

    """

    instantly_apply: Optional[StrictBool] = Field(
        None,
        description="Option if upgrades should be applied automatically and instantly as soon as they are available in the Cluster.",
        examples=[True],
    )
    pre_download: Optional[StrictBool] = Field(
        None,
        description="Option for pre-downloading Cluster Instance. Actual upgrade initiation requires manual action or having `instantly_apply` set to true.",
        examples=[True],
    )


class ClusterSettingForwardLogs(DataModelBase):
    """
    ClusterSettingForwardLogs object.

    Parameters
    ----------
        buffer_size: Optional[StrictInt]
        enabled: Optional[StrictBool]

    """

    buffer_size: Optional[StrictInt] = Field(
        5,
        description="Size in gigabytes of the log storage in the Instance Cluster when Cluster is offline. Any setting changes will delete all logs not yet transferred from the Cluster to Cloud.",
        examples=[10],
    )
    enabled: Optional[StrictBool] = Field(
        True,
        description="Enable offline storage in the Instance Cluster for log retention; transfers logs when Cluster is next online.",
        examples=[True],
    )


class ClusterSettingSync(DataModelBase):
    """
    ClusterSettingSync object.

    Parameters
    ----------
        interval: Optional[StrictInt]

    """

    interval: Optional[StrictInt] = Field(
        30,
        description="Frequency in minutes that the Instance Cluster checks for new changes to apply to Workloads or Applications (deploy, start, stop, etc.)",
        examples=[60],
    )


class ClusterSettingTelemetry(DataModelBase):
    """
    ClusterSettingTelemetry object.

    Parameters
    ----------
        buffer_size: Optional[StrictInt]
        enabled: Optional[StrictBool]
        node_alerts_enabled: Optional[StrictBool]

    """

    buffer_size: Optional[StrictInt] = Field(
        5,
        description="Size in gigabytes of telemetry data storage in the Cluster Instance when the Cluster is offline. Any setting changes will delete all logs not yet transferred from the Cluster to Cloud.",
        examples=[10],
    )
    enabled: Optional[StrictBool] = Field(
        True,
        description="Enable offline storage in the Cluster Instance for telemetry data retention; transfers data when the Cluster is next online.",
    )
    node_alerts_enabled: Optional[StrictBool] = Field(
        True, description="Enable or disable alerts for Node telemetry data.", examples=[True]
    )


class EdgeUi(DataModelBase):
    """
    EdgeUi object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge UI service.")


class EdgeCcm(DataModelBase):
    """
    EdgeCcm object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge CCM service.")


class EdgeK8s(DataModelBase):
    """
    EdgeK8s object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge K8S service.")


class EdgeInfo(DataModelBase):
    """
    EdgeInfo object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge Info service.")


class EdgeMqtt(DataModelBase):
    """
    EdgeMqtt object.

    Parameters
    ----------
        disabled: Optional[StrictBool]
        expose: Optional[StrictBool]
        anonymous: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge MQTT service.")
    expose: Optional[StrictBool] = Field(False, description="Expose the Edge MQTT service.")
    anonymous: Optional[StrictBool] = Field(False, description="Allow anonymous access to the Edge MQTT service.")


class EdgeNats(DataModelBase):
    """
    EdgeNats object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge NATS service.")


class EdgeSync(DataModelBase):
    """
    EdgeSync object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge Sync service.")


class EdgeLeaderApi(DataModelBase):
    """
    EdgeLeaderApi object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge Leader API service.")


class EdgeCustomActionManager(DataModelBase):
    """
    EdgeCustomActionManager object.

    Parameters
    ----------
        disabled: Optional[StrictBool]

    """

    disabled: Optional[StrictBool] = Field(False, description="Disable the Edge Custom Action Manager service.")


class ClusterSettingEdgeApps(DataModelBase):
    """
    ClusterSettingEdgeApps object.

    Parameters
    ----------
        edge_ui: Optional[EdgeUi]
        edge_ccm: Optional[EdgeCcm]
        edge_k8s: Optional[EdgeK8s]
        edge_info: Optional[EdgeInfo]
        edge_mqtt: Optional[EdgeMqtt]
        edge_nats: Optional[EdgeNats]
        edge_sync: Optional[EdgeSync]
        edge_leader_api: Optional[EdgeLeaderApi]
        edge_custom_action_manager: Optional[EdgeCustomActionManager]

    """

    edge_ui: Optional[EdgeUi] = None
    edge_ccm: Optional[EdgeCcm] = None
    edge_k8s: Optional[EdgeK8s] = None
    edge_info: Optional[EdgeInfo] = None
    edge_mqtt: Optional[EdgeMqtt] = None
    edge_nats: Optional[EdgeNats] = None
    edge_sync: Optional[EdgeSync] = None
    edge_leader_api: Optional[EdgeLeaderApi] = None
    edge_custom_action_manager: Optional[EdgeCustomActionManager] = None


class ClusterSetting(DataModelBase):
    """
    ClusterSetting object.

    Parameters
    ----------
        auto_update: Optional[ClusterSettingAutoUpdate]
        cluster_upgrade: Optional[ClusterSettingDeployOptions]
        forward_logs: Optional[ClusterSettingForwardLogs]
        sync: Optional[ClusterSettingSync]
        telemetry: Optional[ClusterSettingTelemetry]
        workload_deploy: Optional[ClusterSettingDeployOptions]
        edge_apps: Optional[ClusterSettingEdgeApps]

    """

    auto_update: Optional[ClusterSettingAutoUpdate] = None
    cluster_upgrade: Optional[ClusterSettingDeployOptions] = None
    forward_logs: Optional[ClusterSettingForwardLogs] = None
    sync: Optional[ClusterSettingSync] = None
    telemetry: Optional[ClusterSettingTelemetry] = None
    workload_deploy: Optional[ClusterSettingDeployOptions] = None
    edge_apps: Optional[ClusterSettingEdgeApps] = None


class InstanceSettingsKelvinClusterUpdate(DataModelBase):
    """
    InstanceSettingsKelvinClusterUpdate object.

    Parameters
    ----------
        payload: Optional[ClusterSetting]

    """

    payload: Optional[ClusterSetting] = None


class InstanceSettingsUpdate(DataModelBase):
    """
    InstanceSettingsUpdate object.

    Parameters
    ----------
        payload: Optional[Dict[str, Any]]

    """

    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The Instance Settings. The structure of this `payload` object depends on the type of Instance Setting being defined.",
    )


class OrchestrationClustersCreate(DataModelBase):
    """
    OrchestrationClustersCreate object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        type: Optional[enum.ClusterType]

    """

    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Cluster.", examples=["aws-cluster"]
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Cluster.", examples=["AWS Cluster"]
    )
    type: Optional[enum.ClusterType] = Field(None, description="Type of Cluster to deploy..")


class ClusterUpgrade(DataModelBase):
    """
    ClusterUpgrade object.

    Parameters
    ----------
        instantly_apply: Optional[StrictBool]
        pre_download: Optional[StrictBool]

    """

    instantly_apply: Optional[StrictBool] = Field(
        None,
        description="Setting to immediately apply upgrades to Workloads or Applications as soon as they are available in the Cluster.",
    )
    pre_download: Optional[StrictBool] = Field(
        None,
        description="Setting to immediately download new Workloads or Application upgrades to the Cluster; requires manual initiation or `instantly_apply` set to true to initiate upgrade.",
    )


class ClusterEdgeAPICredentials(DataModelBase):
    """
    ClusterEdgeAPICredentials object.

    Parameters
    ----------
        username: Optional[StrictStr]
        password: Optional[StrictStr]

    """

    username: Optional[StrictStr] = Field(None, description="Username for the Edge API.", examples=["username"])
    password: Optional[StrictStr] = Field(
        None,
        description="Password for the Edge API. At least one uppercase letter, one lowercase letter, and one number.",
        examples=["password"],
    )


class ClusterEdgeApps(DataModelBase):
    """
    ClusterEdgeApps object.

    Parameters
    ----------
        edge_ui: Optional[EdgeUi]
        edge_ccm: Optional[EdgeCcm]
        edge_k8s: Optional[EdgeK8s]
        edge_info: Optional[EdgeInfo]
        edge_mqtt: Optional[EdgeMqtt]
        edge_nats: Optional[EdgeNats]
        edge_sync: Optional[EdgeSync]
        edge_leader_api: Optional[EdgeLeaderApi]
        edge_custom_action_manager: Optional[EdgeCustomActionManager]

    """

    edge_ui: Optional[EdgeUi] = None
    edge_ccm: Optional[EdgeCcm] = None
    edge_k8s: Optional[EdgeK8s] = None
    edge_info: Optional[EdgeInfo] = None
    edge_mqtt: Optional[EdgeMqtt] = None
    edge_nats: Optional[EdgeNats] = None
    edge_sync: Optional[EdgeSync] = None
    edge_leader_api: Optional[EdgeLeaderApi] = None
    edge_custom_action_manager: Optional[EdgeCustomActionManager] = None


class ClusterEdgeOptions(DataModelBase):
    """
    ClusterEdgeOptions object.

    Parameters
    ----------
        image_pull_policy: Optional[StrictStr]

    """

    image_pull_policy: Optional[StrictStr] = Field(
        None,
        description="Image pull policy to be used when deploying workloads. Options are `Always`, and `IfNotPresent`. Default: `IfNotPresent`",
        examples=["IfNotPresent"],
    )


class OrchestrationClustersUpdate(DataModelBase):
    """
    OrchestrationClustersUpdate object.

    Parameters
    ----------
        forward_logs_buffer_size: Optional[StrictInt]
        forward_logs_enabled: Optional[StrictBool]
        manifests_scrape_enabled: Optional[StrictBool]
        manifests_scrape_interval: Optional[StrictInt]
        ready: Optional[StrictBool]
        sync_scrape_interval: Optional[StrictInt]
        telemetry_buffer_size: Optional[StrictInt]
        telemetry_enabled: Optional[StrictBool]
        telemetry_alerts_enabled: Optional[StrictBool]
        title: Optional[StrictStr]
        upgrade: Optional[ClusterUpgrade]
        api_credentials: Optional[ClusterEdgeAPICredentials]
        edge_apps: Optional[ClusterEdgeApps]
        edge_options: Optional[ClusterEdgeOptions]

    """

    forward_logs_buffer_size: Optional[StrictInt] = Field(
        5,
        description="Size in gigabytes of the log storage in the Cluster when Cluster is offline. Any setting changes will delete all logs not yet transferred from the Cluster to Cloud.",
        examples=[10],
    )
    forward_logs_enabled: Optional[StrictBool] = Field(
        True,
        description="Enable offline storage in the Cluster for log retention; transfers logs when the Cluster is next online.",
    )
    manifests_scrape_enabled: Optional[StrictBool] = Field(
        True, description="Enable auto update Kelvin Software running on the Cluster."
    )
    manifests_scrape_interval: Optional[StrictInt] = Field(
        86400,
        description="Frequency in seconds for checking updates in the Cloud for Kelvin Software running on the Cluster.",
        examples=[3600],
    )
    ready: Optional[StrictBool] = Field(None, description="Setting to inform Kelvin UI if the Cluster is ready.")
    sync_scrape_interval: Optional[StrictInt] = Field(
        30,
        description="Frequency in seconds that the Cluster checks for new changes to apply in Workloads or Applications (deploy, start, stop, etc.)",
        examples=[3600],
    )
    telemetry_buffer_size: Optional[StrictInt] = Field(
        5,
        description="Size in gigabytes of telemetry data storage in the Cluster when the Cluster is offline. Any setting changes will delete all logs not yet transferred from the Cluster to Cloud.",
        examples=[10],
    )
    telemetry_enabled: Optional[StrictBool] = Field(
        True,
        description="Enable offline storage in the Cluster for telemetry data retention; transfers data when the Cluster is next online.",
    )
    telemetry_alerts_enabled: Optional[StrictBool] = Field(
        True, description="Enables or disables the alerts on the cluster nodes.", examples=[False]
    )
    title: Optional[StrictStr] = Field(
        None, description="New display name (`title`) for Cluster.", examples=["AWS Cluster 01"]
    )
    upgrade: Optional[ClusterUpgrade] = None
    api_credentials: Optional[ClusterEdgeAPICredentials] = None
    edge_apps: Optional[ClusterEdgeApps] = None
    edge_options: Optional[ClusterEdgeOptions] = None


class PropertyCreate(DataModelBase):
    """
    PropertyCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        primitive_type: enum.PropertyType

    """

    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` for the Property. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["water-line-pressure"],
    )
    title: StrictStr = Field(
        ...,
        description="Unique `title` for the Property. Unlike Titles in Assets, Data Streams and other areas of the Kelvin Platform, Titles in Property must be unique and repeated title will cause the request to fail.",
        examples=["Water Line Pressure"],
    )
    primitive_type: enum.PropertyType = Field(..., description="Data type for the Property `name`.")


class PropertyUniqueValuesGet(DataModelBase):
    """
    PropertyUniqueValuesGet object.

    Parameters
    ----------
        property_names: Optional[List[StrictStr]]
        resource_types: Optional[List[StrictStr]]
        primitive_types: Optional[List[enum.PropertyType]]

    """

    property_names: Optional[List[StrictStr]] = Field(
        None,
        description="List of property `name` for which the values are to be fetched. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    resource_types: Optional[List[StrictStr]] = Field(
        None, description="List of resource types to filter the list of Property values returned."
    )
    primitive_types: Optional[List[enum.PropertyType]] = Field(
        None, description="List of primitive types to filter the list of Property values returned."
    )


class PropertyValuesUpdate(DataModelBase):
    """
    PropertyValuesUpdate object.

    Parameters
    ----------
        resource_values: Optional[Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]]

    """

    resource_values: Optional[
        Dict[
            str,
            Union[
                StrictInt,
                StrictFloat,
                StrictStr,
                StrictBool,
                List[StrictInt],
                List[StrictFloat],
                List[StrictStr],
                List[StrictBool],
            ],
        ]
    ] = Field(
        None,
        description="List of resources and their corresponding updated values for the defined `property_name`.",
        examples=[{"krn:asset:asset1": 1, "krn:asset:asset2": 2}],
    )


class PropertyValuesDelete(DataModelBase):
    """
    PropertyValuesDelete object.

    Parameters
    ----------
        resources: Optional[List[StrictStr]]

    """

    resources: Optional[List[StrictStr]] = Field(
        None, description="List of resources where the associated `property_name` values will be deleted."
    )


class RangeGetPropertyValues(DataModelBase):
    """
    RangeGetPropertyValues object.

    Parameters
    ----------
        resources: Optional[List[StrictStr]]
        start_date: datetime
        end_date: datetime

    """

    resources: Optional[List[StrictStr]] = Field(
        None, description="List of resources for which to fetch `property_name`."
    )
    start_date: datetime = Field(
        ...,
        description="UTC time for when to begin the time range, formatted in RFC 3339.",
        examples=["2025-01-29T12:00:00Z"],
    )
    end_date: datetime = Field(
        ...,
        description="UTC time for when to end the time range, formatted in RFC 3339.",
        examples=["2025-01-29T12:00:00Z"],
    )


class ResourceName(BaseModelRoot[StrictStr]):
    root: StrictStr


class RecommendationClusteringGet(DataModelBase):
    """
    RecommendationClusteringGet object.

    Parameters
    ----------
        end_date: datetime
        resource_names: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        trace_ids: Optional[List[TraceId]]
        start_date: datetime
        states: Optional[List[enum.RecommendationState]]
        time_bucket: StrictStr
        types: Optional[List[Type]]

    """

    end_date: datetime = Field(
        ...,
        description="Most recent (end) creation time for counting the number of Recommendations. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    resource_names: Optional[List[KRN]] = Field(
        None,
        description="Filter Assets (`resources`) linked to Recommendations for inclusion in the count. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:asset:bp_02", "krn:asset:bp_16"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter to only count Recommendations from certain `source`. The filter is on the full name only. All strings in the array are treated as `OR`. Each KRN name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:app:motor-speed-control"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Custom Actions associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )
    start_date: datetime = Field(
        ...,
        description="Earliest (start) creation time for counting the  number of Recommendations. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    states: Optional[List[enum.RecommendationState]] = Field(
        None,
        description="A filter to only count Recommendations associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["accepted", "applied"]],
    )
    time_bucket: StrictStr = Field(
        ...,
        description='Defines the time range to use to count the number of Recommendations. Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".',
        examples=["5m"],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="A filter to only count Recommendations associated with one or more `types`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["Decrease speed", "increase_speed"]],
    )


class RecommendationCreate(RecommendationBase):
    """
    RecommendationCreate object.

    Parameters
    ----------
        actions: Optional[type.RecommendationActionsCreate]
        state: Optional[enum.RecommendationStateCreate]

    """

    actions: Optional[type.RecommendationActionsCreate] = None
    state: Optional[enum.RecommendationStateCreate] = Field(None, description="Current `state` of the Recommendation.")


class RecommendationLastGet(DataModelBase):
    """
    RecommendationLastGet object.

    Parameters
    ----------
        resources: List[KRN]
        sources: Optional[List[KRN]]
        states: Optional[List[enum.RecommendationState]]
        trace_ids: Optional[List[TraceId]]
        types: Optional[List[Type]]

    """

    resources: List[KRN] = Field(
        ...,
        description="A filter on the list to show Last Recommendation for requested Assets only. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:asset:bp_02", "krn:asset:bp_16"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Data Streams associated with any workloads in the array. The filter is on the full name only. All strings in the array are treated as `OR`. Each Workload name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:app:motor-speed-control"]],
    )
    states: Optional[List[enum.RecommendationState]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["accepted", "applied"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more `types`. The filter is on the full `types` name only. All strings in the array are treated as `OR`.",
        examples=[["Decrease speed", "increase_speed"]],
    )


class RecommendationsList(DataModelBase):
    """
    RecommendationsList object.

    Parameters
    ----------
        ids: Optional[List[UUID]]
        resources: Optional[List[KRN]]
        sources: Optional[List[KRN]]
        states: Optional[List[enum.RecommendationState]]
        trace_ids: Optional[List[TraceId]]
        types: Optional[List[Type]]

    """

    ids: Optional[List[UUID]] = Field(
        None,
        description="Search and filter on the list based on the key `id`. The filter is on the full UUID `id` only. All strings in the array are treated as `OR`.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "00080f9e-d086-452d-b41d-c8aa8fb27c92"]],
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with any Assets in the array. The filter is on the full KRN Asset name only. All strings in the array are treated as `OR`. Each Asset name must be in the KRN format.",
        examples=[["krn:asset:bp_16", "krn:asset:bp_21"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Recommendations created by a certain source. The filter is on the full `source` KRN name only. All strings in the array are treated as `OR`.",
        examples=[["krn:wlappv:cluster1/app1/1.2.0", "krn:user:richard.teo@kelvininc.com"]],
    )
    states: Optional[List[enum.RecommendationState]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["accepted", "applied"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more Recommendation Types. The filter is on the full Recommendation Type `name` only. All strings in the array are treated as `OR`.",
        examples=[["Decrease speed", "increase_speed"]],
    )


class RecommendationRangeGet(DataModelBase):
    """
    RecommendationRangeGet object.

    Parameters
    ----------
        end_date: datetime
        resources: List[KRN]
        sources: Optional[List[KRN]]
        trace_ids: Optional[List[TraceId]]
        start_date: datetime
        states: Optional[List[enum.RecommendationState]]
        types: Optional[List[Type]]

    """

    end_date: datetime = Field(
        ...,
        description="Most recent (end) creation time for the list of Recommendations. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    resources: List[KRN] = Field(
        ...,
        description="A filter on the list to show Range of Recommendations for requested Assets only. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:asset:bp_02", "krn:asset:bp_16"]],
    )
    sources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only Recommendations coming from certain `source`. The filter is on the full name only. All strings in the array are treated as `OR`. Each Workload name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:app:motor-speed-control"]],
    )
    trace_ids: Optional[List[TraceId]] = Field(
        None,
        description="A filter on the list showing only Custom Actions associated with one or more Trace IDs.",
        examples=[["trace id change 123"]],
    )
    start_date: datetime = Field(
        ...,
        description="Earliest (start) creation time for the list of Recommendations. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    states: Optional[List[enum.RecommendationState]] = Field(
        None,
        description="A filter on the list showing only Range of Recommendations associated with one or more `states`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["accepted", "applied"]],
    )
    types: Optional[List[Type]] = Field(
        None,
        description="A filter on the list showing only Recommendations associated with one or more `types`. The filter is on the full `state` name only. All strings in the array are treated as `OR`.",
        examples=[["Decrease speed", "increase_speed"]],
    )


class RecommendationTypeCreate(DataModelBase):
    """
    RecommendationTypeCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        metadata: Optional[Dict[str, Any]]

    """

    name: StrictStr = Field(
        ..., description="Unique identifier `name` for the Recommendation Type.", examples=["Decrease_speed"]
    )
    title: StrictStr = Field(
        ..., description="Unique identifier `title` for the Recommendation Type.", examples=["Decrease speed"]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Recommendation Type. The structure of the `metadata` object can have any key/value structure.",
    )


class RecommendationTypeUpdate(DataModelBase):
    """
    RecommendationTypeUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]

    """

    title: Optional[StrictStr] = Field(None, examples=["Decrease Speed"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Recommendation Type. The structure of the `metadata` object can have any key/value structure.",
    )


class RecommendationAcceptUpdate(DataModelBase):
    """
    RecommendationAcceptUpdate object.

    Parameters
    ----------
        confidence: Optional[StrictInt]
        message: Optional[StrictStr]

    """

    confidence: Optional[StrictInt] = Field(
        None,
        description="Confidence level of the decision to accept the Recommendation. This is usually, but not mandatory, related to any machine learning model confidence results.",
        examples=[7],
    )
    message: Optional[StrictStr] = Field(
        None,
        description="Contains a message with any descriptions useful to be associated with the `accepted` state.",
        examples=["Recommendation is accurate based on the current performance."],
    )


class RecommendationRejectUpdate(DataModelBase):
    """
    RecommendationRejectUpdate object.

    Parameters
    ----------
        confidence: Optional[StrictInt]
        message: Optional[StrictStr]

    """

    confidence: Optional[StrictInt] = Field(
        None,
        description="Confidence level of the decision to reject the Recommendation. This is usually, but not mandatory, related to any machine learning model confidence results.",
        examples=[7],
    )
    message: Optional[StrictStr] = Field(
        None,
        description="Contains a message with any descriptions useful to be associated with the `reject` state.",
        examples=["Recommendation is not accurate based on the current performance."],
    )


class SecretCreate(DataModelBase):
    """
    SecretCreate object.

    Parameters
    ----------
        name: StrictStr
        value: StrictStr

    """

    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` for the Secret. The string can only contain lowercase alphanumeric characters and `-` characters.",
        examples=["my-secret-password"],
    )
    value: StrictStr = Field(
        ...,
        description="The actual secret. Once this is set you can not change or see it from Kelvin API. Retrieval of the value can only be done through an App.",
        examples=["Nh9Noq%QWNaJim%uAe9r"],
    )


class SecretUpdate(DataModelBase):
    """
    SecretUpdate object.

    Parameters
    ----------
        value: Optional[StrictStr]

    """

    value: Optional[StrictStr] = Field(
        None,
        description="The actual secret. Once this is set you can not change or see it from Kelvin API. Retrieval of the value can only be done through an App.",
        examples=["Nh9Noq%QWNaJim%uAe9r"],
    )


class ThreadCreate(DataModelBase):
    """
    ThreadCreate object.

    Parameters
    ----------
        body: StrictStr
        file: Optional[bytes]

    """

    body: StrictStr = Field(..., description="requests.ThreadCreate schema")
    file: Optional[bytes] = Field(None, description="Attachment")


class ThreadReplyCreate(DataModelBase):
    """
    ThreadReplyCreate object.

    Parameters
    ----------
        body: StrictStr
        file: Optional[bytes]

    """

    body: StrictStr = Field(..., description="requests.ThreadReplyCreate schema")
    file: Optional[bytes] = Field(None, description="Attachment")


class ThreadReplyUpdate(DataModelBase):
    """
    ThreadReplyUpdate object.

    Parameters
    ----------
        body: StrictStr
        file: Optional[bytes]

    """

    body: StrictStr = Field(..., description="requests.ThreadReplyUpdate schema")
    file: Optional[bytes] = Field(None, description="Attachment")


class ThreadUpdate(DataModelBase):
    """
    ThreadUpdate object.

    Parameters
    ----------
        body: StrictStr
        file: Optional[bytes]

    """

    body: StrictStr = Field(..., description="requests.ThreadUpdate schema")
    file: Optional[bytes] = Field(None, description="Attachment")


class TimeseriesCreate(DataModelBase):
    """
    TimeseriesCreate object.

    Parameters
    ----------
        data: List[type.KelvinMessage]

    """

    data: List[type.KelvinMessage] = Field(..., description="Array of new time series data objects to create.")


class Selector(DataModelBase):
    """
    Selector object.

    Parameters
    ----------
        fields: Optional[List[StrictStr]]
        resource: KRN

    """

    fields: Optional[List[StrictStr]] = Field(
        None,
        description="A filter on the list based on the `field` element names. Blank array will return all data field element names and associated values.",
    )
    resource: KRN = Field(
        ...,
        description="Specifies the resource (Asset / Data Stream pair) from which field/values are returned.",
        examples=["krn:ad:asset1/data_stream1"],
    )


class TimeseriesLastGet(DataModelBase):
    """
    TimeseriesLastGet object.

    Parameters
    ----------
        selectors: Optional[List[Selector]]

    """

    selectors: Optional[List[Selector]] = Field(
        None,
        description="Array specifying resources and their optional field element names to filter the returned list.",
    )


class ResourceItem(BaseModelRoot[StrictStr]):
    root: StrictStr


class SourceItem(BaseModelRoot[StrictStr]):
    root: StrictStr


class TimeseriesList(DataModelBase):
    """
    TimeseriesList object.

    Parameters
    ----------
        resource: Optional[List[KRN]]
        source: Optional[List[KRN]]

    """

    resource: Optional[List[KRN]] = Field(
        None,
        description="Only return data from the Asset / DataStream pairs specified. Blank array will return all pairs. Resources are written in the krn format.",
        examples=[["krn:ad:asset1/data_stream1", "krn:ad:asset1/data_stream2"]],
    )
    source: Optional[List[KRN]] = Field(
        None,
        description="Only return data from the user and/or workloads specified. Blank array will return from all sources. Sources are written in the krn format.",
        examples=[
            ["krn:user:person@example.com", "krn:wl:my-node/temp-adjuster-1", "krn:wlappv:my-node/pvc-r312:pvc/1.0.0"]
        ],
    )


class TimeseriesRangeGet(DataModelBase):
    """
    TimeseriesRangeGet object.

    Parameters
    ----------
        agg: Optional[enum.TimeseriesAgg]
        end_time: datetime
        fill: Optional[StrictStr]
        group_by_selector: Optional[StrictBool]
        order: Optional[enum.TimeseriesOrder]
        selectors: List[Selector]
        start_time: datetime
        time_bucket: Optional[StrictStr]
        time_shift: Optional[StrictStr]

    """

    agg: Optional[enum.TimeseriesAgg] = enum.TimeseriesAgg.none
    end_time: datetime = Field(
        ...,
        description="UTC time for the latest time in the Time Series, formatted in RFC 3339.",
        examples=["2023-06-01T12:00:00Z"],
    )
    fill: Optional[StrictStr] = Field(
        "none",
        description="""How to fill the values when there is no data. Valid options are:
  - `none`: Doesn't fill empty values
  - `null`: Fills empty values with a null value
  - `linear`: Fills using [linear interpolation](https://en.wikipedia.org/wiki/Linear_interpolation)
  - `previous`: Fills using the previous non-null value
  - `<value>`: Provide a value to be used to fill""",
        examples=["25"],
    )
    group_by_selector: Optional[StrictBool] = Field(
        True,
        description="If true, results will be separated per `selector` element `resource` (Asset / Data Stream pair).",
        examples=[True],
    )
    order: Optional[enum.TimeseriesOrder] = enum.TimeseriesOrder.ASC
    selectors: List[Selector] = Field(
        ...,
        description="An array of `resources` and corresponding data `field` element name to filter on the list and optional `agg` calculations.",
    )
    start_time: datetime = Field(
        ...,
        description="UTC time for the earliest time in the Time Series, formatted in RFC 3339.",
        examples=["2023-06-01T12:00:00Z"],
    )
    time_bucket: Optional[StrictStr] = Field(
        None,
        description='Defines the time range to use to aggregate the data values when using the `agg` key. Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".',
        examples=["5m"],
    )
    time_shift: Optional[StrictStr] = Field(
        None,
        description='Shift initial starting point of time buckets from the standard epoch for `time_bucket`. Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".',
        examples=["1h"],
    )


class TimeseriesRangeDownload(TimeseriesRangeGet):
    """
    TimeseriesRangeDownload object.

    Parameters
    ----------

    """


class UserSettingsUpdate(DataModelBase):
    """
    UserSettingsUpdate object.

    Parameters
    ----------
        payload: Optional[Dict[str, Any]]

    """

    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The new payload for the User Setting. The structure of this `payload` object depends on the type of User Setting being updated.",
    )


class SharedSettingsUpdate(DataModelBase):
    """
    SharedSettingsUpdate object.

    Parameters
    ----------
        payload: Optional[Dict[str, Any]]

    """

    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The new payload for the Shared Setting. The structure of this `payload` object depends on the type of Shared Setting being updated.",
    )


class RoleName(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., description="The name of the role.", examples=["my_role"])


class GroupCreate(DataModelBase):
    """
    GroupCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        description: Optional[StrictStr]
        role_names: Optional[List[RoleName]]

    """

    name: StrictStr = Field(..., description="The name of the group.", examples=["my_group"])
    title: StrictStr = Field(..., description="The title of the group.", examples=["My Group"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the group.", examples=["This is my group"]
    )
    role_names: Optional[List[RoleName]] = None


class GroupUpdate(DataModelBase):
    """
    GroupUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        role_names: Optional[List[RoleName]]

    """

    title: Optional[StrictStr] = Field(None, description="The title of the group.", examples=["My Group"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the group.", examples=["This is my group"]
    )
    role_names: Optional[List[RoleName]] = None


class GroupName(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., description="The name of the Group.", examples=["my_group"])


class RoleCreate(DataModelBase):
    """
    RoleCreate object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        description: Optional[StrictStr]
        group_names: Optional[List[GroupName]]

    """

    name: StrictStr = Field(..., description="The name of the Role.", examples=["my_role"])
    title: StrictStr = Field(..., description="The title of the Role.", examples=["My Role"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Role.", examples=["This is my role"]
    )
    group_names: Optional[List[GroupName]] = None


class RoleUpdate(DataModelBase):
    """
    RoleUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        group_names: Optional[List[GroupName]]

    """

    title: Optional[StrictStr] = Field(None, description="The title of the Role.", examples=["My Role"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Role.", examples=["This is my role"]
    )
    group_names: Optional[List[GroupName]] = None


class Rule(DataModelBase):
    """
    Rule object.

    Parameters
    ----------
        actions: List[enum.RolePolicyAction]
        condition: Optional[type.RolePolicyCondition]

    """

    actions: List[enum.RolePolicyAction]
    condition: Optional[type.RolePolicyCondition] = None


class RolePolicyCreate(DataModelBase):
    """
    RolePolicyCreate object.

    Parameters
    ----------
        name: StrictStr
        resource_type: enum.ResourceType
        title: StrictStr
        description: Optional[StrictStr]
        rule: Rule

    """

    name: StrictStr = Field(..., description="The name of the Policy.", examples=["my_policy"])
    resource_type: enum.ResourceType = Field(
        ..., description="The resource_type to which the rule applies.", examples=["asset"]
    )
    title: StrictStr = Field(..., description="The title of the Policy.", examples=["My Policy"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Policy.", examples=["This is my policy"]
    )
    rule: Rule


class RolePolicyUpdate(DataModelBase):
    """
    RolePolicyUpdate object.

    Parameters
    ----------
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        rule: Optional[Rule]

    """

    title: Optional[StrictStr] = Field(None, description="The title of the Policy.", examples=["My Policy"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Policy.", examples=["This is my policy"]
    )
    rule: Optional[Rule] = None


class LegacyAppCreate(DataModelBase):
    """
    LegacyAppCreate object.

    Parameters
    ----------
        payload: Optional[Dict[str, Any]]

    """

    payload: Optional[Dict[str, Any]] = None


class LegacyAppUpdate(DataModelBase):
    """
    LegacyAppUpdate object.

    Parameters
    ----------
        description: Optional[StrictStr]
        title: Optional[StrictStr]

    """

    description: Optional[StrictStr] = Field(
        None,
        description="New description of the App in the App Registry.",
        examples=[
            """This application controls the speed of the beam pump motor in order to increase production for this type of artificial lift well. It uses values available from the control system such as Downhole Pressure, Motor Speed, Motor Torque and Choke position.
"""
        ],
    )
    title: Optional[StrictStr] = Field(
        None, description="New display name (`title`) of the App in the App Registry.", examples=["Motor Speed Control"]
    )


class BridgeDeploy(DataModelBase):
    """
    BridgeDeploy object.

    Parameters
    ----------
        app_version: Optional[StrictStr]
        cluster_name: StrictStr
        node_name: Optional[StrictStr]
        name: StrictStr
        payload: type.AppYaml
        title: Optional[StrictStr]
        app_name: StrictStr

    """

    app_version: Optional[StrictStr] = None
    cluster_name: StrictStr = Field(
        ...,
        description="Unique identifier `name` of the Cluster. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["docs-demo-cluster-k3s"],
    )
    node_name: Optional[StrictStr] = Field(
        None,
        description="Target Node Name for Workload deployment. If not provided, the Cluster will select the Node.",
        examples=["my-node"],
    )
    name: StrictStr = Field(
        ...,
        description="Unique identifier `name` of the Bridge (Connection). The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-plc-opcua-connection"],
    )
    payload: type.AppYaml = Field(
        ...,
        description="Dictionary with keys for configuration, language, logging level, metrics mapping, protocol, and system packages. Each key represents specific settings and parameters for the Bridge (Connection).",
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Bridge (Connection).", examples=["Motor PLC OPCUA Connection"]
    )
    app_name: StrictStr = Field(
        ...,
        description="Unique identifier `name` of the App. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["test-app"],
    )


class ParametersAppVersionUpdate(DataModelBase):
    """
    ParametersAppVersionUpdate object.

    Parameters
    ----------
        source: Optional[KRN]
        resource_parameters: List[type.ResourceParameters]

    """

    source: Optional[KRN] = Field(
        None,
        description="The User or Service that initiates the bulk updates. Only Service Accounts can write to this parameter.",
    )
    resource_parameters: List[type.ResourceParameters] = Field(
        ..., description="Array of parameters to update for an Asset."
    )


class AppName(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=["motor-speed-control"])


class NameModel3(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., examples=["gas_flow_rate_max_threshold"])


class ParametersDefinitionsList(DataModelBase):
    """
    ParametersDefinitionsList object.

    Parameters
    ----------
        app_names: Optional[List[AppName]]
        names: Optional[List[NameModel3]]
        primitive_types: Optional[List[enum.ParameterType]]
        search: Optional[List[SearchItem]]

    """

    app_names: Optional[List[AppName]] = Field(
        None,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    names: Optional[List[NameModel3]] = Field(None, description="Unique identifier name for this Parameter.")
    primitive_types: Optional[List[enum.ParameterType]] = Field(
        None,
        description="Filter on the list based on the Primitive data type key `primitive_type` of the Parameter.",
        examples=[["number", "boolean"]],
    )
    search: Optional[List[SearchItem]] = Field(
        None,
        description="Search and filter on the list based on the keys `parameter_name`. The search is case insensitive and will find partial matches as well. All strings in the array are treated as `OR`.",
        examples=[["motor", "water"]],
    )


class ParameterAppVersion(DataModelBase):
    """
    ParameterAppVersion object.

    Parameters
    ----------
        name: StrictStr
        version: Optional[StrictStr]

    """

    name: StrictStr = Field(
        ...,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-control"],
    )
    version: Optional[StrictStr] = Field(
        None,
        description="A filter on the list based on the key `app_version`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["1.2.0"],
    )


class ParameterName(BaseModelRoot[StrictStr]):
    root: StrictStr


class ResourceParametersList(DataModelBase):
    """
    ResourceParametersList object.

    Parameters
    ----------
        apps: Optional[List[ParameterAppVersion]]
        resources: Optional[List[KRN]]
        parameter_names: Optional[List[ParameterName]]
        start_date: Optional[datetime]
        end_date: Optional[datetime]

    """

    apps: Optional[List[ParameterAppVersion]] = Field(
        None,
        description="A filter on the list for Apps and its Versions. Multiple Apps and Versions can be given. All App Versions in the array are treated as `OR`.",
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only current Parameter values associated with any Assets in the array. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["krn:asset:bp_16", "krn:asset:bp_21"]],
    )
    parameter_names: Optional[List[ParameterName]] = Field(
        None,
        description="A filter on the list for Parameters. The filter is on the full name only. All strings in the array are treated as `OR`. Each Parameter name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=[["motor-speed-control", "gas_flow_rate_max_threshold"]],
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Earliest `created` time for the list of Parameters. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-06T00:00:00.000000Z"],
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Most recent `created` time for the list of Parameters. Time is based on UTC timezone, formatted in RFC 3339.",
        examples=["2024-02-07T00:00:00.000000Z"],
    )


class Parameter(BaseModelRoot[StrictStr]):
    root: StrictStr


class AppParameterModel(DataModelBase):
    """
    AppParameterModel object.

    Parameters
    ----------
        app_name: StrictStr
        parameters: Optional[List[Parameter]]

    """

    app_name: StrictStr = Field(
        ...,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-control"],
    )
    parameters: Optional[List[Parameter]] = Field(
        None,
        description="Array of Parameter `names` to fetch associated values for Apps.",
        examples=[["gas_flow_rate_min_threshold", "gas_flow_rate_max_threshold"]],
    )


class ParametersValuesGet(DataModelBase):
    """
    ParametersValuesGet object.

    Parameters
    ----------
        app_parameters: Optional[List[AppParameterModel]]
        primitive_types: Optional[List[enum.ParameterType]]

    """

    app_parameters: Optional[List[AppParameterModel]] = Field(
        None,
        description="Filter on the list based on the key `app_name` and wanted Parameter `name` per App. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    primitive_types: Optional[List[enum.ParameterType]] = Field(
        None,
        description="Filter on the list based on the Parameter data type key `primitive_type` of the Parameter.",
        examples=[["number", "boolean"]],
    )


class LegacyWorkloadDeploy(DataModelBase):
    """
    LegacyWorkloadDeploy object.

    Parameters
    ----------
        acp_name: Optional[StrictStr]
        app_name: StrictStr
        app_version: Optional[StrictStr]
        cluster_name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        instantly_apply: Optional[StrictBool]
        name: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        staged: Optional[StrictBool]
        source: Optional[KRN]
        title: Optional[StrictStr]

    """

    acp_name: Optional[StrictStr] = Field(
        None,
        description="[`Deprecated`] Target Cluster Name (`acp_name`) for Workload deployment. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["docs-demo-cluster-k3s"],
    )
    app_name: StrictStr = Field(
        ...,
        description="App Name from App Registry to use for Workload deployment. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["motor-speed-control"],
    )
    app_version: Optional[StrictStr] = Field(None, description="Version of the App to use.", examples=["1.2.0"])
    cluster_name: Optional[StrictStr] = Field(
        None,
        description="Target Cluster Name for Workload deployment. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters. If set, it will override acp_name",
        examples=["docs-demo-cluster-k3s"],
    )
    node_name: Optional[StrictStr] = Field(
        None,
        description="Target Node Name for Workload deployment. If not provided, the Cluster will select the Node.",
        examples=["my-node"],
    )
    instantly_apply: Optional[StrictBool] = Field(
        None,
        description="If true, applies deploy/upgrade immediately. If false, user will need to send an additional API request `/workloads/{workload_name}/apply` to initate the deploy/upgrade.",
        examples=[True],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Workload.", examples=["motor-speed-control-ubdhwnshdy67"]
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="All parameters associated with the Kelvin App like Inputs, Outputs, Info, Spec Version and System.",
    )
    staged: Optional[StrictBool] = Field(
        None,
        description="If true, deploy process is handled by Kelvin and all Workloads wil be downloaded to Edge System before deploy. If false, deploy process is handled by Kubernetes through default settings.",
        examples=[True],
    )
    source: Optional[KRN] = Field(
        None,
        description="Who or which process initiated the Workload deploy.",
        examples=["krn:user:richard.teo@kelvininc.com"],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Workload.", examples=["Motor Speed Control"]
    )


class LegacyWorkloadApply(DataModelBase):
    """
    LegacyWorkloadApply object.

    Parameters
    ----------
        workload_names: Optional[List[StrictStr]]

    """

    workload_names: Optional[List[StrictStr]] = Field(
        None, description="List of staged workload names that will be immediately applied."
    )


class LegacyWorkloadConfigurationUpdate(DataModelBase):
    """
    LegacyWorkloadConfigurationUpdate object.

    Parameters
    ----------
        configuration: Optional[Dict[str, Any]]

    """

    configuration: Optional[Dict[str, Any]] = None
