from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import EmailStr, Field, RootModel, StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.api.client.base_model import BaseModelRoot
from kelvin.api.client.data_model import DataModelBase, PaginatorDataModel
from kelvin.krn import KRN

from . import enum, type
from .pagination import PaginationCursor, PaginationLimits
from .type import (
    App,
    AppParameter,
    AppResource,
    AppShort,
    AppsResourceContext,
    AppVersion,
    AppVersionHistoricParameter,
    AppVersionParameter,
    Asset,
    AssetStatus,
    AssetType,
    Bridge,
    Created,
    CustomAction,
    CustomActionType,
    DataQuality,
    DataStreamDataType,
    DataStreamSemanticType,
    DataTag,
    FileStorage,
    GuardrailModel,
    InstanceAuditLogItem,
    InstanceSettings,
    LegacyApp,
    LegacyAppVersion,
    LegacyWorkload,
    OrchestrationCluster,
    ParameterSchedule,
    PropertyDefinition,
    PropertyValueHistory,
    Recommendation,
    RecommendationBase,
    RecommendationType,
    SharedSetting,
    Tag,
    Thread,
    TimeseriesData,
    Unit,
    Updated,
    UserSetting,
    Workload,
    WorkloadSummary,
)


class AppVersionCreate(AppVersion):
    """
    AppVersionCreate object.

    Parameters
    ----------

    """


class AppVersionGet(AppVersion):
    """
    AppVersionGet object.

    Parameters
    ----------

    """


class AppVersionPatch(AppVersion):
    """
    AppVersionPatch object.

    Parameters
    ----------

    """


class AppVersionUpdate(AppVersion):
    """
    AppVersionUpdate object.

    Parameters
    ----------

    """


class AppVersionDeploy(DataModelBase):
    """
    AppVersionDeploy object.

    Parameters
    ----------
        workload_names: Optional[List[StrictStr]]

    """

    workload_names: Optional[List[StrictStr]] = None


class AppResourcesListPaginatedResponseCursor(PaginatorDataModel[type.AppResource]):
    """
    AppResourcesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppResource]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppResource]] = None
    pagination: Optional[PaginationCursor] = None


class AppResourcesListPaginatedResponseLimits(PaginatorDataModel[type.AppResource]):
    """
    AppResourcesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppResource]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppResource]] = None
    pagination: Optional[PaginationLimits] = None


class AppResourcesListPaginatedResponseStream(AppResource):
    """
    AppResourcesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class ResourceCount(DataModelBase):
    """
    ResourceCount object.

    Parameters
    ----------
        total: Optional[StrictInt]
        running: Optional[StrictInt]

    """

    total: Optional[StrictInt] = None
    running: Optional[StrictInt] = None


class Deployment(DataModelBase):
    """
    Deployment object.

    Parameters
    ----------
        status: Optional[enum.AppStatus]
        resource_count: Optional[ResourceCount]

    """

    status: Optional[enum.AppStatus] = None
    resource_count: Optional[ResourceCount] = None


class AppGet(App):
    """
    AppGet object.

    Parameters
    ----------
        deployment: Optional[Deployment]

    """

    deployment: Optional[Deployment] = None


class AppsListPaginatedResponseCursor(PaginatorDataModel[type.AppShort]):
    """
    AppsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppShort]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppShort]] = None
    pagination: Optional[PaginationCursor] = None


class AppsListPaginatedResponseLimits(PaginatorDataModel[type.AppShort]):
    """
    AppsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppShort]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppShort]] = None
    pagination: Optional[PaginationLimits] = None


class AppsListPaginatedResponseStream(AppShort):
    """
    AppsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AppPatch(App):
    """
    AppPatch object.

    Parameters
    ----------
        deployment: Optional[Deployment]

    """

    deployment: Optional[Deployment] = None


class AppsContextListPaginatedResponseCursor(PaginatorDataModel[type.AppsResourceContext]):
    """
    AppsContextListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppsResourceContext]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppsResourceContext]] = None
    pagination: Optional[PaginationCursor] = None


class AppsContextListPaginatedResponseLimits(PaginatorDataModel[type.AppsResourceContext]):
    """
    AppsContextListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppsResourceContext]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppsResourceContext]] = None
    pagination: Optional[PaginationLimits] = None


class AppsContextListPaginatedResponseStream(AppsResourceContext):
    """
    AppsContextListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AppVersionParameterValuesListPaginatedResponseCursor(PaginatorDataModel[type.AppVersionParameter]):
    """
    AppVersionParameterValuesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppVersionParameter]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppVersionParameter]] = None
    pagination: Optional[PaginationCursor] = None


class AppVersionParameterValuesListPaginatedResponseLimits(PaginatorDataModel[type.AppVersionParameter]):
    """
    AppVersionParameterValuesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppVersionParameter]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppVersionParameter]] = None
    pagination: Optional[PaginationLimits] = None


class AppVersionParameterValuesListPaginatedResponseStream(AppVersionParameter):
    """
    AppVersionParameterValuesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AppVersionParametersHistoryListPaginatedResponseCursor(PaginatorDataModel[type.AppVersionParameter]):
    """
    AppVersionParametersHistoryListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppVersionParameter]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppVersionParameter]] = None
    pagination: Optional[PaginationCursor] = None


class AppVersionParametersHistoryListPaginatedResponseLimits(PaginatorDataModel[type.AppVersionParameter]):
    """
    AppVersionParametersHistoryListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppVersionParameter]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppVersionParameter]] = None
    pagination: Optional[PaginationLimits] = None


class AppVersionParametersHistoryListPaginatedResponseStream(AppVersionHistoricParameter):
    """
    AppVersionParametersHistoryListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AppParametersListPaginatedResponseCursor(PaginatorDataModel[type.AppParameter]):
    """
    AppParametersListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AppParameter]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AppParameter]] = None
    pagination: Optional[PaginationCursor] = None


class AppParametersListPaginatedResponseLimits(PaginatorDataModel[type.AppParameter]):
    """
    AppParametersListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AppParameter]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AppParameter]] = None
    pagination: Optional[PaginationLimits] = None


class AppParametersListPaginatedResponseStream(AppParameter):
    """
    AppParametersListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AppVersionParametersUniqueValuesGet(DataModelBase):
    """
    AppVersionParametersUniqueValuesGet object.

    Parameters
    ----------
        app_parameter_values: Optional[Dict[str, Dict[str, List[Union[StrictInt, StrictFloat, StrictStr, StrictBool]]]]]

    """

    app_parameter_values: Optional[Dict[str, Dict[str, List[Union[StrictInt, StrictFloat, StrictStr, StrictBool]]]]] = (
        Field(
            None,
            description="Collection of objects where each object is an App containing an array of values for each Parameter that meets the request filter definitions. Only unique Parameter Values are shown, default values will not be shown.",
        )
    )


class AppVersionParametersFallbackValuesGet(DataModelBase):
    """
    AppVersionParametersFallbackValuesGet object.

    Parameters
    ----------
        resource_parameters: Optional[Dict[str, Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]]]

    """

    resource_parameters: Optional[Dict[str, Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]]] = Field(
        None, description="List of resources in KRN format and their current or fallback asset parameter values."
    )


class ParametersScheduleCreate(ParameterSchedule):
    """
    ParametersScheduleCreate object.

    Parameters
    ----------

    """


class ParametersScheduleGet(ParameterSchedule):
    """
    ParametersScheduleGet object.

    Parameters
    ----------

    """


class ParametersScheduleListPaginatedResponseCursor(PaginatorDataModel[ParametersScheduleGet]):
    """
    ParametersScheduleListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ParametersScheduleGet]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ParametersScheduleGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ParametersScheduleListPaginatedResponseLimits(PaginatorDataModel[ParametersScheduleGet]):
    """
    ParametersScheduleListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ParametersScheduleGet]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ParametersScheduleGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ParametersScheduleListPaginatedResponseStream(ParametersScheduleGet):
    """
    ParametersScheduleListPaginatedResponseStream object.

    Parameters
    ----------

    """


class WorkloadCreate(Workload, Created, Updated):
    """
    WorkloadCreate object.

    Parameters
    ----------

    """


class WorkloadGet(Workload, Created, Updated):
    """
    WorkloadGet object.

    Parameters
    ----------

    """


class WorkloadUpdate(Workload, Created, Updated):
    """
    WorkloadUpdate object.

    Parameters
    ----------

    """


class WorkloadDownload(DataModelBase):
    """
    WorkloadDownload object.

    Parameters
    ----------
        url: Optional[StrictStr]
        expires_in: Optional[StrictInt]

    """

    url: Optional[StrictStr] = Field(None, description="URL to download the Workload package file.")
    expires_in: Optional[StrictInt] = Field(None, description="Time in seconds before the URL expires.")


class WorkloadsListPaginatedResponseCursor(PaginatorDataModel[type.WorkloadSummary]):
    """
    WorkloadsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.WorkloadSummary]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.WorkloadSummary]] = None
    pagination: Optional[PaginationCursor] = None


class WorkloadsListPaginatedResponseLimits(PaginatorDataModel[type.WorkloadSummary]):
    """
    WorkloadsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.WorkloadSummary]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.WorkloadSummary]] = None
    pagination: Optional[PaginationLimits] = None


class WorkloadsListPaginatedResponseStream(WorkloadSummary):
    """
    WorkloadsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class WorkloadLogsGet(DataModelBase):
    """
    WorkloadLogsGet object.

    Parameters
    ----------
        logs: Optional[Dict[str, List[StrictStr]]]

    """

    logs: Optional[Dict[str, List[StrictStr]]] = None


class WorkloadResourcesAdd(Workload, Created, Updated):
    """
    WorkloadResourcesAdd object.

    Parameters
    ----------

    """


class AssetInsightsItem(DataModelBase):
    """
    AssetInsightsItem object.

    Parameters
    ----------
        asset_type_name: Optional[StrictStr]
        asset_type_title: Optional[StrictStr]
        extra_fields: Optional[Dict[str, Any]]
        last_seen: Optional[datetime]
        name: Optional[StrictStr]
        pinned: Optional[StrictBool]
        state: Optional[enum.AssetInsightsState]
        title: Optional[StrictStr]

    """

    asset_type_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Asset Type linked to this Asset.", examples=["beam_pump"]
    )
    asset_type_title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Asset Type.", examples=["Well 01"]
    )
    extra_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="A dictionary of all requested data from the `extra_fields` key in the request body. The key names and values for each column of data are defined in the request body.",
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when this the Asset was last seen online, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(None, description="Unique identifier `name` of the Asset.", examples=["well_01"])
    pinned: Optional[StrictBool] = Field(
        None,
        description="Pinned status of the Asset. The pinned Assets are defined in an array from the request in the key `PinnedAssets`.",
        examples=[True],
    )
    state: Optional[enum.AssetInsightsState] = None
    title: Optional[StrictStr] = Field(None, description="Display name (`title`) of the Asset.", examples=["Well 01"])


class AssetInsightsGetPaginated(PaginatorDataModel[AssetInsightsItem]):
    """
    AssetInsightsGetPaginated object.

    Parameters
    ----------
        data: Optional[List[AssetInsightsItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[AssetInsightsItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Asset objects starting from `page` number.",
    )
    pagination: Optional[PaginationLimits] = None


class AssetCreate(Asset):
    """
    AssetCreate object.

    Parameters
    ----------

    """


class AssetsListPaginatedResponseCursor(PaginatorDataModel[type.Asset]):
    """
    AssetsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Asset]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Asset]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Assets objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class AssetsListPaginatedResponseLimits(PaginatorDataModel[type.Asset]):
    """
    AssetsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Asset]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Asset]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Assets objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class AssetsListPaginatedResponseStream(Asset):
    """
    AssetsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AssetsAdvancedListPaginatedResponseCursor(AssetsListPaginatedResponseCursor):
    """
    AssetsAdvancedListPaginatedResponseCursor object.

    Parameters
    ----------

    """


class AssetsAdvancedListPaginatedResponseLimits(AssetsListPaginatedResponseLimits):
    """
    AssetsAdvancedListPaginatedResponseLimits object.

    Parameters
    ----------

    """


class AssetsAdvancedListPaginatedResponseStream(AssetsListPaginatedResponseStream):
    """
    AssetsAdvancedListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AssetStatusCountGet(DataModelBase):
    """
    AssetStatusCountGet object.

    Parameters
    ----------
        offline: Optional[StrictInt]
        online: Optional[StrictInt]
        total: Optional[StrictInt]
        unknown: Optional[StrictInt]

    """

    offline: Optional[StrictInt] = Field(
        None, description="Count of all Assets that are inactive and not receiving data.", examples=[592]
    )
    online: Optional[StrictInt] = Field(
        None, description="Count of all Assets that are receiving active data.", examples=[2787]
    )
    total: Optional[StrictInt] = Field(None, description="Count of all Assets.", examples=[3429])
    unknown: Optional[StrictInt] = Field(
        None,
        description="Count of all Assets that has no Data Streams or all Data Streams have never received data.",
        examples=[50],
    )


class AssetStatusCurrentGet(AssetStatus):
    """
    AssetStatusCurrentGet object.

    Parameters
    ----------

    """


class AssetTypeCreate(AssetType):
    """
    AssetTypeCreate object.

    Parameters
    ----------

    """


class AssetTypesListPaginatedResponseCursor(PaginatorDataModel[type.AssetType]):
    """
    AssetTypesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.AssetType]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.AssetType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Asset Types objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class AssetTypesListPaginatedResponseLimits(PaginatorDataModel[type.AssetType]):
    """
    AssetTypesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.AssetType]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.AssetType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Asset Types objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class AssetTypesListPaginatedResponseStream(AssetType):
    """
    AssetTypesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AssetTypesAdvancedListPaginatedResponseCursor(AssetTypesListPaginatedResponseCursor):
    """
    AssetTypesAdvancedListPaginatedResponseCursor object.

    Parameters
    ----------

    """


class AssetTypesAdvancedListPaginatedResponseLimits(AssetTypesListPaginatedResponseLimits):
    """
    AssetTypesAdvancedListPaginatedResponseLimits object.

    Parameters
    ----------

    """


class AssetTypesAdvancedListPaginatedResponseStream(AssetTypesListPaginatedResponseStream):
    """
    AssetTypesAdvancedListPaginatedResponseStream object.

    Parameters
    ----------

    """


class AssetTypeGet(AssetType):
    """
    AssetTypeGet object.

    Parameters
    ----------

    """


class AssetTypeUpdate(AssetType):
    """
    AssetTypeUpdate object.

    Parameters
    ----------

    """


class AssetGet(Asset):
    """
    AssetGet object.

    Parameters
    ----------

    """


class AssetUpdate(Asset):
    """
    AssetUpdate object.

    Parameters
    ----------

    """


class ControlChangeClustering(DataModelBase):
    """
    ControlChangeClustering object.

    Parameters
    ----------
        control_change_ids: Optional[List[UUID]]
        count: Optional[StrictInt]
        time_bucket_start: Optional[datetime]

    """

    control_change_ids: Optional[List[UUID]] = Field(
        None,
        description="An array of Control Change `id`'s that have been counted.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "518bcb79-ffaa-4d3f-8042-52634c34b71e"]],
    )
    count: Optional[StrictInt] = Field(
        None,
        description="Number of occurrences of Control Changes over the time period of `time_bucket` that meet the request parameters starting from time `time_bucket_start`.",
        examples=[2],
    )
    time_bucket_start: Optional[datetime] = Field(
        None,
        description="Time of the start of the count for the current `time_bucket` period in RFC 3339 UTC date/time format.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class ControlChangeCreate(DataModelBase):
    """
    ControlChangeCreate object.

    Parameters
    ----------
        created_by: Optional[StrictStr]
        created_type: Optional[StrictStr]
        id: UUID
        last_state: Optional[enum.ControlChangeState]
        payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        resource: Optional[KRN]
        source: Optional[KRN]
        timestamp: Optional[datetime]
        trace_id: UUID

    """

    created_by: Optional[StrictStr] = Field(
        None,
        description="Name of the process that created the Control Change. This could be a user, workload, application, etc.",
        examples=[["krn:user:person@kelvin.ai", "krn:app:motor_speed_control"]],
    )
    created_type: Optional[StrictStr] = Field(
        None,
        description="Type of process that created the Control Change. This is inferred from `source`.",
        examples=["recommendation"],
    )
    id: UUID = Field(
        ...,
        description="A unique randomly generated UUID as the key `id` for the Control Change.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    last_state: Optional[enum.ControlChangeState] = Field(None, description="Current state of the Control Change.")
    payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None,
        description="The new value payload to be applied to the Asset / Data Stream pair in `resource`.",
        examples=[2000],
    )
    resource: Optional[KRN] = Field(
        None,
        description="The asset / data stream pair that this Control Change will be applied to.",
        examples=["krn:ad:beam_pump_01/motor_speed_set_point"],
    )
    source: Optional[KRN] = Field(
        None,
        description="The process that created the Control Change request. This can be a user or an automated process like a workload, application, recommendation, etc.",
        examples=["krn:ad:beam_pump_01/motor_speed_set_point"],
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="UTC time when the log was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    trace_id: UUID = Field(
        ...,
        description="This is for internal purposes and is the same as the `id`.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )


class ControlChangeGetStatus(DataModelBase):
    """
    ControlChangeGetStatus object.

    Parameters
    ----------
        message: Optional[StrictStr]
        reported: Optional[type.ControlChangeReported]
        state: enum.ControlChangeState
        timestamp: Optional[datetime]

    """

    message: Optional[StrictStr] = Field(
        None, description="A message about the change in status. This will only appear if there is a message attached."
    )
    reported: Optional[type.ControlChangeReported] = None
    state: enum.ControlChangeState = Field(..., description="Control Change state when log was created.")
    timestamp: Optional[datetime] = Field(
        None,
        description="UTC time when the log was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class ControlChangeGet(DataModelBase):
    """
    ControlChangeGet object.

    Parameters
    ----------
        created: Optional[datetime]
        created_by: Optional[StrictStr]
        created_type: Optional[StrictStr]
        id: UUID
        trace_id: Optional[StrictStr]
        last_message: Optional[StrictStr]
        last_state: Optional[enum.ControlChangeState]
        retries: Optional[StrictInt]
        timeout: Optional[StrictInt]
        expiration_date: Optional[datetime]
        from_: Optional[type.ControlChangeFrom]
        reported: Optional[type.ControlChangeReported]
        payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        resource: KRN
        status_log: Optional[List[ControlChangeGetStatus]]
        timestamp: Optional[datetime]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Control Change was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created_by: Optional[StrictStr] = Field(
        None,
        description="Name of the process that created the Control Change. This could be a user, workload, application, recommendation, etc.",
        examples=[["krn:user:person@kelvin.ai", "krn:app:motor_speed_control"]],
    )
    created_type: Optional[StrictStr] = Field(
        None,
        description="Type of process that created the Control Change. This is inferred from `source`.",
        examples=["recommendation"],
    )
    id: UUID = Field(
        ...,
        description="A unique randomly generated UUID as the key `id` for the Control Change.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    trace_id: Optional[StrictStr] = Field(None, examples=["app-trace-123"])
    last_message: Optional[StrictStr] = Field(
        None,
        description="Last message received from the Control Change Manager.",
        examples=[
            "The Control Change was sent to the Bridge. At this stage, the system is monitoring according to the Acceptance Criteria parameters and the retry logic."
        ],
    )
    last_state: Optional[enum.ControlChangeState] = Field(None, description="Current state of the Control Change.")
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
    expiration_date: Optional[datetime] = Field(
        None,
        description="UTC time when the Control Change will expire and the `status` is automatically marked as `failed`, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    from_: Optional[type.ControlChangeFrom] = Field(None, alias="from")
    reported: Optional[type.ControlChangeReported] = None
    payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None,
        description="The new value payload to be applied to the Asset / Data Stream pair in `resource`.",
        examples=[2000],
    )
    resource: KRN = Field(
        ...,
        description="The asset / data stream pair that this Control Change will be applied to.",
        examples=["krn:ad:beam_pump_01/motor_speed_set_point"],
    )
    status_log: Optional[List[ControlChangeGetStatus]] = Field(
        None, description="Array of dictionary objects with the details of each `status` change."
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="UTC time when the Control Change was created, formatted in RFC 3339.",
        examples=["2023-11-13T12:00:00Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Control Change keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class ControlChangeLastGetPaginatedResponseCursor(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangeLastGetPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ControlChangeLastGetPaginatedResponseLimits(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangeLastGetPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ControlChangeLastGetPaginatedResponseStream(ControlChangeGet):
    """
    ControlChangeLastGetPaginatedResponseStream object.

    Parameters
    ----------

    """


class ControlChangesListPaginatedResponseCursor(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ControlChangesListPaginatedResponseLimits(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ControlChangesListPaginatedResponseStream(ControlChangeGet):
    """
    ControlChangesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class ControlChangeRangeGetPaginatedResponseCursor(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangeRangeGetPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ControlChangeRangeGetPaginatedResponseLimits(PaginatorDataModel[ControlChangeGet]):
    """
    ControlChangeRangeGetPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ControlChangeGet]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ControlChangeGet]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Control Changes and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ControlChangeRangeGetPaginatedResponseStream(ControlChangeGet):
    """
    ControlChangeRangeGetPaginatedResponseStream object.

    Parameters
    ----------

    """


class CustomActionCreate(CustomAction):
    """
    CustomActionCreate object.

    Parameters
    ----------

    """


class CustomActionsListPaginatedResponseCursor(PaginatorDataModel[type.CustomAction]):
    """
    CustomActionsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.CustomAction]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.CustomAction]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Custom Actions and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class CustomActionsListPaginatedResponseLimits(PaginatorDataModel[type.CustomAction]):
    """
    CustomActionsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.CustomAction]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.CustomAction]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Custom Actions and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class CustomActionsListPaginatedResponseStream(CustomAction):
    """
    CustomActionsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class CustomActionGet(CustomAction):
    """
    CustomActionGet object.

    Parameters
    ----------

    """


class CustomActionsTypeCreate(CustomActionType):
    """
    CustomActionsTypeCreate object.

    Parameters
    ----------

    """


class CustomActionsTypesListPaginatedCursor(PaginatorDataModel[type.CustomActionType]):
    """
    CustomActionsTypesListPaginatedCursor object.

    Parameters
    ----------
        data: Optional[List[type.CustomActionType]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.CustomActionType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendation Types and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class CustomActionsTypesListPaginatedLimits(PaginatorDataModel[type.CustomActionType]):
    """
    CustomActionsTypesListPaginatedLimits object.

    Parameters
    ----------
        data: Optional[List[type.CustomActionType]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.CustomActionType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendation Types and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class CustomActionsTypesListPaginatedStream(CustomActionType):
    """
    CustomActionsTypesListPaginatedStream object.

    Parameters
    ----------

    """


class CustomActionsTypeGet(CustomActionType):
    """
    CustomActionsTypeGet object.

    Parameters
    ----------

    """


class CustomActionsTypeUpdate(CustomActionType):
    """
    CustomActionsTypeUpdate object.

    Parameters
    ----------

    """


class DataQualityCreate(DataQuality):
    """
    DataQualityCreate object.

    Parameters
    ----------

    """


class DataQualityGet(DataQuality):
    """
    DataQualityGet object.

    Parameters
    ----------

    """


class DataQualityUpdate(DataQuality):
    """
    DataQualityUpdate object.

    Parameters
    ----------

    """


class DataQualityListPaginatedResponseCursor(PaginatorDataModel[type.DataQuality]):
    """
    DataQualityListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.DataQuality]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.DataQuality]] = None
    pagination: Optional[PaginationCursor] = None


class DataQualityListPaginatedResponseLimits(PaginatorDataModel[type.DataQuality]):
    """
    DataQualityListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.DataQuality]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.DataQuality]] = None
    pagination: Optional[PaginationLimits] = None


class DataQualityListPaginatedResponseStream(DataQuality):
    """
    DataQualityListPaginatedResponseStream object.

    Parameters
    ----------

    """


class DataQualityData(DataModelBase):
    """
    DataQualityData object.

    Parameters
    ----------
        kelvin_duplicate_detection: Optional[List[type.SimulationData]]
        kelvin_out_of_range_detection: Optional[List[type.SimulationData]]
        kelvin_outlier_detection: Optional[List[type.SimulationData]]
        kelvin_data_availability: Optional[List[type.SimulationData]]

    """

    kelvin_duplicate_detection: Optional[List[type.SimulationData]] = None
    kelvin_out_of_range_detection: Optional[List[type.SimulationData]] = None
    kelvin_outlier_detection: Optional[List[type.SimulationData]] = None
    kelvin_data_availability: Optional[List[type.SimulationData]] = None


class DataQualitySimulate(DataModelBase):
    """
    DataQualitySimulate object.

    Parameters
    ----------
        timeseries_data: Optional[List[type.SimulationData]]
        data_quality_data: Optional[DataQualityData]

    """

    timeseries_data: Optional[List[type.SimulationData]] = Field(
        None, description="The simulated timeseries data for the specified resource."
    )
    data_quality_data: Optional[DataQualityData] = Field(
        None, description="The simulated Data Quality data for the specified resource."
    )


class DataStreamsDataTypesListPaginatedResponseCursor(PaginatorDataModel[type.DataStreamDataType]):
    """
    DataStreamsDataTypesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.DataStreamDataType]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.DataStreamDataType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Type objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataStreamsDataTypesListPaginatedResponseLimits(PaginatorDataModel[type.DataStreamDataType]):
    """
    DataStreamsDataTypesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.DataStreamDataType]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.DataStreamDataType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Type objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataStreamsDataTypesListPaginatedResponseStream(DataStreamDataType):
    """
    DataStreamsDataTypesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class DataStreamSemanticTypeCreate(DataStreamSemanticType):
    """
    DataStreamSemanticTypeCreate object.

    Parameters
    ----------

    """


class DataStreamSemanticTypeUpdate(DataStreamSemanticType):
    """
    DataStreamSemanticTypeUpdate object.

    Parameters
    ----------

    """


class DataStreamSemanticTypeGet(DataStreamSemanticType):
    """
    DataStreamSemanticTypeGet object.

    Parameters
    ----------

    """


class DataStreamsSemanticTypesListPaginatedResponseCursor(PaginatorDataModel[type.DataStreamSemanticType]):
    """
    DataStreamsSemanticTypesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.DataStreamSemanticType]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.DataStreamSemanticType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Semantic Type objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataStreamsSemanticTypesListPaginatedResponseLimits(PaginatorDataModel[type.DataStreamSemanticType]):
    """
    DataStreamsSemanticTypesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.DataStreamSemanticType]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.DataStreamSemanticType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Semantic Type objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataStreamsSemanticTypesListPaginatedResponseStream(DataStreamSemanticType):
    """
    DataStreamsSemanticTypesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class DataStreamUnitCreate(Unit):
    """
    DataStreamUnitCreate object.

    Parameters
    ----------

    """


class DataStreamUnitUpdate(Unit):
    """
    DataStreamUnitUpdate object.

    Parameters
    ----------

    """


class DataStreamUnitGet(Unit):
    """
    DataStreamUnitGet object.

    Parameters
    ----------

    """


class DataStreamsUnitsListPaginatedResponseCursor(PaginatorDataModel[type.Unit]):
    """
    DataStreamsUnitsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Unit]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Unit]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Unit objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataStreamsUnitsListPaginatedResponseLimits(PaginatorDataModel[type.Unit]):
    """
    DataStreamsUnitsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Unit]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Unit]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Unit objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataStreamsUnitsListPaginatedResponseStream(Unit):
    """
    DataStreamsUnitsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class DataStream(DataModelBase):
    """
    DataStream object.

    Parameters
    ----------
        created: Optional[datetime]
        description: Optional[StrictStr]
        name: Optional[StrictStr]
        data_type_name: Optional[enum.DataType]
        semantic_type_name: Optional[StrictStr]
        title: Optional[StrictStr]
        type: Optional[enum.DataStreamType]
        unit_name: Optional[StrictStr]
        is_protected: Optional[StrictBool]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Data Stream was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    description: Optional[StrictStr] = Field(
        None,
        description="Detailed description of the Data Stream.",
        examples=["The rate at which gas flows from the reservoir to the surface."],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Data Stream.", examples=["gas_flow_rate"]
    )
    data_type_name: Optional[enum.DataType] = Field(None, description="Data type of the Data Stream.")
    semantic_type_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Semantic Type that describes the nature, purpose or origin of the data.",
        examples=["volume_flow_rate"],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Data Stream.", examples=["Gas Flow Rate"]
    )
    type: Optional[enum.DataStreamType] = None
    unit_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Units that describes the type or category of data represented by each unit. Only available if the Primitive Type is `number`.",
        examples=["litre_per_second"],
    )
    is_protected: Optional[StrictBool] = Field(
        None,
        description="Indicates whether the Data Stream is protected or not. If `true`, the Data Stream is protected and cannot be deleted or modified.",
        examples=[False],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Data Stream keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class DataStreamCreate(DataStream):
    """
    DataStreamCreate object.

    Parameters
    ----------

    """


class DataStreamUpdate(DataStream):
    """
    DataStreamUpdate object.

    Parameters
    ----------

    """


class DataStreamGet(DataStream):
    """
    DataStreamGet object.

    Parameters
    ----------

    """


class DataStreamsListPaginatedResponseCursor(PaginatorDataModel[DataStream]):
    """
    DataStreamsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[DataStream]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[DataStream]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Streams objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataStreamsListPaginatedResponseLimits(PaginatorDataModel[DataStream]):
    """
    DataStreamsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[DataStream]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[DataStream]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Streams objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataStreamsListPaginatedResponseStream(DataStream):
    """
    DataStreamsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class Context(DataModelBase):
    """
    Context object.

    Parameters
    ----------
        created: Optional[datetime]
        resource: Optional[KRN]
        source: Optional[KRN]
        updated: Optional[datetime]
        writable: Optional[StrictBool]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Asset / Data Stream pair was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    resource: Optional[KRN] = Field(
        None, description="Asset `name` that is associated with the Data Stream.", examples=["krn:asset:bp_16"]
    )
    source: Optional[KRN] = Field(
        None,
        description="Workload `name` that is sending data to the Asset / Data Stream pair.",
        examples=["krn:wlappv:cluster1/app1/1.2.0"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Asset / Data Stream pair keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    writable: Optional[StrictBool] = Field(
        None,
        description="Indicates whether the Asset / Data Stream pair `write` key is read/write (`true`) or read only (`false`).",
        examples=[True],
    )


class DataStreamContext(DataModelBase):
    """
    DataStreamContext object.

    Parameters
    ----------
        context: Optional[List[Context]]
        created: Optional[datetime]
        datastream_name: Optional[StrictStr]
        updated: Optional[datetime]

    """

    context: Optional[List[Context]] = Field(
        None,
        description="An array of objects associated with the Data Stream. Each object contains keys for the Asset `name` of the Asset / Data Stream pair and and the Source for the pair.",
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Data Stream was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    datastream_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Data Stream.", examples=["gas_flow_rate"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Data Stream keys were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )


class DataStreamContextGet(DataStreamContext):
    """
    DataStreamContextGet object.

    Parameters
    ----------

    """


class DataStreamContextsListPaginatedResponseCursor(PaginatorDataModel[DataStreamContext]):
    """
    DataStreamContextsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[DataStreamContext]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[DataStreamContext]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Streams and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataStreamContextsListPaginatedResponseLimits(PaginatorDataModel[DataStreamContext]):
    """
    DataStreamContextsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[DataStreamContext]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[DataStreamContext]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Streams and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataStreamContextsListPaginatedResponseStream(DataStreamContext):
    """
    DataStreamContextsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class DataTagCreate(DataTag):
    """
    DataTagCreate object.

    Parameters
    ----------

    """


class DataTagUpdate(DataTag):
    """
    DataTagUpdate object.

    Parameters
    ----------

    """


class DataTagGet(DataTag):
    """
    DataTagGet object.

    Parameters
    ----------

    """


class DataTagListPaginatedResponseCursor(PaginatorDataModel[type.DataTag]):
    """
    DataTagListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.DataTag]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.DataTag]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Tag objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class DataTagListPaginatedResponseLimits(PaginatorDataModel[type.DataTag]):
    """
    DataTagListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.DataTag]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.DataTag]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Tag objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class DataTagListPaginatedResponseStream(DataTag):
    """
    DataTagListPaginatedResponseStream object.

    Parameters
    ----------

    """


class TagCreate(Tag):
    """
    TagCreate object.

    Parameters
    ----------

    """


class TagUpdate(Tag):
    """
    TagUpdate object.

    Parameters
    ----------

    """


class TagGet(Tag):
    """
    TagGet object.

    Parameters
    ----------

    """


class TagListPaginatedResponseCursor(PaginatorDataModel[type.Tag]):
    """
    TagListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Tag]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Tag]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Tag objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class TagListPaginatedResponseLimits(PaginatorDataModel[type.Tag]):
    """
    TagListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Tag]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Tag]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Tag objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class TagListPaginatedResponseStream(Tag):
    """
    TagListPaginatedResponseStream object.

    Parameters
    ----------

    """


class FileUpload(FileStorage):
    """
    FileUpload object.

    Parameters
    ----------

    """


class FilesListPaginatedCursor(PaginatorDataModel[type.FileStorage]):
    """
    FilesListPaginatedCursor object.

    Parameters
    ----------
        data: Optional[List[type.FileStorage]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.FileStorage]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` file objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class FilesListPaginatedLimits(PaginatorDataModel[type.FileStorage]):
    """
    FilesListPaginatedLimits object.

    Parameters
    ----------
        data: Optional[List[type.FileStorage]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.FileStorage]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` file objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class FilesListPaginatedStream(FileStorage):
    """
    FilesListPaginatedStream object.

    Parameters
    ----------

    """


class FileGet(FileStorage):
    """
    FileGet object.

    Parameters
    ----------

    """


class GuardrailCreate(GuardrailModel):
    """
    GuardrailCreate object.

    Parameters
    ----------

    """


class GuardrailGet(GuardrailModel):
    """
    GuardrailGet object.

    Parameters
    ----------

    """


class GuardrailUpdate(GuardrailModel):
    """
    GuardrailUpdate object.

    Parameters
    ----------

    """


class GuardrailsListPaginatedResponseCursor(PaginatorDataModel[type.GuardrailModel]):
    """
    GuardrailsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.GuardrailModel]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.GuardrailModel]] = None
    pagination: Optional[PaginationCursor] = None


class GuardrailsListPaginatedResponseLimits(PaginatorDataModel[type.GuardrailModel]):
    """
    GuardrailsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.GuardrailModel]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.GuardrailModel]] = None
    pagination: Optional[PaginationLimits] = None


class GuardrailsListPaginatedResponseStream(GuardrailModel):
    """
    GuardrailsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class BulkGuardrailsCreate(DataModelBase):
    """
    BulkGuardrailsCreate object.

    Parameters
    ----------
        data: Optional[List[type.GuardrailModel]]

    """

    data: Optional[List[type.GuardrailModel]] = Field(
        None, description="A dictionary with a data property that contains an array of all Guardrail objects created."
    )


class InstanceAuditLogGetItem(InstanceAuditLogItem):
    """
    InstanceAuditLogGetItem object.

    Parameters
    ----------

    """


class InstanceAuditLogsListPaginatedResponseCursor(PaginatorDataModel[InstanceAuditLogGetItem]):
    """
    InstanceAuditLogsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[InstanceAuditLogGetItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[InstanceAuditLogGetItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Audit Log objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class InstanceAuditLogsListPaginatedResponseLimits(PaginatorDataModel[InstanceAuditLogGetItem]):
    """
    InstanceAuditLogsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[InstanceAuditLogGetItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[InstanceAuditLogGetItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Audit Log objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class InstanceAuditLogsListPaginatedResponseStream(InstanceAuditLogGetItem):
    """
    InstanceAuditLogsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class InstanceAuditLogGet(DataModelBase):
    """
    InstanceAuditLogGet object.

    Parameters
    ----------
        action: Optional[StrictStr]
        created: Optional[datetime]
        id: Optional[StrictInt]
        identifier: Optional[StrictStr]
        meta: Optional[Dict[str, Any]]
        namespace: Optional[StrictStr]
        request_id: Optional[StrictStr]
        user_id: Optional[UUID]
        username: Optional[StrictStr]

    """

    action: Optional[StrictStr] = Field(
        None, description="Type of action performed over the platform resource.", examples=["BATCH-UPDATE-NODE"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Audit Log was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    id: Optional[StrictInt] = Field(None, description="Unique ID of the Audit Log entry.", examples=[4739892])
    identifier: Optional[StrictStr] = Field(
        None, description="The platform resource that generated the audit log.", examples=["application_name"]
    )
    meta: Optional[Dict[str, Any]] = Field(
        None,
        description="Contextual information about the action. For example, updating a resource you probably see information about the previous state (FROM key) and the current state (TO key) of the resource.",
    )
    namespace: Optional[StrictStr] = Field(
        None, description="In which service the audit log was created.", examples=["api-workload"]
    )
    request_id: Optional[StrictStr] = Field(None, description="Deprecated. Not being used.")
    user_id: Optional[UUID] = Field(
        None, description="User ID that initiated the action.", examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"]
    )
    username: Optional[StrictStr] = Field(
        None, description="Username used to create the action.", examples=["service-account-node-client-aws-cluster"]
    )


class InstanceSettingsKelvinClusterGet(InstanceSettings):
    """
    InstanceSettingsKelvinClusterGet object.

    Parameters
    ----------

    """


class InstanceSettingsKelvinClusterUpdate(InstanceSettings):
    """
    InstanceSettingsKelvinClusterUpdate object.

    Parameters
    ----------

    """


class InstanceSettingsListPaginatedResponseCursor(PaginatorDataModel[type.InstanceSettings]):
    """
    InstanceSettingsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.InstanceSettings]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.InstanceSettings]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Instance Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class InstanceSettingsListPaginatedResponseLimits(PaginatorDataModel[type.InstanceSettings]):
    """
    InstanceSettingsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.InstanceSettings]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.InstanceSettings]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Instance Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class InstanceSettingsListPaginatedResponseStream(InstanceSettings):
    """
    InstanceSettingsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class InstanceSettingsGet(InstanceSettings):
    """
    InstanceSettingsGet object.

    Parameters
    ----------

    """


class InstanceSettingsUpdate(InstanceSettings):
    """
    InstanceSettingsUpdate object.

    Parameters
    ----------

    """


class ComponentStatus(DataModelBase):
    """
    ComponentStatus object.

    Parameters
    ----------
        name: Optional[StrictStr]
        status: Optional[StrictBool]

    """

    name: Optional[StrictStr] = Field(None, description="Name of service on the Instance.", examples=["api-workload"])
    status: Optional[StrictBool] = Field(
        None, description="Current status of the service on the Instance.", examples=[True]
    )


class InstanceStatusGet(DataModelBase):
    """
    InstanceStatusGet object.

    Parameters
    ----------
        components: Optional[List[ComponentStatus]]
        status: Optional[StrictBool]

    """

    components: Optional[List[ComponentStatus]] = None
    status: Optional[StrictBool] = Field(None, description="Overall status of the Instance.", examples=[True])


class OrchestrationClustersCreate(OrchestrationCluster):
    """
    OrchestrationClustersCreate object.

    Parameters
    ----------

    """


class OrchestrationClustersCreateItem(DataModelBase):
    """
    OrchestrationClustersCreateItem object.

    Parameters
    ----------
        created: Optional[datetime]
        last_seen: Optional[datetime]
        name: Optional[StrictStr]
        ready: Optional[StrictBool]
        kelvin_version: Optional[StrictStr]
        container_version: Optional[StrictStr]
        status: Optional[enum.OrchestrationClusterStatus]
        title: Optional[StrictStr]
        type: Optional[enum.ClusterType]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Cluster was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Cluster was last seen by the Cloud, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Cluster.", examples=["aws-cluster"]
    )
    ready: Optional[StrictBool] = Field(
        None, description="Setting to inform Kelvin UI if the Cluster is ready.", examples=[True]
    )
    kelvin_version: Optional[StrictStr] = Field(
        None, description="Current version of Kelvin Software installed on the Cluster.", examples=["9.0.0"]
    )
    container_version: Optional[StrictStr] = Field(
        None,
        description="Current version of the runtime container installed on the Cluster.",
        examples=["v1.24.10+k3s1"],
    )
    status: Optional[enum.OrchestrationClusterStatus] = None
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Cluster.", examples=["AWS Cluster"]
    )
    type: Optional[enum.ClusterType] = Field(
        None, description="Type of Cluster deployed. `k3s` is managed by Kelvin, `kubernetes` is managed by client."
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Cluster keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class OrchestrationClustersListPaginatedResponseCursor(PaginatorDataModel[OrchestrationClustersCreateItem]):
    """
    OrchestrationClustersListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[OrchestrationClustersCreateItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[OrchestrationClustersCreateItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Clusters and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class OrchestrationClustersListPaginatedResponseLimits(PaginatorDataModel[OrchestrationClustersCreateItem]):
    """
    OrchestrationClustersListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[OrchestrationClustersCreateItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[OrchestrationClustersCreateItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Clusters and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class OrchestrationClustersListPaginatedResponseStream(OrchestrationClustersCreateItem):
    """
    OrchestrationClustersListPaginatedResponseStream object.

    Parameters
    ----------

    """


class OrchestrationClustersGet(OrchestrationCluster):
    """
    OrchestrationClustersGet object.

    Parameters
    ----------

    """


class OrchestrationClustersCreateManifestImageItem(DataModelBase):
    """
    OrchestrationClustersCreateManifestImageItem object.

    Parameters
    ----------
        args: Optional[StrictStr]
        path: Optional[StrictStr]

    """

    args: Optional[StrictStr] = Field(
        None, description="Additional arguments for the image, if any.", examples=["--help"]
    )
    path: Optional[StrictStr] = Field(
        None, description="The path or location of the image.", examples=["<URL>/analysis-frame/<app-name>:{app-}"]
    )


class OrchestrationClustersCreateManifestItem(DataModelBase):
    """
    OrchestrationClustersCreateManifestItem object.

    Parameters
    ----------
        content: Optional[StrictStr]
        file_name: Optional[StrictStr]

    """

    content: Optional[StrictStr] = Field(
        None, description="Base64 encoded content of the manifest file.", examples=["YXBpVmVyc2lvbj..."]
    )
    file_name: Optional[StrictStr] = Field(
        None, description="Name of the manifest file.", examples=["certificate.yaml"]
    )


class OrchestrationClustersCreateManifestUpgrade(DataModelBase):
    """
    OrchestrationClustersCreateManifestUpgrade object.

    Parameters
    ----------
        download_type: Optional[StrictStr]
        upgrade_type: Optional[StrictStr]

    """

    download_type: Optional[StrictStr] = Field(
        None, description="Type of download process for the upgrade.", examples=["instantly"]
    )
    upgrade_type: Optional[StrictStr] = Field(None, description="Type of upgrade process.", examples=["instantly"])


class OrchestrationClustersManifestsGet(DataModelBase):
    """
    OrchestrationClustersManifestsGet object.

    Parameters
    ----------
        images: Optional[List[OrchestrationClustersCreateManifestImageItem]]
        manifests: Optional[List[OrchestrationClustersCreateManifestItem]]
        revision: Optional[StrictStr]
        upgrade: Optional[OrchestrationClustersCreateManifestUpgrade]

    """

    images: Optional[List[OrchestrationClustersCreateManifestImageItem]] = Field(
        None, description="List of images on the Cluster."
    )
    manifests: Optional[List[OrchestrationClustersCreateManifestItem]] = Field(
        None, description="List of Manifest files on the Cluster."
    )
    revision: Optional[StrictStr] = Field(
        None, description="Current Kelvin Software version installed on the Cluster.", examples=["4.0.0-rc2024.521"]
    )
    upgrade: Optional[OrchestrationClustersCreateManifestUpgrade] = None


class OrchestrationClustersNodesGetItem(DataModelBase):
    """
    OrchestrationClustersNodesGetItem object.

    Parameters
    ----------
        created: Optional[datetime]
        last_seen: Optional[datetime]
        main: Optional[StrictBool]
        name: Optional[StrictStr]
        status: Optional[enum.OrchestrationNodeStatus]
        updated: Optional[datetime]
        warnings: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Node was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Node was last seen by the Cloud, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    main: Optional[StrictBool] = Field(
        None, description="Whether the Node is the Master Node in the Cluster.", examples=[True]
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Node.", examples=["internal-node-01"]
    )
    status: Optional[enum.OrchestrationNodeStatus] = None
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Node keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    warnings: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None,
        description="Any warning messages received from Kubernetes.",
        examples=[
            "container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized"
        ],
    )


class OrchestrationClustersNodeListPaginatedResponseCursor(PaginatorDataModel[OrchestrationClustersNodesGetItem]):
    """
    OrchestrationClustersNodeListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[OrchestrationClustersNodesGetItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[OrchestrationClustersNodesGetItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Nodes and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class OrchestrationClustersNodeListPaginatedResponseLimits(PaginatorDataModel[OrchestrationClustersNodesGetItem]):
    """
    OrchestrationClustersNodeListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[OrchestrationClustersNodesGetItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[OrchestrationClustersNodesGetItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Nodes and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class OrchestrationClustersNodeListPaginatedResponseStream(OrchestrationClustersNodesGetItem):
    """
    OrchestrationClustersNodeListPaginatedResponseStream object.

    Parameters
    ----------

    """


class OrchestrationClustersNodesGetConditionItem(DataModelBase):
    """
    OrchestrationClustersNodesGetConditionItem object.

    Parameters
    ----------
        lastHeartbeatTime: Optional[datetime]
        lastTransitionTime: Optional[datetime]
        message: Optional[StrictStr]
        name: Optional[StrictStr]
        reason: Optional[StrictStr]
        status: Optional[StrictStr]
        status_message: Optional[StrictStr]
        type: Optional[StrictStr]

    """

    lastHeartbeatTime: Optional[datetime] = Field(
        None, description="Timestamp of the last heartbeat received.", examples=["2024-01-20T12:34:56Z"]
    )
    lastTransitionTime: Optional[datetime] = Field(
        None, description="Timestamp of the last status transition.", examples=["2024-01-19T11:30:00Z"]
    )
    message: Optional[StrictStr] = Field(
        None,
        description="Human-readable message indicating details about the transition.",
        examples=["kubelet has no disk pressure"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique name identifying the resource.", examples=["Disk Pressure"]
    )
    reason: Optional[StrictStr] = Field(
        None,
        description="Short, machine-understandable string that gives the reason for the condition's last transition.",
        examples=["KubeletHasNoDiskPressure"],
    )
    status: Optional[StrictStr] = Field(
        None, description="Status of the condition, typically True, False, or Unknown.", examples=["False"]
    )
    status_message: Optional[StrictStr] = Field(None, description="Detailed status message.", examples=["ready"])
    type: Optional[StrictStr] = Field(None, description="Type of the condition.", examples=["DiskPressure"])


class OrchestrationClustersNodesGetSystemInfo(DataModelBase):
    """
    OrchestrationClustersNodesGetSystemInfo object.

    Parameters
    ----------
        architecture: Optional[StrictStr]
        boot_id: Optional[StrictStr]
        container_runtime_version: Optional[StrictStr]
        host_name: Optional[StrictStr]
        kernel_version: Optional[StrictStr]
        kube_proxy_version: Optional[StrictStr]
        kubelet_version: Optional[StrictStr]
        machine_id: Optional[StrictStr]
        operating_system: Optional[StrictStr]
        os_image: Optional[StrictStr]
        system_uuid: Optional[StrictStr]

    """

    architecture: Optional[StrictStr] = Field(
        None, description="Architecture of the node's system (e.g., x86_64, arm).", examples=["amd64"]
    )
    boot_id: Optional[StrictStr] = Field(
        None,
        description="Unique identifier for the current boot session.",
        examples=["c24e67a8-067f-462d-b569-12d06f700117"],
    )
    container_runtime_version: Optional[StrictStr] = Field(
        None, description="Version of the container runtime.", examples=["containerd://1.6.15-k3s1"]
    )
    host_name: Optional[StrictStr] = Field(None, description="Hostname of the node.", examples=["node01"])
    kernel_version: Optional[StrictStr] = Field(
        None, description="Version of the node's kernel.", examples=["5.15.0-1050-aws"]
    )
    kube_proxy_version: Optional[StrictStr] = Field(
        None, description="Version of kube-proxy running on the node.", examples=["v1.24.10+k3s1"]
    )
    kubelet_version: Optional[StrictStr] = Field(
        None, description="Version of kubelet running on the node.", examples=["v1.24.10+k3s1"]
    )
    machine_id: Optional[StrictStr] = Field(
        None, description="Unique identifier of the node's machine.", examples=["ec22bcece3288e3a08d7b7ce4b0742c1"]
    )
    operating_system: Optional[StrictStr] = Field(
        None, description="Operating system running on the node.", examples=["linux"]
    )
    os_image: Optional[StrictStr] = Field(
        None, description="Operating system image used on the node.", examples=["Ubuntu 22.04.3 LTS"]
    )
    system_uuid: Optional[StrictStr] = Field(
        None,
        description="Universal unique identifier of the system.",
        examples=["ec22bcec-e328-8e3a-08d7-b7ce4b0742c1"],
    )


class NetworkInfoItem(DataModelBase):
    """
    NetworkInfoItem object.

    Parameters
    ----------
        interface: Optional[StrictStr]
        ipv4: Optional[List[StrictStr]]
        ipv6: Optional[List[StrictStr]]
        dns: Optional[List[StrictStr]]

    """

    interface: Optional[StrictStr] = None
    ipv4: Optional[List[StrictStr]] = None
    ipv6: Optional[List[StrictStr]] = None
    dns: Optional[List[StrictStr]] = None


class OrchestrationClustersNodesGet(DataModelBase):
    """
    OrchestrationClustersNodesGet object.

    Parameters
    ----------
        capacity: Optional[type.NodeCapacity]
        conditions: Optional[List[OrchestrationClustersNodesGetConditionItem]]
        created: Optional[datetime]
        hostname: Optional[StrictStr]
        internal_ip: Optional[StrictStr]
        k8s_version: Optional[StrictStr]
        labels: Optional[Dict[str, StrictStr]]
        last_seen: Optional[datetime]
        main: Optional[StrictBool]
        name: Optional[StrictStr]
        network_info: Optional[List[NetworkInfoItem]]
        status: Optional[enum.OrchestrationNodeStatus]
        system_info: Optional[OrchestrationClustersNodesGetSystemInfo]
        updated: Optional[datetime]
        warnings: Optional[Dict[str, Any]]

    """

    capacity: Optional[type.NodeCapacity] = None
    conditions: Optional[List[OrchestrationClustersNodesGetConditionItem]] = Field(
        None, description="Detailed information about the Node's telemetry."
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Node was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    hostname: Optional[StrictStr] = Field(
        None,
        description="Name of a computer hosting Node. This name identifies the computer on the network.",
        examples=["node01"],
    )
    internal_ip: Optional[StrictStr] = Field(
        None,
        description="Internal IP address of the computer. It's a unique address within the local network, typically starting with 192.168, 10, or 172.16 to 172.31.",
        examples=["192.168.1.10"],
    )
    k8s_version: Optional[StrictStr] = Field(
        None, description="Current version of k8s installed on the Cluster.", examples=["v1.24.10+k3s1"]
    )
    labels: Optional[Dict[str, StrictStr]] = Field(
        None,
        description="Labels assigned to the Node.",
        examples=[
            {
                "kubernetes.io/os": "linux",
                "node-role.kubernetes.io/control-plane": "true",
                "node-role.kubernetes.io/master": "true",
                "node.kubernetes.io/role": "acp",
            }
        ],
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Node was last seen by the Cloud, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    main: Optional[StrictBool] = Field(
        None, description="Whether the Node is the Master Node in the Cluster.", examples=[True]
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Node.", examples=["aws-cluster-node-01"]
    )
    network_info: Optional[List[NetworkInfoItem]] = Field(
        None,
        description="Details about the Node's current network settings.",
        examples=[
            [{"dns": [""], "interface": "ens5", "ipv4": ["172.31.40.200"], "ipv6": ["fe80::10d3:f3ff:fe1b:bea1"]}]
        ],
    )
    status: Optional[enum.OrchestrationNodeStatus] = None
    system_info: Optional[OrchestrationClustersNodesGetSystemInfo] = None
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Node keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    warnings: Optional[Dict[str, Any]] = Field(
        None,
        description="Any warning messages received from Kubernetes.",
        examples=[
            "container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized"
        ],
    )


class ServiceItem(DataModelBase):
    """
    ServiceItem object.

    Parameters
    ----------
        address: Optional[StrictStr]
        created: Optional[datetime]
        name: Optional[StrictStr]
        network_interface: Optional[StrictStr]
        service_type: Optional[enum.ServiceType]
        updated: Optional[datetime]
        workload_name: Optional[StrictStr]

    """

    address: Optional[StrictStr] = Field(
        None, description="Address and port to connect to the Service.", examples=["opcua-se-0298b03c3fdbbe0.app:4842"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Service was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Service.", examples=["opcua-se-0298b03c3fdbbe0"]
    )
    network_interface: Optional[StrictStr] = Field(
        None, description="Physical network interface name of the Node hosting the Service.", examples=["kelvin"]
    )
    service_type: Optional[enum.ServiceType] = None
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Service keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    workload_name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Node.", examples=["opcua-se-0298b03c3fdbbe0"]
    )


class OrchestrationClustersServiceListPaginatedResponseCursor(PaginatorDataModel[ServiceItem]):
    """
    OrchestrationClustersServiceListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ServiceItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ServiceItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Nodes and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class OrchestrationClustersServiceListPaginatedResponseLimits(PaginatorDataModel[ServiceItem]):
    """
    OrchestrationClustersServiceListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ServiceItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ServiceItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Nodes and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class OrchestrationClustersServiceListPaginatedResponseStream(ServiceItem):
    """
    OrchestrationClustersServiceListPaginatedResponseStream object.

    Parameters
    ----------

    """


class OrchestrationClustersUpdate(OrchestrationCluster):
    """
    OrchestrationClustersUpdate object.

    Parameters
    ----------

    """


class PropertyCreate(PropertyDefinition):
    """
    PropertyCreate object.

    Parameters
    ----------

    """


class PropertyGet(PropertyDefinition):
    """
    PropertyGet object.

    Parameters
    ----------

    """


class PropertiesListPaginatedResponseCursor(PaginatorDataModel[type.PropertyDefinition]):
    """
    PropertiesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.PropertyDefinition]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.PropertyDefinition]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Property objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class PropertiesListPaginatedResponseLimits(PaginatorDataModel[type.PropertyDefinition]):
    """
    PropertiesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.PropertyDefinition]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.PropertyDefinition]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Property objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class PropertiesListPaginatedResponseStream(PropertyDefinition):
    """
    PropertiesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class PropertyUniqueValuesGet(DataModelBase):
    """
    PropertyUniqueValuesGet object.

    Parameters
    ----------
        properties: Optional[Dict[str, List[Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]]]

    """

    properties: Optional[
        Dict[
            str,
            List[
                Union[
                    StrictInt,
                    StrictFloat,
                    StrictStr,
                    StrictBool,
                    List[StrictInt],
                    List[StrictFloat],
                    List[StrictStr],
                    List[StrictBool],
                ]
            ],
        ]
    ] = Field(
        None,
        description="Dictionary containing the `name` of the Asset Property and an array of the associated values.",
        examples=[{"area": ["North", "South", "Central", "Easy", "West"], "fluid-level-high": [200]}],
    )


class PropertyValuesGet(DataModelBase):
    """
    PropertyValuesGet object.

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
        description="List of resources and their current corresponding values for the `property_name`.",
        examples=[{"krn:asset:asset1": 1, "krn:asset:asset2": 2}],
    )


class RangeGetPropertyPaginatedResponseCursor(PaginatorDataModel[type.PropertyValueHistory]):
    """
    RangeGetPropertyPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.PropertyValueHistory]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.PropertyValueHistory]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` historical value objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RangeGetPropertyPaginatedResponseLimits(PaginatorDataModel[type.PropertyValueHistory]):
    """
    RangeGetPropertyPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.PropertyValueHistory]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.PropertyValueHistory]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Property objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RangeGetPropertyPaginatedResponseStream(PropertyValueHistory):
    """
    RangeGetPropertyPaginatedResponseStream object.

    Parameters
    ----------

    """


class RecommendationClustering(DataModelBase):
    """
    RecommendationClustering object.

    Parameters
    ----------
        count: Optional[StrictInt]
        recommendations_ids: Optional[List[UUID]]
        time_bucket_start: Optional[datetime]

    """

    count: Optional[StrictInt] = Field(
        None,
        description="Number of occurrences of Recommendations over the time period of `time_bucket` that meet the request parameters starting from time `time_bucket_start`.",
        examples=[2],
    )
    recommendations_ids: Optional[List[UUID]] = Field(
        None,
        description="An array of Recommendation `id`'s that have been counted.",
        examples=[["0002bc79-b42f-461b-95d6-cf0a28ba87aa", "518bcb79-ffaa-4d3f-8042-52634c34b71e"]],
    )
    time_bucket_start: Optional[datetime] = Field(
        None,
        description="Time of the start of the count for the current `time_bucket` period in RFC 3339 UTC date/time format.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class RecommendationCreate(RecommendationBase):
    """
    RecommendationCreate object.

    Parameters
    ----------
        actions: Optional[type.RecommendationActionsCreate]
        state: Optional[enum.RecommendationStateCreate]
        id: Optional[UUID]
        type_title: Optional[StrictStr]
        created: Optional[datetime]
        source: Optional[KRN]
        updated: Optional[datetime]
        updated_by: Optional[KRN]

    """

    actions: Optional[type.RecommendationActionsCreate] = None
    state: Optional[enum.RecommendationStateCreate] = Field(None, description="Current `state` of the Recommendation.")
    id: Optional[UUID] = Field(
        None,
        description="A unique randomly generated UUID as the key `id` for the Recommendation.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    type_title: Optional[StrictStr] = Field(
        None,
        description="The Recommendation Type `title` associated with the Recommendation.",
        examples=["Decrease Speed"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Recommendation was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    source: Optional[KRN] = Field(
        None,
        description="The process that created this Recommendation. This can be a user or an automated process like a workload, application, etc.",
        examples=["krn:wlappv:cluster1/app1/1.2.0"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Recommendation keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated_by: Optional[KRN] = Field(
        None,
        description="The process that last updated this Recommendation. This can be a user or an automated process like a workload, application, etc.",
        examples=["krn:wlappv:cluster1/app1/1.2.0"],
    )


class RecommendationLastGetPaginatedResponseCursor(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationLastGetPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Last Recommendation for each Asset and its associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RecommendationLastGetPaginatedResponseLimits(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationLastGetPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Last Recommendation for each Asset and its associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RecommendationLastGetPaginatedResponseStream(Recommendation):
    """
    RecommendationLastGetPaginatedResponseStream object.

    Parameters
    ----------

    """


class RecommendationsListPaginatedResponseCursor(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendations and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RecommendationsListPaginatedResponseLimits(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendations and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RecommendationsListPaginatedResponseStream(Recommendation):
    """
    RecommendationsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class RecommendationRangeGetPaginatedResponseCursor(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationRangeGetPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendation for each Asset and its associated context objects over the time range, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RecommendationRangeGetPaginatedResponseLimits(PaginatorDataModel[type.Recommendation]):
    """
    RecommendationRangeGetPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.Recommendation]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.Recommendation]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendations for each Asset and its associated context objects over the time range for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RecommendationRangeGetPaginatedResponseStream(Recommendation):
    """
    RecommendationRangeGetPaginatedResponseStream object.

    Parameters
    ----------

    """


class RecommendationTypeCreate(RecommendationType):
    """
    RecommendationTypeCreate object.

    Parameters
    ----------

    """


class RecommendationTypesListPaginatedCursor(PaginatorDataModel[type.RecommendationType]):
    """
    RecommendationTypesListPaginatedCursor object.

    Parameters
    ----------
        data: Optional[List[type.RecommendationType]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.RecommendationType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendation Types and associated context objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RecommendationTypesListPaginatedLimits(PaginatorDataModel[type.RecommendationType]):
    """
    RecommendationTypesListPaginatedLimits object.

    Parameters
    ----------
        data: Optional[List[type.RecommendationType]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.RecommendationType]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Recommendation Types and associated context objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RecommendationTypesListPaginatedStream(RecommendationType):
    """
    RecommendationTypesListPaginatedStream object.

    Parameters
    ----------

    """


class RecommendationTypeGet(RecommendationType):
    """
    RecommendationTypeGet object.

    Parameters
    ----------

    """


class RecommendationTypeUpdate(RecommendationType):
    """
    RecommendationTypeUpdate object.

    Parameters
    ----------

    """


class RecommendationGet(Recommendation):
    """
    RecommendationGet object.

    Parameters
    ----------

    """


class SecretCreate(DataModelBase):
    """
    SecretCreate object.

    Parameters
    ----------
        name: Optional[StrictStr]
        created: Optional[datetime]
        created_by: Optional[StrictStr]
        updated: Optional[datetime]
        updated_by: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Secret. The string can only contain lowercase alphanumeric characters and `-` characters.",
        examples=["secret-password"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    created_by: Optional[StrictStr] = Field(
        None, description="Name of the user that created the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    updated_by: Optional[StrictStr] = Field(
        None, description="Name of the user that updated the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )


class SecretItem(DataModelBase):
    """
    SecretItem object.

    Parameters
    ----------
        name: Optional[StrictStr]
        created: Optional[datetime]
        created_by: Optional[StrictStr]
        updated: Optional[datetime]
        updated_by: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Secret. The string can only contain lowercase alphanumeric characters and `-` characters.",
        examples=["secret-password"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    created_by: Optional[StrictStr] = Field(
        None, description="Name of the user that created the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    updated_by: Optional[StrictStr] = Field(
        None, description="Name of the user that updated the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )


class SecretsListPaginatedResponseCursor(PaginatorDataModel[SecretItem]):
    """
    SecretsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[SecretItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[SecretItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Secret objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class SecretsListPaginatedResponseLimits(PaginatorDataModel[SecretItem]):
    """
    SecretsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[SecretItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[SecretItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Secret objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class SecretsListPaginatedResponseStream(SecretItem):
    """
    SecretsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class SecretUpdate(DataModelBase):
    """
    SecretUpdate object.

    Parameters
    ----------
        name: Optional[StrictStr]
        created: Optional[datetime]
        created_by: Optional[StrictStr]
        updated: Optional[datetime]
        updated_by: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Secret. The string can only contain lowercase alphanumeric characters and `-` characters.",
        examples=["secret-password"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    created_by: Optional[StrictStr] = Field(
        None, description="Name of the user that created the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Secret was first updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    updated_by: Optional[StrictStr] = Field(
        None, description="Name of the user that updated the Secret.", examples=[["krn:user:person@kelvin.ai"]]
    )


class TimeseriesLastGet(TimeseriesData):
    """
    TimeseriesLastGet object.

    Parameters
    ----------

    """


class TimeseriesListPaginatedResponseCursor(PaginatorDataModel[type.TimeseriesData]):
    """
    TimeseriesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.TimeseriesData]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.TimeseriesData]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Time Series objects, starting from the index specified by the pagination parameters. Each object is a separate last value that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class TimeseriesListPaginatedResponseLimits(PaginatorDataModel[type.TimeseriesData]):
    """
    TimeseriesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.TimeseriesData]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.TimeseriesData]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Time Series objects for the page number specified by the pagination parameters. Each object is a separate last value that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class TimeseriesListPaginatedResponseStream(TimeseriesData):
    """
    TimeseriesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class TimeseriesRangeGet(DataModelBase):
    """
    TimeseriesRangeGet object.

    Parameters
    ----------
        payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        resource: Optional[KRN]
        timestamp: Optional[datetime]

    """

    payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None, description="Raw or aggregate value for `resource` at the specified `timestamp`."
    )
    resource: Optional[KRN] = Field(
        None,
        description="The `resource` (Asset / Data Stream pair) associated with the `payload`.",
        examples=["krn:ad:asset1/data_stream1"],
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="UTC time when the `payload` values were saved, formatted in RFC 3339.",
        examples=["2023-11-13T12:00:00Z"],
    )


class UserItem(DataModelBase):
    """
    UserItem object.

    Parameters
    ----------
        created: Optional[datetime]
        email: Optional[EmailStr]
        first_name: Optional[StrictStr]
        id: Optional[UUID]
        last_name: Optional[StrictStr]
        username: Optional[StrictStr]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the User was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    email: Optional[EmailStr] = Field(None, description="Email of the user.", examples=["john.doe@kelvin.ai"])
    first_name: Optional[StrictStr] = Field(None, description="First name of the User.", examples=["John"])
    id: Optional[UUID] = Field(
        None,
        description="A unique randomly generated UUID as the key `id` for the User.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    last_name: Optional[StrictStr] = Field(None, description="Last name of the User.", examples=["Doe"])
    username: Optional[StrictStr] = Field(None, description="Username of the User.", examples=["johndoe"])


class UsersListPaginatedResponseCursor(PaginatorDataModel[UserItem]):
    """
    UsersListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[UserItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[UserItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` User objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class UsersListPaginatedResponseLimits(PaginatorDataModel[UserItem]):
    """
    UsersListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[UserItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[UserItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` User objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class UsersListPaginatedResponseStream(UserItem):
    """
    UsersListPaginatedResponseStream object.

    Parameters
    ----------

    """


class Permission(BaseModelRoot[StrictStr]):
    root: StrictStr


class UserMeGet(DataModelBase):
    """
    UserMeGet object.

    Parameters
    ----------
        created: Optional[datetime]
        email: Optional[EmailStr]
        first_name: Optional[StrictStr]
        id: Optional[UUID]
        last_name: Optional[StrictStr]
        permissions: Optional[List[Permission]]
        groups: Optional[List[StrictStr]]
        username: Optional[StrictStr]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the current User was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    email: Optional[EmailStr] = Field(None, description="Email of the current user.", examples=["john.doe@kelvin.ai"])
    first_name: Optional[StrictStr] = Field(None, description="First name of the current User.", examples=["John"])
    id: Optional[UUID] = Field(
        None,
        description="A unique randomly generated UUID as the key `id` for the current User.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    last_name: Optional[StrictStr] = Field(None, description="Last name of the current User.", examples=["Doe"])
    permissions: Optional[List[Permission]] = Field(
        None,
        description="Lists all Instance permissions accessible to the current User.",
        examples=[["kelvin.permission.bridge.update", "kelvin.permission.asset.delete"]],
    )
    groups: Optional[List[StrictStr]] = Field(
        None, description="Lists of all groups the current User belongs to.", examples=[["my_group"]]
    )
    username: Optional[StrictStr] = Field(None, description="Username of the current User.", examples=["johndoe"])


class UserSettingsListPaginatedResponseCursor(PaginatorDataModel[type.UserSetting]):
    """
    UserSettingsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.UserSetting]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.UserSetting]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` User Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class UserSettingsListPaginatedResponseLimits(PaginatorDataModel[type.UserSetting]):
    """
    UserSettingsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.UserSetting]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.UserSetting]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` User Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class UserSettingsListPaginatedResponseStream(UserSetting):
    """
    UserSettingsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class UserSettingsGet(UserSetting):
    """
    UserSettingsGet object.

    Parameters
    ----------

    """


class UserSettingsUpdate(UserSetting):
    """
    UserSettingsUpdate object.

    Parameters
    ----------

    """


class UserGet(DataModelBase):
    """
    UserGet object.

    Parameters
    ----------
        created: Optional[datetime]
        email: Optional[EmailStr]
        first_name: Optional[StrictStr]
        id: Optional[UUID]
        last_name: Optional[StrictStr]
        username: Optional[StrictStr]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the User was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    email: Optional[EmailStr] = Field(None, description="Email of the user.", examples=["john.doe@kelvin.ai"])
    first_name: Optional[StrictStr] = Field(None, description="First name of the User.", examples=["John"])
    id: Optional[UUID] = Field(
        None,
        description="A unique randomly generated UUID as the key `id` for the User.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    last_name: Optional[StrictStr] = Field(None, description="Last name of the User.", examples=["Doe"])
    username: Optional[StrictStr] = Field(None, description="Username of the User.", examples=["johndoe"])


class SharedSettingsUpdate(SharedSetting):
    """
    SharedSettingsUpdate object.

    Parameters
    ----------

    """


class SharedSettingsGet(SharedSetting):
    """
    SharedSettingsGet object.

    Parameters
    ----------

    """


class SharedSettingsListPaginatedResponseCursor(PaginatorDataModel[type.SharedSetting]):
    """
    SharedSettingsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[type.SharedSetting]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[type.SharedSetting]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Shared Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class SharedSettingsListPaginatedResponseLimits(PaginatorDataModel[type.SharedSetting]):
    """
    SharedSettingsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[type.SharedSetting]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[type.SharedSetting]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Shared Setting objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class SharedSettingsListPaginatedResponseStream(SharedSetting):
    """
    SharedSettingsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class Role(DataModelBase):
    """
    Role object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Role.", examples=["my_role"])
    title: Optional[StrictStr] = Field(None, description="The title of the Role.", examples=["My Role"])


class Group(DataModelBase):
    """
    Group object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        roles: Optional[List[Role]]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Group.", examples=["my_group"])
    title: Optional[StrictStr] = Field(None, description="The title of the Group.", examples=["My Group"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Group.          ", examples=["This is my group"]
    )
    roles: Optional[List[Role]] = Field(None, description="A list of role objects that the group belongs to.")
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Group was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Group was last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class GroupCreate(Group):
    """
    GroupCreate object.

    Parameters
    ----------

    """


class GroupItem(DataModelBase):
    """
    GroupItem object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Group.", examples=["my_group"])
    title: Optional[StrictStr] = Field(None, description="The title of the Group.", examples=["My Group"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Group.          ", examples=["This is my group"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Group was created, formatted in RFC 3339.          ",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Group was last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class GroupsListPaginatedResponseCursor(PaginatorDataModel[GroupItem]):
    """
    GroupsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[GroupItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[GroupItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Group objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class GroupsListPaginatedResponseLimits(PaginatorDataModel[GroupItem]):
    """
    GroupsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[GroupItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[GroupItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Group objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class GroupsListPaginatedResponseStream(GroupItem):
    """
    GroupsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class GroupGet(Group):
    """
    GroupGet object.

    Parameters
    ----------

    """


class GroupUpdate(Group):
    """
    GroupUpdate object.

    Parameters
    ----------

    """


class GroupModel(DataModelBase):
    """
    GroupModel object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Group.", examples=["my_group"])
    title: Optional[StrictStr] = Field(None, description="The title of the Group.", examples=["My Group"])


class RoleModel(DataModelBase):
    """
    RoleModel object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        groups: Optional[List[GroupModel]]
        updated: Optional[datetime]
        created: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Role.", examples=["my_role"])
    title: Optional[StrictStr] = Field(None, description="The title of the Role.", examples=["My Role"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Role.", examples=["This is my role"]
    )
    groups: Optional[List[GroupModel]] = Field(None, description="A list of group objects that the role belongs to.")
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Role was last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Role was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class RoleCreate(RoleModel):
    """
    RoleCreate object.

    Parameters
    ----------

    """


class PolicyName(BaseModelRoot[StrictStr]):
    root: StrictStr = Field(..., description="The name of the Policy.", examples=["my_policy"])


class RoleItem(DataModelBase):
    """
    RoleItem object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        policy_names: Optional[List[PolicyName]]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Role.", examples=["my_role"])
    title: Optional[StrictStr] = Field(None, description="The title of the Role.", examples=["My Role"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Role.", examples=["This is my role"]
    )
    policy_names: Optional[List[PolicyName]] = None
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Role was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Role was last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class RolesListPaginatedResponseCursor(PaginatorDataModel[RoleItem]):
    """
    RolesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[RoleItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[RoleItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Role objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RolesListPaginatedResponseLimits(PaginatorDataModel[RoleItem]):
    """
    RolesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[RoleItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[RoleItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Role objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RolesListPaginatedResponseStream(RoleItem):
    """
    RolesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class RoleGet(RoleModel):
    """
    RoleGet object.

    Parameters
    ----------

    """


class RoleUpdate(RoleModel):
    """
    RoleUpdate object.

    Parameters
    ----------

    """


class Rule(DataModelBase):
    """
    Rule object.

    Parameters
    ----------
        actions: Optional[List[enum.RolePolicyAction]]
        condition: Optional[type.RolePolicyCondition]

    """

    actions: Optional[List[enum.RolePolicyAction]] = None
    condition: Optional[type.RolePolicyCondition] = None


class RolePolicy(DataModelBase):
    """
    RolePolicy object.

    Parameters
    ----------
        name: Optional[StrictStr]
        resource_type: Optional[enum.ResourceType]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        rule: Optional[Rule]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the Policy.", examples=["my_policy"])
    resource_type: Optional[enum.ResourceType] = Field(
        None, description="The resource_type to which the policy applies.", examples=["asset"]
    )
    title: Optional[StrictStr] = Field(None, description="The title of the Policy.", examples=["My Policy"])
    description: Optional[StrictStr] = Field(
        None, description="The description of the Policy.", examples=["This is my policy"]
    )
    rule: Optional[Rule] = None
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Policy was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the Policy was last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class RolePolicyCreate(RolePolicy):
    """
    RolePolicyCreate object.

    Parameters
    ----------

    """


class RolePoliciesListPaginatedResponseCursor(PaginatorDataModel[RolePolicy]):
    """
    RolePoliciesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[RolePolicy]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[RolePolicy]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Role Policy objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class RolePoliciesListPaginatedResponseLimits(PaginatorDataModel[RolePolicy]):
    """
    RolePoliciesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[RolePolicy]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[RolePolicy]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Role Policy objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class RolePoliciesListPaginatedResponseStream(RolePolicy):
    """
    RolePoliciesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class RolePolicyGet(RolePolicy):
    """
    RolePolicyGet object.

    Parameters
    ----------

    """


class RolePolicyUpdate(RolePolicy):
    """
    RolePolicyUpdate object.

    Parameters
    ----------

    """


class LegacyAppCreate(LegacyApp):
    """
    LegacyAppCreate object.

    Parameters
    ----------

    """


class ErrorMessage(DataModelBase):
    """
    ErrorMessage object.

    Parameters
    ----------
        error_code: Optional[StrictInt]
        http_status_code: Optional[StrictInt]
        message: Optional[List[StrictStr]]
        type: Optional[enum.ErrorLegacyType]

    """

    error_code: Optional[StrictInt] = Field(
        None, description="Internal Kelvin error code (used for internal purposes).", examples=[32]
    )
    http_status_code: Optional[StrictInt] = Field(None, description="HTTP status error code.", examples=["4XX"])
    message: Optional[List[StrictStr]] = Field(
        None, description="Detailed description of the error.", examples=[["Detailed information about the error."]]
    )
    type: Optional[enum.ErrorLegacyType] = None


class LegacyAppItem(DataModelBase):
    """
    LegacyAppItem object.

    Parameters
    ----------
        created: Optional[datetime]
        description: Optional[StrictStr]
        latest_version: Optional[StrictStr]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        type: Optional[enum.LegacyAppType]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the App was first uploaded to the App Registry, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    description: Optional[StrictStr] = Field(
        None,
        description="Description of the App in the App Registry.",
        examples=[
            """This application controls the speed of the beam pump motor in order to increase production for this type of artificial lift well. It uses values available from the control system such as Downhole Pressure, Motor Speed, Motor Torque and Choke position.
"""
        ],
    )
    latest_version: Optional[StrictStr] = Field(
        None, description="Latest version number of the App in the App Registry.", examples=["1.2.0"]
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the App in the App Registry.", examples=["motor-speed-control"]
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the App in the App Registry.", examples=["Motor Speed Control"]
    )
    type: Optional[enum.LegacyAppType] = Field(
        None,
        description="Type of development used for the App. `kelvin` is Kelvin App using Python and `docker` is using the generic Dockerfile format.",
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any App keys in the App Registry were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )


class LegacyAppRegistryAppsListPaginatedResponseCursor(PaginatorDataModel[LegacyAppItem]):
    """
    LegacyAppRegistryAppsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[LegacyAppItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[LegacyAppItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Type objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class LegacyAppRegistryAppsListPaginatedResponseLimits(PaginatorDataModel[LegacyAppItem]):
    """
    LegacyAppRegistryAppsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[LegacyAppItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[LegacyAppItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Data Type objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class LegacyAppRegistryAppsListPaginatedResponseStream(LegacyAppItem):
    """
    LegacyAppRegistryAppsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class LegacyAppRegistryAppGet(LegacyApp):
    """
    LegacyAppRegistryAppGet object.

    Parameters
    ----------

    """


class LegacyAppUpdate(LegacyApp):
    """
    LegacyAppUpdate object.

    Parameters
    ----------

    """


class LegacyAppVersionGet(LegacyAppVersion):
    """
    LegacyAppVersionGet object.

    Parameters
    ----------

    """


class BridgeDeploy(Bridge):
    """
    BridgeDeploy object.

    Parameters
    ----------

    """


class BridgeItem(DataModelBase):
    """
    BridgeItem object.

    Parameters
    ----------
        cluster_name: Optional[StrictStr]
        created: Optional[datetime]
        enabled: Optional[StrictBool]
        name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        status: Optional[type.WorkloadStatus]
        title: Optional[StrictStr]
        updated: Optional[datetime]
        workload_name: Optional[StrictStr]
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]

    """

    cluster_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Cluster.", examples=["docs-demo-cluster-k3s"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Bridge (Connection) was first created, formatted in RFC 3339.",
        examples=["2023-12-26T18:22:18.582724Z"],
    )
    enabled: Optional[StrictBool] = Field(
        None,
        description="If true, Bridge (Connection) `status` is set to `running` and will process I/O's. If false, Bridge (Connection) `status` is set to `stopped` but remains in Node on the Edge System.",
        examples=[True],
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Bridge (Connection).",
        examples=["motor-plc-opcua-connection"],
    )
    node_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Node in the Cluster hosting the Bridge (Connection).",
        examples=["docs-demo-node-01"],
    )
    status: Optional[type.WorkloadStatus] = None
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Bridge (Connection).", examples=["Motor PLC OPCUA Connection"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Bridge (Connection) keys were last updated, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    workload_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Workload that the Bridge (Connection) App is deployed as to the Cluster.",
        examples=["motor-plc-opcua-connection"],
    )
    app_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the App. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["test-app"],
    )
    app_version: Optional[StrictStr] = Field(None, description="App version", examples=["1.2.0"])


class BridgesListPaginatedResponseCursor(PaginatorDataModel[BridgeItem]):
    """
    BridgesListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[BridgeItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[BridgeItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Bridge (Connection) objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class BridgesListPaginatedResponseLimits(PaginatorDataModel[BridgeItem]):
    """
    BridgesListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[BridgeItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[BridgeItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Bridge (Connection) objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class BridgesListPaginatedResponseStream(BridgeItem):
    """
    BridgesListPaginatedResponseStream object.

    Parameters
    ----------

    """


class BridgeGet(Bridge):
    """
    BridgeGet object.

    Parameters
    ----------

    """


class ParameterDefinitionItem(DataModelBase):
    """
    ParameterDefinitionItem object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        created: Optional[datetime]
        last_title: Optional[StrictStr]
        name: Optional[StrictStr]
        primitive_type: Optional[enum.ParameterType]
        updated: Optional[datetime]

    """

    app_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the App in the App Registry linked to this Paramete Definition.",
        examples=["motor-speed-control"],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Parameter Definition was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    last_title: Optional[StrictStr] = Field(
        None,
        description="Latest Display name (`title`) of the Parameter in the App.",
        examples=["Gas Flow Max Threshold"],
    )
    name: Optional[StrictStr] = Field(
        None, description="The name of the Parameter.", examples=["gas_flow_rate_max_threshold"]
    )
    primitive_type: Optional[enum.ParameterType] = None
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Parameter Definition keys were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )


class ParametersDefinitionsListPaginatedResponseCursor(PaginatorDataModel[ParameterDefinitionItem]):
    """
    ParametersDefinitionsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ParameterDefinitionItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ParameterDefinitionItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter Definition objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ParametersDefinitionsListPaginatedResponseLimits(PaginatorDataModel[ParameterDefinitionItem]):
    """
    ParametersDefinitionsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ParameterDefinitionItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ParameterDefinitionItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter Definition objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ParametersDefinitionsListPaginatedResponseStream(ParameterDefinitionItem):
    """
    ParametersDefinitionsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class ParameterValueHistorianItem(DataModelBase):
    """
    ParameterValueHistorianItem object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]
        comment: Optional[StrictStr]
        created: Optional[datetime]
        parameter_name: Optional[StrictStr]
        resource: Optional[KRN]
        source: Optional[KRN]
        updated: Optional[datetime]
        value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        invalidated: Optional[datetime]

    """

    app_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the App in the App Registry linked to this Parameter.",
        examples=["motor-speed-control"],
    )
    app_version: Optional[StrictStr] = Field(
        None, description="Version number of the App in the App Registry linked to this Parameter.", examples=["1.2.0"]
    )
    comment: Optional[StrictStr] = Field(
        None,
        description="Latest information from user when creating or updating this Parameter.",
        examples=["updating parameter for well operational optimization."],
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Parameter was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    parameter_name: Optional[StrictStr] = Field(
        None, description="The name of the Parameter.", examples=["gas_flow_rate_max_threshold"]
    )
    resource: Optional[KRN] = Field(
        None, description="The target Asset to which the parameters are to be applied.", examples=["krn:asset:well_01"]
    )
    source: Optional[KRN] = Field(
        None,
        description="KRN of the User or Service that last created or updated the Parameter.",
        examples=["krn:user:richard.teo@kelvininc.com"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Parameter keys were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None,
        description="The current value of the Parameter. The format returned will depend on the Primitive Type of the Parameter.",
        examples=[100],
    )
    invalidated: Optional[datetime] = Field(
        None,
        description="UTC time when any Parameter value were invalidated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )


class ResourceParametersListPaginatedResponseCursor(PaginatorDataModel[ParameterValueHistorianItem]):
    """
    ResourceParametersListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[ParameterValueHistorianItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[ParameterValueHistorianItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter objects and its current value for the related Resource, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class ResourceParametersListPaginatedResponseLimits(PaginatorDataModel[ParameterValueHistorianItem]):
    """
    ResourceParametersListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[ParameterValueHistorianItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[ParameterValueHistorianItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Parameter objects and its current value for the related Resource for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class ResourceParametersListPaginatedResponseStream(ParameterValueHistorianItem):
    """
    ResourceParametersListPaginatedResponseStream object.

    Parameters
    ----------

    """


class ParametersValuesGet(DataModelBase):
    """
    ParametersValuesGet object.

    Parameters
    ----------
        app_parameter_values: Optional[Dict[str, Dict[str, List[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]]]]

    """

    app_parameter_values: Optional[
        Dict[str, Dict[str, List[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]]]
    ] = Field(
        None,
        description="Collection of objects where each object is an App containing an array of values for each Parameter that meets the request filter definitions. Only unique Parameter Values are shown, default values will not be shown.",
        examples=[
            {
                "cp-temperature-producer": {"temperature_max_in_celsius": [111], "temperature_min_in_celsius": [69]},
                "demo-model": {"recommended_speed_setpoint": [120, 150, 90]},
            }
        ],
    )


class LegacyWorkloadDeploy(LegacyWorkload):
    """
    LegacyWorkloadDeploy object.

    Parameters
    ----------

    """


class Staged(DataModelBase):
    """
    Staged object.

    Parameters
    ----------
        ready: Optional[StrictBool]
        app_version: Optional[StrictStr]
        status: Optional[type.StagedStatus]

    """

    ready: Optional[StrictBool] = Field(None, description="Staged workload ready to be applied.", examples=[True])
    app_version: Optional[StrictStr] = Field(
        None, description="Version Number of the Kelvin App used for the Staged Workload.", examples=["1.2.0"]
    )
    status: Optional[type.StagedStatus] = None


class LegacyWorkloadItem(DataModelBase):
    """
    LegacyWorkloadItem object.

    Parameters
    ----------
        acp_name: Optional[StrictStr]
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]
        cluster_name: Optional[StrictStr]
        created: Optional[datetime]
        download_status: Optional[enum.WorkloadDownloadStatus]
        download_error: Optional[StrictStr]
        enabled: Optional[StrictBool]
        instantly_apply: Optional[StrictBool]
        name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        pre_download: Optional[StrictBool]
        status: Optional[type.LegacyWorkloadStatus]
        title: Optional[StrictStr]
        updated: Optional[datetime]
        staged: Optional[Staged]

    """

    acp_name: Optional[StrictStr] = Field(
        None, description="[`Deprecated`] Unique identifier `name` of the Cluster.", examples=["docs-demo-cluster-k3s"]
    )
    app_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Kelvin App in the App Registry.",
        examples=["motor-speed-control"],
    )
    app_version: Optional[StrictStr] = Field(
        None, description="Version Number of the Kelvin App used for this Workload.", examples=["1.2.0"]
    )
    cluster_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Cluster.", examples=["docs-demo-cluster-k3s"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Workload was first created, formatted in RFC 3339.",
        examples=["2023-12-26T18:22:18.582724Z"],
    )
    download_status: Optional[enum.WorkloadDownloadStatus] = None
    download_error: Optional[StrictStr] = Field(
        None,
        description="Simple description of the error in case the image download failed.",
        examples=["an error occurred while saving the image"],
    )
    enabled: Optional[StrictBool] = Field(
        None,
        description="If true, Workload `status` is set to `running` and will process I/O's. If false, Workload `status` is set to `stopped` but remains in Node on the Edge System.",
        examples=[True],
    )
    instantly_apply: Optional[StrictBool] = Field(
        None,
        description="If true, applies deploy/upgrade immediately. If false, user will need to send an additional API request `/workloads/{workload_name}/apply` to initate the deploy/upgrade.",
        examples=[True],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Workload.", examples=["motor-speed-control-ubdhwnshdy67"]
    )
    node_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Node in the Cluster hosting the Workload.",
        examples=["docs-demo-node-01"],
    )
    pre_download: Optional[StrictBool] = Field(
        None,
        description="If true, deploy process is handled by Kelvin and all Workloads wil be downloaded to Edge System before deploy. If false, deploy process is handled by Kubernetes through default settings.",
        examples=[True],
    )
    status: Optional[type.LegacyWorkloadStatus] = None
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Workload.", examples=["Motor Speed Control"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Workload keys were last updated, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    staged: Optional[Staged] = None


class LegacyWorkloadsListPaginatedResponseCursor(PaginatorDataModel[LegacyWorkloadItem]):
    """
    LegacyWorkloadsListPaginatedResponseCursor object.

    Parameters
    ----------
        data: Optional[List[LegacyWorkloadItem]]
        pagination: Optional[PaginationCursor]

    """

    data: Optional[List[LegacyWorkloadItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Workload objects, starting from the index specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationCursor] = None


class LegacyWorkloadsListPaginatedResponseLimits(PaginatorDataModel[LegacyWorkloadItem]):
    """
    LegacyWorkloadsListPaginatedResponseLimits object.

    Parameters
    ----------
        data: Optional[List[LegacyWorkloadItem]]
        pagination: Optional[PaginationLimits]

    """

    data: Optional[List[LegacyWorkloadItem]] = Field(
        None,
        description="A dictionary with a data property that contains an array of up to `page_size` Workload objects for the page number specified by the pagination parameters, that matches the query parameters.",
    )
    pagination: Optional[PaginationLimits] = None


class LegacyWorkloadsListPaginatedResponseStream(LegacyWorkloadItem):
    """
    LegacyWorkloadsListPaginatedResponseStream object.

    Parameters
    ----------

    """


class LegacyWorkloadConfigurationGet(DataModelBase):
    """
    LegacyWorkloadConfigurationGet object.

    Parameters
    ----------
        configuration: Optional[Dict[str, Any]]

    """

    configuration: Optional[Dict[str, Any]] = None


class LegacyWorkloadConfigurationUpdate(DataModelBase):
    """
    LegacyWorkloadConfigurationUpdate object.

    Parameters
    ----------
        configuration: Optional[Dict[str, Any]]

    """

    configuration: Optional[Dict[str, Any]] = None


class LegacyWorkloadDownload(DataModelBase):
    """
    LegacyWorkloadDownload object.

    Parameters
    ----------
        url: Optional[StrictStr]
        expires_in: Optional[StrictInt]

    """

    url: Optional[StrictStr] = Field(None, description="URL to download the Workload package file.")
    expires_in: Optional[StrictInt] = Field(None, description="Time in seconds before the URL expires.")


class LegacyWorkloadGet(LegacyWorkload):
    """
    LegacyWorkloadGet object.

    Parameters
    ----------

    """


class LegacyWorkloadLogsGet(DataModelBase):
    """
    LegacyWorkloadLogsGet object.

    Parameters
    ----------
        logs: Optional[Dict[str, List[StrictStr]]]

    """

    logs: Optional[Dict[str, List[StrictStr]]] = Field(
        None,
        examples=[
            {
                "bp-opcua-bridge-0": [
                    '2023-12-20T13:57:38.466076008Z {"asset":"bp_33","event":"Casted message from Float64 variant"}',
                    '2023-12-20T13:57:38.466198095Z {"event":"[Runtime.cpp: 626:D] - publishing:  choke_position_set_point"}',
                ]
            }
        ],
    )


class ThreadsList(BaseModelRoot[List[type.Thread]]):
    root: List[type.Thread]


class ThreadCreate(Thread):
    """
    ThreadCreate object.

    Parameters
    ----------

    """


class ThreadFollowUpdate(Thread):
    """
    ThreadFollowUpdate object.

    Parameters
    ----------

    """


class ThreadGet(Thread):
    """
    ThreadGet object.

    Parameters
    ----------

    """


class ThreadReplyCreate(Thread):
    """
    ThreadReplyCreate object.

    Parameters
    ----------

    """


class ThreadReplyUpdate(Thread):
    """
    ThreadReplyUpdate object.

    Parameters
    ----------

    """


class ThreadSeenUpdate(Thread):
    """
    ThreadSeenUpdate object.

    Parameters
    ----------

    """


class ThreadUpdate(Thread):
    """
    ThreadUpdate object.

    Parameters
    ----------

    """
