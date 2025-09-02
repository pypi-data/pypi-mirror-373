from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import ConfigDict, Field, RootModel, StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.api.client.base_model import BaseModelRoot
from kelvin.api.client.data_model import DataModelBase
from kelvin.krn import KRN

from . import enum, manifest
from .manifest import AppInfo, AppManifest


class Created(DataModelBase):
    """
    Created object.

    Parameters
    ----------
        created_at: Optional[datetime]
        created_by: Optional[KRN]

    """

    created_at: Optional[datetime] = Field(
        None,
        description="UTC time when the object was created, formatted in RFC 3339.",
        examples=["2024-11-18T18:22:18.582724Z"],
    )
    created_by: Optional[KRN] = Field(None, description="KRN of the user or process that created the object.")


class Updated(DataModelBase):
    """
    Updated object.

    Parameters
    ----------
        updated_at: Optional[datetime]
        updated_by: Optional[KRN]

    """

    updated_at: Optional[datetime] = Field(
        None,
        description="UTC time when any keys were last updated, formatted in RFC 3339.",
        examples=["2024-11-18T18:22:18.582724Z"],
    )
    updated_by: Optional[KRN] = Field(None, description="KRN of the user or process that last updated any of the keys.")


class AppVersion(AppManifest, Created, Updated):
    """
    AppVersion object.

    Parameters
    ----------

    """


class AppDataQuality(DataModelBase):
    """
    AppDataQuality object.

    Parameters
    ----------
        way: Optional[enum.DQWay]
        datastreams: Optional[Dict[str, Dict[str, Any]]]
        configuration: Optional[Dict[str, Any]]

    """

    way: Optional[enum.DQWay] = None
    datastreams: Optional[Dict[str, Dict[str, Any]]] = None
    configuration: Optional[Dict[str, Any]] = None


class Datastreams(DataModelBase):
    """
    Datastreams object.

    Parameters
    ----------
        map_to: Optional[StrictStr]
        configuration: Optional[Dict[str, Any]]
        remote: Optional[StrictBool]
        way: Optional[enum.Way]
        storage: Optional[enum.Storage]

    """

    map_to: Optional[StrictStr] = None
    configuration: Optional[Dict[str, Any]] = None
    remote: Optional[StrictBool] = None
    way: Optional[enum.Way] = None
    storage: Optional[enum.Storage] = None


class Resource(DataModelBase):
    """
    Resource object.

    Parameters
    ----------
        resource: Optional[StrictStr]
        parameters: Optional[Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]]
        datastreams: Optional[Dict[str, Datastreams]]
        data_quality: Optional[Dict[str, AppDataQuality]]

    """

    resource: Optional[StrictStr] = None
    parameters: Optional[
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
    ] = None
    datastreams: Optional[Dict[str, Datastreams]] = None
    data_quality: Optional[Dict[str, AppDataQuality]] = None


class AppDeploymentRuntimeResources(DataModelBase):
    """
    AppDeploymentRuntimeResources object.

    Parameters
    ----------
        resources: Optional[List[Resource]]

    """

    resources: Optional[List[Resource]] = None


class AppDeploymentRuntime(AppDeploymentRuntimeResources):
    """
    AppDeploymentRuntime object.

    Parameters
    ----------
        configuration: Optional[Dict[str, Any]]

    """

    configuration: Optional[Dict[str, Any]] = None


class AppResourceWorkload(DataModelBase):
    """
    AppResourceWorkload object.

    Parameters
    ----------
        app_version: Optional[StrictStr]
        workload_name: Optional[StrictStr]
        cluster_name: Optional[StrictStr]

    """

    app_version: Optional[StrictStr] = None
    workload_name: Optional[StrictStr] = None
    cluster_name: Optional[StrictStr] = None


class AppResource(Created, Updated):
    """
    AppResource object.

    Parameters
    ----------
        resource: Optional[KRN]
        app_name: Optional[StrictStr]
        enabled: Optional[StrictBool]
        workloads: Optional[List[AppResourceWorkload]]

    """

    resource: Optional[KRN] = None
    app_name: Optional[StrictStr] = None
    enabled: Optional[StrictBool] = None
    workloads: Optional[List[AppResourceWorkload]] = None


class AppVersionOnly(Created, Updated):
    """
    AppVersionOnly object.

    Parameters
    ----------
        version: Optional[StrictStr]

    """

    version: Optional[StrictStr] = None


class Deployment(DataModelBase):
    """
    Deployment object.

    Parameters
    ----------
        status: Optional[enum.AppStatus]

    """

    status: Optional[enum.AppStatus] = None


class App(AppInfo, Created, Updated):
    """
    App object.

    Parameters
    ----------
        dashboard_uid: Optional[StrictStr]
        latest_version: Optional[StrictStr]
        versions: Optional[List[AppVersionOnly]]
        deployment: Optional[Deployment]

    """

    dashboard_uid: Optional[StrictStr] = None
    latest_version: Optional[StrictStr] = Field(None, description="The version of the Application that was crated last")
    versions: Optional[List[AppVersionOnly]] = None
    deployment: Optional[Deployment] = None


class AppShort(AppInfo, Created, Updated):
    """
    AppShort object.

    Parameters
    ----------
        dashboard_uid: Optional[StrictStr]
        latest_version: Optional[StrictStr]
        status: Optional[enum.AppStatus]

    """

    dashboard_uid: Optional[StrictStr] = None
    latest_version: Optional[StrictStr] = Field(None, description="The version of the Application that was crated last")
    status: Optional[enum.AppStatus] = None


class AppsResourceContext(DataModelBase):
    """
    AppsResourceContext object.

    Parameters
    ----------
        resource: Optional[KRN]
        source: Optional[KRN]

    """

    resource: Optional[KRN] = None
    source: Optional[KRN] = None


class AppVersionParameter(Created, Updated):
    """
    AppVersionParameter object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]
        comment: Optional[StrictStr]
        created: Optional[datetime]
        name: Optional[StrictStr]
        resource: Optional[KRN]
        value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]

    """

    app_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the App in the App Registry linked to this Parameter."
    )
    app_version: Optional[StrictStr] = Field(
        None, description="Version number of the App in the App Registry linked to this Parameter."
    )
    comment: Optional[StrictStr] = Field(
        None, description="Latest information from user when creating or updating this Parameter."
    )
    created: Optional[datetime] = Field(
        None, description="UTC time when the Parameter was first created, formatted in RFC 3339."
    )
    name: Optional[StrictStr] = Field(None, description="The name of the Parameter.")
    resource: Optional[KRN] = Field(None, description="KRN of the Asset associated with the Parameter.")
    value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None,
        description="The current value of the Parameter. The format returned will depend on the Data Type of the Parameter.",
    )


class AppVersionHistoricParameter(AppVersionParameter):
    """
    AppVersionHistoricParameter object.

    Parameters
    ----------
        invalidated: Optional[datetime]

    """

    invalidated: Optional[datetime] = Field(
        None, description="UTC time when any Parameter value were invalidated, formatted in RFC 3339."
    )


class AppParameter(Created, Updated):
    """
    AppParameter object.

    Parameters
    ----------
        app_name: Optional[StrictStr]
        title: Optional[StrictStr]
        name: Optional[StrictStr]
        data_type: Optional[enum.ParameterType]

    """

    app_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the App in the App Registry linked to this Paramete Definition."
    )
    title: Optional[StrictStr] = Field(None, description="Latest Display name (`title`) of the Parameter in the App.")
    name: Optional[StrictStr] = Field(None, description="The name of the Parameter.")
    data_type: Optional[enum.ParameterType] = None


class ParameterItemNoComment(DataModelBase):
    """
    ParameterItemNoComment object.

    Parameters
    ----------
        name: StrictStr
        value: Union[StrictInt, StrictFloat, StrictStr, StrictBool]

    """

    name: StrictStr = Field(..., description="Parameter name")
    value: Union[StrictInt, StrictFloat, StrictStr, StrictBool]


class ParameterItem(ParameterItemNoComment):
    """
    ParameterItem object.

    Parameters
    ----------
        comment: Optional[StrictStr]

    """

    comment: Optional[StrictStr] = Field(None, description="Comment regarding the parameter change action")


class AppVersionResourceParameters(DataModelBase):
    """
    AppVersionResourceParameters object.

    Parameters
    ----------
        resource: KRN
        parameters: List[ParameterItem]

    """

    resource: KRN = Field(..., description="The target resource to which the parameters are to be applied")
    parameters: List[ParameterItem]


class ParameterScheduleResourceParameter(DataModelBase):
    """
    ParameterScheduleResourceParameter object.

    Parameters
    ----------
        resource: KRN
        parameters: Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]

    """

    resource: KRN = Field(..., description="The target Asset to which the parameters are to be applied.")
    parameters: Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]


class Revert(DataModelBase):
    """
    Revert object.

    Parameters
    ----------
        scheduled_for: datetime
        resource_parameters: List[ParameterScheduleResourceParameter]

    """

    scheduled_for: datetime = Field(
        ...,
        description="UTC date and time when the original or alternative parameters are to be applied, formatted in RFC 3339. This must be a time after the original change schedule in the key `scheduled_for` in the root of this json data package.",
    )
    resource_parameters: List[ParameterScheduleResourceParameter]


class ParameterScheduleBase(DataModelBase):
    """
    ParameterScheduleBase object.

    Parameters
    ----------
        app_name: StrictStr
        app_version: StrictStr
        scheduled_for: datetime
        resources: List[KRN]
        parameters: Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]
        comment: Optional[StrictStr]
        revert: Optional[Revert]

    """

    app_name: StrictStr = Field(
        ..., description="Application key `name` to associate with Assets (resources) to perform the required actions."
    )
    app_version: StrictStr = Field(..., description="Version of Application.")
    scheduled_for: datetime = Field(
        ..., description="UTC date and time when the new parameters are to be applied, formatted in RFC 3339."
    )
    resources: List[KRN] = Field(
        ...,
        description="List of assets for which the parameters to be updated at the scheduled time. (example `krn:asset:bp_16`)",
        examples=["krn:asset:bp_16"],
        min_length=1,
    )
    parameters: Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool]]
    comment: Optional[StrictStr] = Field(
        None, description="Additional comments associated with the scheduled parameter change"
    )
    revert: Optional[Revert] = Field(
        None,
        description="Revert parameters configuration at a schedule time after the initial parameter change is implemented.",
    )


class ParameterSchedule(ParameterScheduleBase):
    """
    ParameterSchedule object.

    Parameters
    ----------
        id: UUID
        state: enum.ParameterScheduleState
        original_resource_parameters: Optional[List[ParameterScheduleResourceParameter]]
        error_msg: Optional[StrictStr]
        created_at: datetime
        created_by: KRN
        applied_at: Optional[datetime]
        applied_by: Optional[KRN]
        reverted_at: Optional[datetime]
        reverted_by: Optional[KRN]

    """

    id: UUID = Field(..., description="Unique ID of this parameter schedule")
    state: enum.ParameterScheduleState
    original_resource_parameters: Optional[List[ParameterScheduleResourceParameter]] = None
    error_msg: Optional[StrictStr] = Field(None, description="Error message if the schedule fails to be implemented.")
    created_at: datetime = Field(
        ..., description="UTC date and time when the parameter schedule is first created, formatted in RFC 3339."
    )
    created_by: KRN = Field(
        ..., description="The user or process that initiated the creation of this parameter scheduled."
    )
    applied_at: Optional[datetime] = Field(
        None, description="UTC date and time when the new parameters are actually applied, formatted in RFC 3339."
    )
    applied_by: Optional[KRN] = Field(
        None, description="The user or process that initiated the apply parameters command of this parameter scheduled."
    )
    reverted_at: Optional[datetime] = Field(
        None,
        description="UTC date and time when the new revert parameters are actually applied, formatted in RFC 3339.",
    )
    reverted_by: Optional[KRN] = Field(
        None,
        description="The user or process that initiated the revert parameters command of this parameter scheduled.",
    )


class WorkloadModifiableFields(DataModelBase):
    """
    WorkloadModifiableFields object.

    Parameters
    ----------
        app_version: Optional[StrictStr]
        cluster_name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        title: Optional[StrictStr]
        runtime: Optional[AppDeploymentRuntime]
        system: Optional[manifest.System]
        deployment_type: Optional[enum.DeploymentType]

    """

    app_version: Optional[StrictStr] = None
    cluster_name: Optional[StrictStr] = None
    node_name: Optional[StrictStr] = None
    title: Optional[StrictStr] = None
    runtime: Optional[AppDeploymentRuntime] = None
    system: Optional[manifest.System] = None
    deployment_type: Optional[enum.DeploymentType] = None


class WorkloadStatus(DataModelBase):
    """
    WorkloadStatus object.

    Parameters
    ----------
        last_seen: Optional[datetime]
        message: Optional[StrictStr]
        state: Optional[enum.WorkloadStatus]
        warnings: Optional[List[StrictStr]]

    """

    last_seen: Optional[datetime] = Field(
        None, description="UTC time when the Workload was last seen by the Cloud, formatted in RFC 3339."
    )
    message: Optional[StrictStr] = Field(None, description="Descriptive, human-readable string for `state`.")
    state: Optional[enum.WorkloadStatus] = Field(None, description="Current status of the Workload.")
    warnings: Optional[List[StrictStr]] = Field(None, description="All warnings received for any Workload operations.")


class WorkloadCommon(DataModelBase):
    """
    WorkloadCommon object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        app_name: Optional[StrictStr]
        app_version: Optional[StrictStr]
        app_type: Optional[enum.AppType]
        cluster_name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        download_status: Optional[enum.WorkloadDownloadStatus]
        download_error: Optional[StrictStr]
        status: Optional[WorkloadStatus]

    """

    name: Optional[StrictStr] = None
    title: Optional[StrictStr] = None
    app_name: Optional[StrictStr] = None
    app_version: Optional[StrictStr] = None
    app_type: Optional[enum.AppType] = None
    cluster_name: Optional[StrictStr] = None
    node_name: Optional[StrictStr] = None
    download_status: Optional[enum.WorkloadDownloadStatus] = None
    download_error: Optional[StrictStr] = Field(
        None, description="Simple description of the error in case the image download failed."
    )
    status: Optional[WorkloadStatus] = None


class WorkloadModifiableRuntimeResourceDatastream(DataModelBase):
    """
    WorkloadModifiableRuntimeResourceDatastream object.

    Parameters
    ----------
        map_to: Optional[StrictStr]
        configuration: Optional[Dict[str, Any]]
        way: Optional[StrictStr]
        storage: Optional[StrictStr]
        remote: Optional[StrictBool]

    """

    map_to: Optional[StrictStr] = None
    configuration: Optional[Dict[str, Any]] = None
    way: Optional[StrictStr] = None
    storage: Optional[StrictStr] = None
    remote: Optional[StrictBool] = None


class GuardrailValue(DataModelBase):
    """
    GuardrailValue object.

    Parameters
    ----------
        value: Union[StrictInt, StrictFloat]
        inclusive: Optional[StrictBool]

    """

    value: Union[StrictInt, StrictFloat] = Field(..., description="The limiting value.")
    inclusive: Optional[StrictBool] = Field(
        False, description="The defined limiting value is inclusive within the allowable range."
    )


class GuardrailRelativeValue(DataModelBase):
    """
    GuardrailRelativeValue object.

    Parameters
    ----------
        value: StrictFloat
        inclusive: Optional[StrictBool]
        type: Optional[enum.GuardrailRelativeType]

    """

    value: StrictFloat = Field(..., description="The limiting rate of change value.")
    inclusive: Optional[StrictBool] = Field(
        False, description="The defined limiting rate of change value is inclusive within the allowable range."
    )
    type: Optional[enum.GuardrailRelativeType] = None


class Increase(DataModelBase):
    """
    Increase object.

    Parameters
    ----------
        min: Optional[GuardrailRelativeValue]
        max: Optional[GuardrailRelativeValue]

    """

    min: Optional[GuardrailRelativeValue] = None
    max: Optional[GuardrailRelativeValue] = None


class Decrease(DataModelBase):
    """
    Decrease object.

    Parameters
    ----------
        min: Optional[GuardrailRelativeValue]
        max: Optional[GuardrailRelativeValue]

    """

    min: Optional[GuardrailRelativeValue] = None
    max: Optional[GuardrailRelativeValue] = None


class Relative(DataModelBase):
    """
    Relative object.

    Parameters
    ----------
        increase: Optional[Increase]
        decrease: Optional[Decrease]

    """

    increase: Optional[Increase] = Field(
        None, description="Allowable rate of increase of the Asset / Data Stream pair. "
    )
    decrease: Optional[Decrease] = Field(
        None, description="Allowable rate of decrease of the Asset / Data Stream pair. "
    )


class GuardrailRelativeConfig(DataModelBase):
    """
    GuardrailRelativeConfig object.

    Parameters
    ----------
        relative: Optional[Relative]

    """

    relative: Optional[Relative] = Field(
        None, description="Allowable rate of increase/decrease of the Asset / Data Stream pair. "
    )


class GuardrailNumberConfig(GuardrailRelativeConfig):
    """
    GuardrailNumberConfig object.

    Parameters
    ----------
        min: Optional[GuardrailValue]
        max: Optional[GuardrailValue]

    """

    min: Optional[GuardrailValue] = Field(
        None, description="Minimum limiting value allowed for the Asset / Data Stream pair."
    )
    max: Optional[GuardrailValue] = Field(
        None, description="Maximum limiting value allowed for the Asset / Data Stream pair."
    )


class Guardrail(DataModelBase):
    """
    Guardrail object.

    Parameters
    ----------
        control_disabled: Optional[StrictBool]
        number: Optional[GuardrailNumberConfig]

    """

    control_disabled: Optional[StrictBool] = False
    number: Optional[GuardrailNumberConfig] = None


class DatastreamsModel(WorkloadModifiableRuntimeResourceDatastream):
    """
    DatastreamsModel object.

    Parameters
    ----------
        guardrail: Optional[Guardrail]

    """

    guardrail: Optional[Guardrail] = None


class ResourceModel(DataModelBase):
    """
    ResourceModel object.

    Parameters
    ----------
        resource: Optional[StrictStr]
        parameters: Optional[Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]]
        datastreams: Optional[Dict[str, DatastreamsModel]]
        data_quality: Optional[Dict[str, AppDataQuality]]
        properties: Optional[Dict[str, Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]]

    """

    resource: Optional[StrictStr] = None
    parameters: Optional[
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
    ] = None
    datastreams: Optional[Dict[str, DatastreamsModel]] = None
    data_quality: Optional[Dict[str, AppDataQuality]] = None
    properties: Optional[
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
    ] = None


class WorkloadRuntime(DataModelBase):
    """
    WorkloadRuntime object.

    Parameters
    ----------
        custom_actions: Optional[List[manifest.CustomAction]]
        resources: Optional[List[ResourceModel]]
        configuration: Optional[Dict[str, Any]]

    """

    custom_actions: Optional[List[manifest.CustomAction]] = None
    resources: Optional[List[ResourceModel]] = None
    configuration: Optional[Dict[str, Any]] = None


class StagedStatus(DataModelBase):
    """
    StagedStatus object.

    Parameters
    ----------
        message: Optional[StrictStr]
        state: Optional[enum.WorkloadStatus]
        warnings: Optional[List[StrictStr]]

    """

    message: Optional[StrictStr] = Field(None, description="Descriptive, human-readable string for `state`.")
    state: Optional[enum.WorkloadStatus] = Field(None, description="Current status of the Staged Workload.")
    warnings: Optional[List[StrictStr]] = Field(
        None, description="All warnings received for any Staged Workload operations."
    )


class WorkloadStaged(DataModelBase):
    """
    WorkloadStaged object.

    Parameters
    ----------
        ready: Optional[StrictBool]
        app_version: Optional[StrictStr]
        deployment_type: Optional[enum.DeploymentType]
        status: Optional[StagedStatus]
        runtime: Optional[WorkloadRuntime]
        system: Optional[manifest.System]

    """

    ready: Optional[StrictBool] = Field(None, description="Staged workload ready to be applied.")
    app_version: Optional[StrictStr] = Field(
        None, description="Version Number of the Kelvin App used for the Staged Workload."
    )
    deployment_type: Optional[enum.DeploymentType] = None
    status: Optional[StagedStatus] = None
    runtime: Optional[WorkloadRuntime] = None
    system: Optional[manifest.System] = None


class Workload(WorkloadCommon):
    """
    Workload object.

    Parameters
    ----------
        runtime: Optional[WorkloadRuntime]
        system: Optional[manifest.System]
        staged: Optional[WorkloadStaged]

    """

    runtime: Optional[WorkloadRuntime] = None
    system: Optional[manifest.System] = None
    staged: Optional[WorkloadStaged] = None


class WorkloadStagedSummary(DataModelBase):
    """
    WorkloadStagedSummary object.

    Parameters
    ----------
        ready: Optional[StrictBool]
        app_version: Optional[StrictStr]
        deployment_type: Optional[enum.DeploymentType]
        status: Optional[StagedStatus]

    """

    ready: Optional[StrictBool] = Field(None, description="Staged workload ready to be applied.")
    app_version: Optional[StrictStr] = Field(
        None, description="Version Number of the Kelvin App used for the Staged Workload."
    )
    deployment_type: Optional[enum.DeploymentType] = None
    status: Optional[StagedStatus] = None


class WorkloadSummary(WorkloadCommon, Created, Updated):
    """
    WorkloadSummary object.

    Parameters
    ----------
        staged: Optional[WorkloadStagedSummary]

    """

    staged: Optional[WorkloadStagedSummary] = None


class WorkloadNamesList(DataModelBase):
    """
    WorkloadNamesList object.

    Parameters
    ----------
        workload_names: Optional[List[StrictStr]]

    """

    workload_names: Optional[List[StrictStr]] = None


class AssetProperty(DataModelBase):
    """
    AssetProperty object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, List[StrictInt], List[StrictFloat], List[StrictStr], List[StrictBool]]]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Asset Property. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["water-line-pressure"],
    )
    title: Optional[StrictStr] = Field(
        None,
        description="Display name (title) for the Asset Property. You can use any character, numeric, space and special character in this key.",
        examples=["Water Line Pressure"],
    )
    value: Optional[
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
    ] = Field(None, description="Value for this Asset Property.", examples=[87])


class AssetStatusItem(DataModelBase):
    """
    AssetStatusItem object.

    Parameters
    ----------
        last_seen: Optional[datetime]
        state: Optional[enum.AssetState]

    """

    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Asset was last seen, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    state: Optional[enum.AssetState] = None


class Asset(DataModelBase):
    """
    Asset object.

    Parameters
    ----------
        asset_type_name: Optional[StrictStr]
        asset_type_title: Optional[StrictStr]
        created: Optional[datetime]
        name: Optional[StrictStr]
        properties: Optional[List[AssetProperty]]
        status: Optional[AssetStatusItem]
        title: Optional[StrictStr]
        updated: Optional[datetime]

    """

    asset_type_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Asset Type linked to this Asset.", examples=["beam_pump"]
    )
    asset_type_title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Asset Type linked to this Asset.", examples=["Beam Pump"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Asset was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(None, description="Unique identifier `name` of the Asset.", examples=["well_01"])
    properties: Optional[List[AssetProperty]] = Field(
        None,
        description="Array of custom properties. These properties are not used by the Kelvin Platform and are for end-user use only.",
    )
    status: Optional[AssetStatusItem] = None
    title: Optional[StrictStr] = Field(None, description="Display name (`title`) of the Asset.", examples=["Well 01"])
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Asset keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class SimpleAsset(DataModelBase):
    """
    SimpleAsset object.

    Parameters
    ----------
        name: Optional[StrictStr]
        state: Optional[enum.AssetState]

    """

    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Asset. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["beam_pump"],
    )
    state: Optional[enum.AssetState] = None


class AssetStatus(DataModelBase):
    """
    AssetStatus object.

    Parameters
    ----------
        data: Optional[List[SimpleAsset]]

    """

    data: Optional[List[SimpleAsset]] = Field(
        None,
        description="A dictionary with a data property that contains an array of all Assets and their corresponding current status (`state`).",
    )


class AssetType(DataModelBase):
    """
    AssetType object.

    Parameters
    ----------
        created: Optional[datetime]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Asset Type was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` for the Asset Type. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
        examples=["beam_pump"],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Asset Type.", examples=["Beam Pump"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Asset Type keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class ControlChangeFrom(DataModelBase):
    """
    ControlChangeFrom object.

    Parameters
    ----------
        value: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]
        timestamp: datetime

    """

    value: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ..., description="Value represented in one of these formats."
    )
    timestamp: datetime = Field(
        ...,
        description="UTC time when the current `value` is recorded in the Control Change object, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class ControlChangeReport(DataModelBase):
    """
    ControlChangeReport object.

    Parameters
    ----------
        value: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]
        timestamp: datetime
        source: enum.ControlChangeSource

    """

    value: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ..., description="Value represented in one of these formats."
    )
    timestamp: datetime = Field(..., examples=["2024-12-18T18:22:18.582724Z"])
    source: enum.ControlChangeSource


class ControlChangeReported(DataModelBase):
    """
    ControlChangeReported object.

    Parameters
    ----------
        before: Optional[ControlChangeReport]
        after: Optional[ControlChangeReport]

    """

    before: Optional[ControlChangeReport] = None
    after: Optional[ControlChangeReport] = None


class CustomActionCreationFields(DataModelBase):
    """
    CustomActionCreationFields object.

    Parameters
    ----------
        type: StrictStr
        resource: KRN
        title: StrictStr
        description: Optional[StrictStr]
        expiration_date: datetime
        payload: Optional[Dict[str, Any]]
        trace_id: Optional[StrictStr]

    """

    type: StrictStr = Field(
        ...,
        description="The type of the action. This is used to identify the action in the system.",
        examples=["email"],
    )
    resource: KRN = Field(..., description="", examples=["krn:asset:my-asset"])
    title: StrictStr = Field(
        ...,
        description="The title of the action. This is a short description of the action that will be displayed to the user.",
        examples=["Diagnose Beam Pump GW-B12-037"],
    )
    description: Optional[StrictStr] = Field(
        None,
        description="The description of the action. This is a longer description of the action that will be displayed to the user.",
        examples=["Beam Pump GW-B12-037 needs to be diagnosed."],
    )
    expiration_date: datetime = Field(
        ...,
        description="The expiration date of the action. The action will be automatically cancelled if it is not completed by this date.",
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The payload is a JSON object that contains the necessary information for the executor to perform the action. The structure of the payload will depend on the action type.",
        examples=[{"id": "WO-2025-0412", "priority": "high", "description": "Diagnose Beam Pump GW-B12-037."}],
    )
    trace_id: Optional[StrictStr] = None


class CustomActionTransitionData(DataModelBase):
    """
    CustomActionTransitionData object.

    Parameters
    ----------
        state: enum.CustomActionState
        failure_reason: Optional[enum.CustomActionFailureReason]
        message: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]

    """

    state: enum.CustomActionState
    failure_reason: Optional[enum.CustomActionFailureReason] = None
    message: Optional[StrictStr] = Field(None, description="A message associated with the state transition.")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="The metadata is a JSON object that contains additional information about the action. The structure of the metadata will depend on the action type.",
    )


class StatusLogItem(CustomActionTransitionData):
    """
    StatusLogItem object.

    Parameters
    ----------
        timestamp: datetime
        source: StrictStr

    """

    timestamp: datetime
    source: StrictStr


class CustomActionTransitions(DataModelBase):
    """
    CustomActionTransitions object.

    Parameters
    ----------
        status_log: Optional[List[StatusLogItem]]

    """

    status_log: Optional[List[StatusLogItem]] = Field(
        None, description="The transitions array contains a list of entries that describe the action state transitions."
    )


class CustomAction(CustomActionCreationFields, CustomActionTransitionData, CustomActionTransitions):
    """
    CustomAction object.

    Parameters
    ----------
        id: UUID
        created: datetime
        updated: datetime

    """

    id: UUID
    created: datetime = Field(
        ...,
        description="UTC time when the Recommendation Type was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated: datetime = Field(
        ...,
        description="UTC time when any Recommendation Type keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class CustomActionType(DataModelBase):
    """
    CustomActionType object.

    Parameters
    ----------
        created: Optional[datetime]
        created_by: Optional[KRN]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]
        updated: Optional[datetime]
        updated_by: Optional[KRN]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Custom Action Type was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created_by: Optional[KRN] = Field(
        None,
        description="The user or process that initiated the creation of this custom action type.",
        examples=["krn:user:email@kelvininc.com"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` for the Custom Action Type.", examples=["Email"]
    )
    title: Optional[StrictStr] = Field(None, examples=["Email"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Custom Action Type. The structure of the `metadata` object can have any key/value structure.",
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Custom Action Type keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated_by: Optional[KRN] = Field(
        None,
        description="The user or process that updated this custom action type.",
        examples=["krn:user:email@kelvininc.com"],
    )


class KelvinTimestampAnomaly(DataModelBase):
    """
    KelvinTimestampAnomaly object.

    Parameters
    ----------
        enabled: StrictBool

    """

    enabled: StrictBool = Field(..., description="Define if the timestamp anomaly algorithm is enabled.")


class Configuration(DataModelBase):
    """
    Configuration object.

    Parameters
    ----------
        window_size: Optional[StrictInt]

    """

    window_size: Optional[StrictInt] = Field(5, description="The size of the window to check for duplicates.")


class KelvinDuplicateDetection(DataModelBase):
    """
    KelvinDuplicateDetection object.

    Parameters
    ----------
        enabled: StrictBool
        configuration: Optional[Configuration]

    """

    enabled: StrictBool = Field(..., description="Define if the duplicate detection algorithm is enabled.")
    configuration: Optional[Configuration] = Field(
        {}, description="The configuration for the duplicate detection algorithm."
    )


class ConfigurationModel(DataModelBase):
    """
    ConfigurationModel object.

    Parameters
    ----------
        min_threshold: Optional[StrictFloat]
        max_threshold: Optional[StrictFloat]

    """

    min_threshold: Optional[StrictFloat] = Field(
        None, description="The minimum threshold for the out of range detection."
    )
    max_threshold: Optional[StrictFloat] = Field(
        None, description="The maximum threshold for the out of range detection."
    )


class KelvinOutOfRangeDetection(DataModelBase):
    """
    KelvinOutOfRangeDetection object.

    Parameters
    ----------
        enabled: StrictBool
        configuration: Optional[ConfigurationModel]

    """

    enabled: StrictBool = Field(..., description="Define if the out of range detection algorithm is enabled.")
    configuration: Optional[ConfigurationModel] = Field(
        {}, description="The configuration for the out of range detection algorithm."
    )


class ZScore(DataModelBase):
    """
    ZScore object.

    Parameters
    ----------
        threshold: Optional[StrictFloat]
        window_size: Optional[StrictInt]

    """

    threshold: Optional[StrictFloat] = Field(3, description="The threshold for outlier detection.")
    window_size: Optional[StrictInt] = Field(10, description="The size of the window to check for outliers.")


class ConfigurationModel1(DataModelBase):
    """
    ConfigurationModel1 object.

    Parameters
    ----------
        model: Optional[enum.OutlierDetectionModel]
        z_score: Optional[ZScore]

    """

    model: Optional[enum.OutlierDetectionModel] = None
    z_score: Optional[ZScore] = Field(None, description="The configuration for the z-score outlier detection model.")


class KelvinOutlierDetection(DataModelBase):
    """
    KelvinOutlierDetection object.

    Parameters
    ----------
        enabled: StrictBool
        configuration: Optional[ConfigurationModel1]

    """

    enabled: StrictBool = Field(..., description="Define if the outlier detection algorithm is enabled.")
    configuration: Optional[ConfigurationModel1] = Field(
        {}, description="The configuration for the outlier detection algorithm."
    )


class ConfigurationModel2(DataModelBase):
    """
    ConfigurationModel2 object.

    Parameters
    ----------
        window_expected_number_msgs: Optional[StrictInt]
        window_interval_unit: Optional[enum.WindowIntervalUnit]

    """

    window_expected_number_msgs: Optional[StrictInt] = Field(None, description="The expected number of messages.")
    window_interval_unit: Optional[enum.WindowIntervalUnit] = Field(
        None, description="The window interval unit for the data availability check.", examples=["sec"]
    )


class KelvinDataAvailability(DataModelBase):
    """
    KelvinDataAvailability object.

    Parameters
    ----------
        enabled: StrictBool
        configuration: Optional[ConfigurationModel2]

    """

    enabled: StrictBool = Field(..., description="Define if the data availability algorithm is enabled.")
    configuration: Optional[ConfigurationModel2] = Field(
        {}, description="The configuration for the data availability algorithm."
    )


class DataQualityConfigurations(DataModelBase):
    """
    DataQualityConfigurations object.

    Parameters
    ----------
        kelvin_timestamp_anomaly: Optional[KelvinTimestampAnomaly]
        kelvin_duplicate_detection: Optional[KelvinDuplicateDetection]
        kelvin_out_of_range_detection: Optional[KelvinOutOfRangeDetection]
        kelvin_outlier_detection: Optional[KelvinOutlierDetection]
        kelvin_data_availability: Optional[KelvinDataAvailability]

    """

    kelvin_timestamp_anomaly: Optional[KelvinTimestampAnomaly] = None
    kelvin_duplicate_detection: Optional[KelvinDuplicateDetection] = None
    kelvin_out_of_range_detection: Optional[KelvinOutOfRangeDetection] = None
    kelvin_outlier_detection: Optional[KelvinOutlierDetection] = None
    kelvin_data_availability: Optional[KelvinDataAvailability] = None


class DataQualityCreationFields(DataModelBase):
    """
    DataQualityCreationFields object.

    Parameters
    ----------
        resource: KRN
        configurations: DataQualityConfigurations

    """

    resource: KRN = Field(
        ...,
        description="The Asset or Asset/Data Stream pair to which the DataQuality is applied. (example: `krn:ad:asset1/setpoint`).",
        examples=["krn:ad:asset1/setpoint"],
    )
    configurations: DataQualityConfigurations


class KelvinDataAvailabilityCount(DataModelBase):
    """
    KelvinDataAvailabilityCount object.

    Parameters
    ----------
        enabled: StrictBool

    """

    enabled: StrictBool = Field(..., description="Define if the data availability count algorithm is enabled.")


class KelvinDataAvailabilityRate(DataModelBase):
    """
    KelvinDataAvailabilityRate object.

    Parameters
    ----------
        enabled: StrictBool

    """

    enabled: StrictBool = Field(..., description="Define if the data availability rate algorithm is enabled.")


class Configurations(DataModelBase):
    """
    Configurations object.

    Parameters
    ----------
        kelvin_timestamp_anomaly: Optional[KelvinTimestampAnomaly]
        kelvin_duplicate_detection: Optional[KelvinDuplicateDetection]
        kelvin_out_of_range_detection: Optional[KelvinOutOfRangeDetection]
        kelvin_outlier_detection: Optional[KelvinOutlierDetection]
        kelvin_data_availability: Optional[KelvinDataAvailability]
        kelvin_data_availability_count: Optional[KelvinDataAvailabilityCount]
        kelvin_data_availability_rate: Optional[KelvinDataAvailabilityRate]

    """

    kelvin_timestamp_anomaly: Optional[KelvinTimestampAnomaly] = None
    kelvin_duplicate_detection: Optional[KelvinDuplicateDetection] = None
    kelvin_out_of_range_detection: Optional[KelvinOutOfRangeDetection] = None
    kelvin_outlier_detection: Optional[KelvinOutlierDetection] = None
    kelvin_data_availability: Optional[KelvinDataAvailability] = None
    kelvin_data_availability_count: Optional[KelvinDataAvailabilityCount] = None
    kelvin_data_availability_rate: Optional[KelvinDataAvailabilityRate] = None


class DataQuality(DataModelBase):
    """
    DataQuality object.

    Parameters
    ----------
        resource: KRN
        configurations: Configurations
        created: Optional[datetime]
        created_by: Optional[KRN]
        updated: Optional[datetime]
        updated_by: Optional[KRN]

    """

    resource: KRN = Field(
        ...,
        description="The Asset or Asset/Data Stream pair to which the DataQuality is applied. (example: `krn:ad:asset1/setpoint`).",
        examples=["krn:ad:asset1/setpoint"],
    )
    configurations: Configurations = Field(
        ..., description="The Data Quality configurations applied to the Asset or Asset/Data Stream pair."
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the data quality was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created_by: Optional[KRN] = Field(
        None,
        description="The process that created this data quality. This can be a user or an automated process like a workload, application, etc.",
        examples=["krn:user:john@kelvininc.com"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any data quality keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated_by: Optional[KRN] = Field(
        None,
        description="The process that last updated this data quality. This can be a user or an automated process like a workload, application, etc.",
        examples=["krn:user:john@kelvininc.com"],
    )


class SimulationData(DataModelBase):
    """
    SimulationData object.

    Parameters
    ----------
        payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        resource: Optional[KRN]
        timestamp: Optional[datetime]

    """

    payload: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None, description="Raw value for `resource` at the specified `timestamp`."
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


class DataStreamDataType(DataModelBase):
    """
    DataStreamDataType object.

    Parameters
    ----------
        created: Optional[datetime]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Data Type was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Data Type.", examples=["number"]
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Data Type.", examples=["Number"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Data Type keys were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )


class DataStreamSemanticType(DataModelBase):
    """
    DataStreamSemanticType object.

    Parameters
    ----------
        created: Optional[datetime]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Semantic Type was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Semantic Type.", examples=["mass_flow_rate"]
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Semantic Type.", examples=["Mass Flow Rate"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Semantic Type keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class Unit(DataModelBase):
    """
    Unit object.

    Parameters
    ----------
        created: Optional[datetime]
        name: Optional[StrictStr]
        symbol: Optional[StrictStr]
        title: Optional[StrictStr]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Unit was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Unit.", examples=["degree_fahrenheit"]
    )
    symbol: Optional[StrictStr] = Field(
        None,
        description="A brief and precise character or set of characters that symbolize a specific measurement of the Unit.",
        examples=["°F"],
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Unit.", examples=["Degree Fahrenheit"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Unit keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class Context(BaseModelRoot[StrictStr]):
    root: StrictStr


class DataTag(DataModelBase):
    """
    DataTag object.

    Parameters
    ----------
        id: Optional[UUID]
        start_date: Optional[datetime]
        end_date: Optional[datetime]
        tag_name: Optional[StrictStr]
        resource: Optional[KRN]
        source: Optional[KRN]
        description: Optional[StrictStr]
        contexts: Optional[List[KRN]]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    id: Optional[UUID] = Field(
        None,
        description="A unique randomly generated UUID as the key `id` for the Data Tag.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
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
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Data Tag was created, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Data Tag keys were last updated, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )


class Tag(DataModelBase):
    """
    Tag object.

    Parameters
    ----------
        name: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(None, description="Tag name", examples=["Valve Change"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Tag. The structure of the `metadata` object can have any key/value structure and will depend on the required properties of the Tag.",
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Data Tag was created, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Data Tag keys were last updated, formatted in RFC 3339.",
        examples=["2024-02-06T19:22:18.582724Z"],
    )


class FileStorage(DataModelBase):
    """
    FileStorage object.

    Parameters
    ----------
        file_id: Optional[StrictStr]
        file_name: Optional[StrictStr]
        file_size: Optional[StrictInt]
        checksum: Optional[StrictStr]
        source: Optional[StrictStr]
        created: Optional[datetime]
        metadata: Optional[Dict[str, Any]]

    """

    file_id: Optional[StrictStr] = Field(
        None, description="Generated UUID for a file", examples=["50FDD765-DBD7-4C7C-844D-E6211C9CD9E7"]
    )
    file_name: Optional[StrictStr] = Field(None, description="Actual file name", examples=["test.csv"])
    file_size: Optional[StrictInt] = Field(None, description="File size in bytes", examples=[300])
    checksum: Optional[StrictStr] = Field(
        None,
        description="File SHA256 checksum",
        examples=["e07de9b7a1788fe439bd1d9a114d1a3ee4eb5b29f8a9e11057f7c31d718c5614"],
    )
    source: Optional[StrictStr] = Field(
        None, description="Resource that uploaded the file", examples=["krn:user:user1"]
    )
    created: Optional[datetime] = Field(
        None,
        description="UTC time representing when the file was uploaded, formatted in RFC 3339.",
        examples=["2024-02-20T22:22:18.582724Z"],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="A free-form JSON object representing the files metadata",
        examples=[{"property1": True, "property2": 2}],
    )


class GuardrailValueUpdater(DataModelBase):
    """
    GuardrailValueUpdater object.

    Parameters
    ----------
        source: KRN
        inclusive: Optional[StrictBool]

    """

    source: KRN = Field(
        ...,
        description="Asset / Data Stream pair used to determine the values for the minimum and maximum guardrail values.",
    )
    inclusive: Optional[StrictBool] = Field(
        False, description="The Asset / Data Stream pair value is inclusive within the allowable range."
    )


class Number(DataModelBase):
    """
    Number object.

    Parameters
    ----------
        min: Optional[GuardrailValueUpdater]
        max: Optional[GuardrailValueUpdater]

    """

    min: Optional[GuardrailValueUpdater] = None
    max: Optional[GuardrailValueUpdater] = None


class GuardrailUpdater(DataModelBase):
    """
    GuardrailUpdater object.

    Parameters
    ----------
        number: Optional[Number]

    """

    number: Optional[Number] = Field(None, description="Limits for absolute minimum and maximum values.")


class GuardrailConfig(DataModelBase):
    """
    GuardrailConfig object.

    Parameters
    ----------
        control_disabled: Optional[StrictBool]
        number: Optional[GuardrailNumberConfig]
        updater: Optional[GuardrailUpdater]

    """

    control_disabled: Optional[StrictBool] = Field(
        False, description="Set the current status indicating whether this Guardrail is active or disabled."
    )
    number: Optional[GuardrailNumberConfig] = None
    updater: Optional[GuardrailUpdater] = None


class GuardrailConfigWithResource(GuardrailConfig):
    """
    GuardrailConfigWithResource object.

    Parameters
    ----------
        resource: KRN

    """

    resource: KRN = Field(
        ...,
        description="The Asset/Data Stream pair to which the Guardrail will be applied.",
        examples=["krn:ad:asset1/setpoint"],
    )


class Min(GuardrailValue, Updated):
    """
    Min object.

    Parameters
    ----------

    """


class Max(GuardrailValue, Updated):
    """
    Max object.

    Parameters
    ----------

    """


class GuardrailNumber(GuardrailRelativeConfig):
    """
    GuardrailNumber object.

    Parameters
    ----------
        min: Optional[Min]
        max: Optional[Max]

    """

    min: Optional[Min] = Field(None, description="Minimum limiting value allowed for the Asset / Data Stream pair.")
    max: Optional[Max] = Field(None, description="Maximum limiting value allowed for the Asset / Data Stream pair.")


class GuardrailModel(Created, Updated):
    """
    GuardrailModel object.

    Parameters
    ----------
        resource: KRN
        control_disabled: Optional[StrictBool]
        number: Optional[GuardrailNumber]
        updater: Optional[GuardrailUpdater]

    """

    resource: KRN = Field(
        ...,
        description="The Asset/Data Stream pair to which the Guardrail is applied. (example: `krn:ad:asset1/setpoint`).",
        examples=["krn:ad:asset1/setpoint"],
    )
    control_disabled: Optional[StrictBool] = Field(
        False, description="Current status indicating whether this Guardrail is active or disabled."
    )
    number: Optional[GuardrailNumber] = None
    updater: Optional[GuardrailUpdater] = None


class InstanceAuditLogItem(DataModelBase):
    """
    InstanceAuditLogItem object.

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


class InstanceSettings(DataModelBase):
    """
    InstanceSettings object.

    Parameters
    ----------
        created: Optional[datetime]
        name: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Instance Setting was first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Instance Setting.",
        examples=["core.ui.datastreams.asset-type.groups"],
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The Instance Settings. The structure of this `payload` object depends on the type of Instance Setting being defined.",
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Instance Settings keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
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


class UpgradeStatus(DataModelBase):
    """
    UpgradeStatus object.

    Parameters
    ----------
        message: Optional[StrictStr]
        state: Optional[enum.UpgradeStatusState]

    """

    message: Optional[StrictStr] = Field(
        None, description="Any feedback messages about the current upgrade process.", examples=[""]
    )
    state: Optional[enum.UpgradeStatusState] = None


class Version(DataModelBase):
    """
    Version object.

    Parameters
    ----------
        k8s_version: Optional[StrictStr]
        kelvin_version: Optional[StrictStr]

    """

    k8s_version: Optional[StrictStr] = Field(
        None, description="Current version of k8s installed on the Cluster.", examples=["v1.24.10+k3s1"]
    )
    kelvin_version: Optional[StrictStr] = Field(
        None, description="Current version of Kelvin Software installed on the Cluster.", examples=["4.0.0-rc2024.519"]
    )


class OrchestrationCluster(DataModelBase):
    """
    OrchestrationCluster object.

    Parameters
    ----------
        created: Optional[datetime]
        forward_logs_buffer_size: Optional[StrictInt]
        forward_logs_enabled: Optional[StrictBool]
        join_script: Optional[StrictStr]
        last_seen: Optional[datetime]
        manifests_scrape_enabled: Optional[StrictBool]
        manifests_scrape_interval: Optional[StrictInt]
        name: Optional[StrictStr]
        provision_script: Optional[StrictStr]
        ready: Optional[StrictBool]
        service_account_token: Optional[StrictStr]
        status: Optional[enum.OrchestrationClusterStatus]
        sync_scrape_interval: Optional[StrictInt]
        telemetry_buffer_size: Optional[StrictInt]
        telemetry_enabled: Optional[StrictBool]
        telemetry_scrape_interval: Optional[StrictInt]
        telemetry_alerts_enabled: Optional[StrictBool]
        title: Optional[StrictStr]
        type: Optional[enum.ClusterType]
        updated: Optional[datetime]
        upgrade_instantly_apply: Optional[StrictBool]
        upgrade_pre_download: Optional[StrictBool]
        upgrade_status: Optional[UpgradeStatus]
        version: Optional[Version]
        edge_apps: Optional[ClusterEdgeApps]
        edge_options: Optional[ClusterEdgeOptions]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Cluster was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    forward_logs_buffer_size: Optional[StrictInt] = Field(
        5,
        description="Size in gigabytes of the log storage in the Cluster when Cluster is offline. Any setting changes will delete all logs not yet transferred from the Cluster to Cloud.",
        examples=[10],
    )
    forward_logs_enabled: Optional[StrictBool] = Field(
        True,
        description="Enable offline storage in the Cluster for log retention; transfers logs when Cluster is next online.",
        examples=[True],
    )
    join_script: Optional[StrictStr] = None
    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Cluster was last seen by the Cloud, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    manifests_scrape_enabled: Optional[StrictBool] = Field(
        True, description="Enable auto update Kelvin Software running on the Cluster.", examples=[True]
    )
    manifests_scrape_interval: Optional[StrictInt] = Field(
        86400,
        description="Frequency in seconds for checking updates in the Cloud for Kelvin Software running on the Cluster.",
        examples=[3600],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier key `name` of the Cluster.", examples=["aws-cluster"]
    )
    provision_script: Optional[StrictStr] = Field(
        None,
        description="Provision script required to install the Kelvin Software at the edge.",
        examples=["bash <(curl -sfS https://{URL}/provision) --service-account bm9kZS1jbGllbnQt..."],
    )
    ready: Optional[StrictBool] = Field(
        None, description="Setting to inform Kelvin UI if the Cluster is ready.", examples=[True]
    )
    service_account_token: Optional[StrictStr] = Field(
        None,
        description="Service account token for automated processes to authenticate with when performing actions in the Cluster.",
    )
    status: Optional[enum.OrchestrationClusterStatus] = None
    sync_scrape_interval: Optional[StrictInt] = Field(
        30,
        description="Frequency in seconds that the Cluster checks for new changes to apply to Workloads or Applications (deploy, start, stop, etc.)",
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
    telemetry_scrape_interval: Optional[StrictInt] = Field(
        60,
        description="Time interval in seconds to save each telemetry data. Any setting changes will delete all data not yet transferred from the Cluster to Cloud.",
        examples=[60],
    )
    telemetry_alerts_enabled: Optional[StrictBool] = Field(
        True, description="Enables or disables the alerts on the cluster nodes.", examples=[False]
    )
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Cluster.", examples=["AWS Cluster"]
    )
    type: Optional[enum.ClusterType] = Field(None, description="Type of Cluster deployed.")
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Cluster keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    upgrade_instantly_apply: Optional[StrictBool] = Field(
        None,
        description="Option if upgrades should be applied automatically and instantly as soon as they are available in the Cluster.",
        examples=[True],
    )
    upgrade_pre_download: Optional[StrictBool] = Field(
        None,
        description="Option for pre-downloading new Workloads or Application upgrades to the Cluster. Actual upgrade initiation requires manual action or having `instantly_apply` set to true.",
        examples=[True],
    )
    upgrade_status: Optional[UpgradeStatus] = Field(
        None, description="Current status and messages for any ongoing updates to the Cluster."
    )
    version: Optional[Version] = Field(
        None, description="Current versions of the different core component software installed on the Cluster."
    )
    edge_apps: Optional[ClusterEdgeApps] = None
    edge_options: Optional[ClusterEdgeOptions] = None


class NodeCapacity(DataModelBase):
    """
    NodeCapacity object.

    Parameters
    ----------
        cpu: Optional[StrictStr]
        ephemeral_storage: Optional[StrictStr]
        memory: Optional[StrictStr]
        pods: Optional[StrictStr]

    """

    cpu: Optional[StrictStr] = Field(None, description="Number of CPU cores available on the Node.", examples=["2"])
    ephemeral_storage: Optional[StrictStr] = Field(
        None,
        alias="ephemeral-storage",
        description="Amount of ephemeral storage available on the Node.",
        examples=["30417472Ki"],
    )
    memory: Optional[StrictStr] = Field(
        None, description="Amount of memory available on the Node.", examples=["3944492Ki"]
    )
    pods: Optional[StrictStr] = Field(
        None, description="Maximum number of Pods that can be scheduled on the Node.", examples=["110"]
    )


class PropertyDefinition(DataModelBase):
    """
    PropertyDefinition object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        primitive_type: Optional[enum.PropertyType]
        created: Optional[datetime]
        updated: Optional[datetime]

    """

    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Property Definition.", examples=["region"]
    )
    title: Optional[StrictStr] = Field(
        None, description="Unique identifier `title` of the Property Definition.", examples=["Region"]
    )
    primitive_type: Optional[enum.PropertyType] = None
    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Property was created, formatted in RFC 3339.",
        examples=["2024-11-11T18:22:18.582724Z"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Property keys were last updated, formatted in RFC 3339.",
        examples=["2024-11-11T18:22:18.582724Z"],
    )


class PropertyValueHistory(DataModelBase):
    """
    PropertyValueHistory object.

    Parameters
    ----------
        property_name: Optional[StrictStr]
        resource: Optional[KRN]
        timestamp: Optional[datetime]
        source: Optional[StrictStr]
        value: Optional[Dict[str, Any]]

    """

    property_name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Property.", examples=["region"]
    )
    resource: Optional[KRN] = Field(
        None, description="Resource to which the value belongs.", examples=["krn:asset:asset1"]
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="UTC time for when the value was updated, formatted in RFC 3339.",
        examples=["2025-01-29T12:00:00.582724Z"],
    )
    source: Optional[StrictStr] = Field(
        None, description="Represents who triggered the value change.", examples=["krn:user:user1"]
    )
    value: Optional[Dict[str, Any]] = Field(None, description="Historical value at the given timestamp.", examples=[1])


class RecommendationEvidence(DataModelBase):
    """
    RecommendationEvidence object.

    Parameters
    ----------
        type: Optional[enum.RecommendationEvidenceType]
        payload: Optional[Dict[str, Any]]

    """

    type: Optional[enum.RecommendationEvidenceType] = None
    payload: Optional[Dict[str, Any]] = Field(
        None, description="The payload of the evidence that is being used to create the Recommendation."
    )


class RecommendationBase(DataModelBase):
    """
    RecommendationBase object.

    Parameters
    ----------
        confidence: Optional[StrictInt]
        custom_identifier: Optional[StrictStr]
        description: Optional[StrictStr]
        expiration_date: Optional[datetime]
        metadata: Optional[Dict[str, Any]]
        resource: KRN
        resource_parameters: Optional[Dict[str, Any]]
        type: StrictStr
        evidences: Optional[List[RecommendationEvidence]]

    """

    confidence: Optional[StrictInt] = Field(
        None,
        description="Confidence level of the Recommendation. This is usually, but not mandatory, related to any machine learning model confidence results.",
        examples=[7],
    )
    custom_identifier: Optional[StrictStr] = Field(
        None, description="An optional custom identifier for any purpose.", examples=["model-aws-ltsm-anomaly"]
    )
    description: Optional[StrictStr] = Field(
        None,
        description="Detailed description of the Recommendation.",
        examples=[
            "Beam pump speed AI optimizer application recommends a new value for the speed setpoint of the controller."
        ],
    )
    expiration_date: Optional[datetime] = Field(
        None,
        description="UTC time when any the Recommendation will expire and the `status` automatically marked as `expired`, formatted in RFC 3339. The operator will not be able to take any further actions on this Recommendation. If no date is given, then the Recommendation will never expire.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom dictionary keys/values for use by clients for anything useful and related to the Recommendation.",
    )
    resource: KRN = Field(
        ..., description="The asset that this Recommendation is related to.", examples=["krn:asset:bp_16"]
    )
    resource_parameters: Optional[Dict[str, Any]] = Field(None, description="resource_parameters")
    type: StrictStr = Field(
        ...,
        description="The Recommendation Type `name` associated with the Recommendation.",
        examples=["Decrease Speed"],
    )
    evidences: Optional[List[RecommendationEvidence]] = Field(
        None, description="A list of evidence that is being used to create the Recommendation."
    )


class RecommendationControlChangeCreate(DataModelBase):
    """
    RecommendationControlChangeCreate object.

    Parameters
    ----------
        control_change_id: Optional[UUID]
        expiration_date: datetime
        trace_id: Optional[StrictStr]
        payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]
        resource: KRN
        retries: Optional[StrictInt]
        timeout: Optional[StrictInt]
        from_: Optional[ControlChangeFrom]

    """

    control_change_id: Optional[UUID] = Field(
        None,
        description="Unique identifier id for the Control Change request. This will only be returned when the Recommendation state is `applied` or `auto_accepted` where the actions have been created and an id registered on the Server.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    expiration_date: datetime = Field(
        ...,
        description="UTC time when any the Control Change initiated will expire and the `status` automatically marked as `failed`, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    trace_id: Optional[StrictStr] = Field(None, examples=["app-trace-123"])
    payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ..., description="Value represented in one of these formats."
    )
    resource: KRN = Field(
        ...,
        description="The asset / data stream pair that this Control Change will be applied to.",
        examples=["krn:ad:bp_16/motor_speed_setpoint"],
    )
    retries: Optional[StrictInt] = Field(
        0,
        description="Number of retry attempts to write the Control Change to the Bridge until a `processed` acknowledgment is received from the Bridge. If number of attempts exceeds `retries` then the Control Change Manager updates the Control Change key `state` with the value `failed`.",
        examples=[3],
    )
    timeout: Optional[StrictInt] = Field(
        300,
        description="Time in seconds the Control Change Manager will wait after sending the Control Change for the Bridge to send a `processed` acknowledgement reply before retry sending the Control Change.",
        examples=[600],
    )
    from_: Optional[ControlChangeFrom] = Field(None, alias="from")


class RecommendationActionsCreate(DataModelBase):
    """
    RecommendationActionsCreate object.

    Parameters
    ----------
        control_changes: Optional[List[RecommendationControlChangeCreate]]
        custom_actions: Optional[List[CustomActionCreationFields]]

    """

    control_changes: Optional[List[RecommendationControlChangeCreate]] = Field(
        None,
        description="An array of objects with Control Change information. If the Recommendation is `pending`, it will display creation information or if the Recommendation is `accepted` or `applied` it will show the Control Change status. Each Control Change does not need to be related to the `resource` of the Recommendation.",
    )
    custom_actions: Optional[List[CustomActionCreationFields]] = None


class RecommendationControlChange(DataModelBase):
    """
    RecommendationControlChange object.

    Parameters
    ----------
        control_change_id: Optional[UUID]
        trace_id: Optional[StrictStr]
        expiration_date: Optional[datetime]
        payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]
        resource: KRN
        retries: Optional[StrictInt]
        timeout: Optional[StrictInt]
        from_: Optional[ControlChangeFrom]
        status: Optional[enum.RecommendationActionStatus]
        status_message: Optional[StrictStr]

    """

    control_change_id: Optional[UUID] = Field(
        None,
        description="Unique identifier id for the Control Change request. This will only be returned when the Recommendation state is `applied` or `auto_accepted` where the actions have been created and an id registered on the Server.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    trace_id: Optional[StrictStr] = Field(None, examples=["app-trace-123"])
    expiration_date: Optional[datetime] = Field(
        None,
        description="UTC time when any the Control Change initiated will expire and the `status` automatically marked as `failed`, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ..., description="Value represented in one of these formats."
    )
    resource: KRN = Field(
        ...,
        description="The asset / data stream pair that this Control Change will be applied to.",
        examples=["krn:ad:bp_16/motor_speed_setpoint"],
    )
    retries: Optional[StrictInt] = Field(
        0,
        description="Number of retry attempts to write the Control Change to the Bridge until a `processed` acknowledgment is received from the Bridge. If number of attempts exceeds `retries` then the Control Change Manager updates the Control Change key `state` with the value `failed`.",
        examples=[3],
    )
    timeout: Optional[StrictInt] = Field(
        300,
        description="Time in seconds the Control Change Manager will wait after sending the Control Change for the Bridge to send a `processed` acknowledgement reply before retry sending the Control Change.",
        examples=[600],
    )
    from_: Optional[ControlChangeFrom] = Field(None, alias="from")
    status: Optional[enum.RecommendationActionStatus] = Field(
        None, description="Current `status` of the Recommendation action."
    )
    status_message: Optional[StrictStr] = Field(
        None,
        description="If something goes wrong while applying the action, this field will contain the error message.",
    )


class CustomActionModel(CustomActionCreationFields):
    """
    CustomActionModel object.

    Parameters
    ----------
        custom_action_id: Optional[UUID]
        status: Optional[enum.RecommendationActionStatus]
        status_message: Optional[StrictStr]

    """

    custom_action_id: Optional[UUID] = None
    status: Optional[enum.RecommendationActionStatus] = Field(
        None, description="Current `status` of the Recommendation action."
    )
    status_message: Optional[StrictStr] = Field(
        None,
        description="If something goes wrong while applying the action, this field will contain the error message.",
    )


class RecommendationActions(DataModelBase):
    """
    RecommendationActions object.

    Parameters
    ----------
        control_changes: Optional[List[RecommendationControlChange]]
        custom_actions: Optional[List[CustomActionModel]]

    """

    control_changes: Optional[List[RecommendationControlChange]] = Field(
        None,
        description="An array of objects with Control Change information. If the Recommendation is `pending`, it will display creation information or if the Recommendation is `accepted` or `applied` it will show the Control Change status. Each Control Change does not need to be related to the `resource` of the Recommendation.",
    )
    custom_actions: Optional[List[CustomActionModel]] = None


class Recommendation(RecommendationBase):
    """
    Recommendation object.

    Parameters
    ----------
        actions: Optional[RecommendationActions]
        id: Optional[UUID]
        type_title: Optional[StrictStr]
        message: Optional[StrictStr]
        state: Optional[enum.RecommendationState]
        created: Optional[datetime]
        source: Optional[KRN]
        updated: Optional[datetime]
        updated_by: Optional[KRN]

    """

    actions: Optional[RecommendationActions] = None
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
    message: Optional[StrictStr] = Field(
        None,
        description="Contains a message sent by the user with any descriptions useful to be associated with the `accepted` or `rejected` state.",
        examples=["Recommendation is accurate based on the current performance."],
    )
    state: Optional[enum.RecommendationState] = Field(None, description="Current `state` of the Recommendations.")
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


class RecommendationType(DataModelBase):
    """
    RecommendationType object.

    Parameters
    ----------
        created: Optional[datetime]
        created_by: Optional[KRN]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        metadata: Optional[Dict[str, Any]]
        updated: Optional[datetime]
        updated_by: Optional[KRN]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Recommendation Type was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created_by: Optional[KRN] = Field(
        None,
        description="The user or process that initiated the creation of this recommendation type.",
        examples=["krn:user:email@kelvininc.com"],
    )
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` for the Recommendation Type.", examples=["Decrease speed"]
    )
    title: Optional[StrictStr] = Field(None, examples=["Decrease Speed"])
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed Attributes of the Recommendation Type. The structure of the `metadata` object can have any key/value structure.",
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Recommendation Type keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated_by: Optional[KRN] = Field(
        None,
        description="The user or process that updated this recommendation type.",
        examples=["krn:user:email@kelvininc.com"],
    )


class ThreadAttachment(DataModelBase):
    """
    ThreadAttachment object.

    Parameters
    ----------
        extension: Optional[StrictStr]
        filename: Optional[StrictStr]
        size: Optional[StrictInt]
        url: Optional[StrictStr]

    """

    extension: Optional[StrictStr] = None
    filename: Optional[StrictStr] = None
    size: Optional[StrictInt] = None
    url: Optional[StrictStr] = None


class ThreadUserFollow(DataModelBase):
    """
    ThreadUserFollow object.

    Parameters
    ----------
        mute: Optional[StrictBool]
        seen: Optional[StrictBool]

    """

    mute: Optional[StrictBool] = None
    seen: Optional[StrictBool] = None


class KelvinMessage(DataModelBase):
    """
    KelvinMessage object.

    Parameters
    ----------
        id: UUID
        type: StrictStr
        resource: KRN
        source: KRN
        timestamp: datetime
        payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]

    """

    id: UUID = Field(
        ...,
        description="A unique randomly generated UUID as the key `id`. Duplicate keys are not allowed.",
        examples=["0002bc79-b42f-461b-95d6-cf0a28ba87aa"],
    )
    type: StrictStr = Field(
        ...,
        description="Kelvin Message Type representing the message type. If you do not know what Kelvin Message Type to put, most likely you can use `data;pt={primitive-type}`.",
    )
    resource: KRN = Field(
        ...,
        description="The resource that this message's data is linked with, expressed as a KRN. This can be an Asset, Data Stream, Asset / Data Stream pair, etc.",
        examples=["krn:ad:bp_01/motor_speed_setpoint"],
    )
    source: KRN = Field(
        ...,
        description="The resource that has initiated the writing of this message, expressed as a KRN. This can be an Application, Workload, Version specific Workload, etc.",
        examples=["krn:wlappv:cluster-01/beam-pump-optimization/3.4.7"],
    )
    timestamp: datetime = Field(
        ...,
        description="UTC time representing the time of this message's data, formatted in RFC 3339. This is usually the current time of creation of the message, but can also be back dated to any time in the past.",
    )
    payload: Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]] = Field(
        ..., description="The value of the measurement."
    )


class TimeseriesData(DataModelBase):
    """
    TimeseriesData object.

    Parameters
    ----------
        created: Optional[datetime]
        data_type: Optional[StrictStr]
        fields: Optional[List[StrictStr]]
        last_timestamp: Optional[datetime]
        last_value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]
        resource: Optional[KRN]
        source: Optional[KRN]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the `last_value` values were first created, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    data_type: Optional[StrictStr] = Field(None, description="Primitive data type of the `last_value` values.")
    fields: Optional[List[StrictStr]] = Field(
        None, description="Data `field` element name of each value in `last_value`.", examples=[["value"]]
    )
    last_timestamp: Optional[datetime] = Field(
        None,
        description="UTC time when the time series data was last accessed, formatted in RFC 3339.",
        examples=["2023-11-10T09:55:08.627924Z"],
    )
    last_value: Optional[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]] = Field(
        None, description="Most recent value received for each `field`."
    )
    resource: Optional[KRN] = Field(
        None, description="Asset / Data Stream associated with `last_value`.", examples=["krn:ad:asset/data_stream"]
    )
    source: Optional[KRN] = Field(
        None,
        description="Specifies the user or workload source for `last_value`.",
        examples=["krn:wlappv:cluster1/app1/1.2.0"],
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when the time series data was last updated, formatted in RFC 3339.",
        examples=["2023-11-10T09:55:09.31857Z"],
    )


class UserSetting(DataModelBase):
    """
    UserSetting object.

    Parameters
    ----------
        created: Optional[datetime]
        payload: Optional[Dict[str, Any]]
        setting_name: Optional[StrictStr]
        updated: Optional[datetime]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the User Setting was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The User Settings. The structure of this `payload` object depends on the type of User Setting being defined.",
    )
    setting_name: Optional[StrictStr] = Field(
        None, description="Unique identifier User Setting key `setting_name`.", examples=["kelvin-notifications"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any User Setting keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )


class SharedSetting(DataModelBase):
    """
    SharedSetting object.

    Parameters
    ----------
        created: Optional[datetime]
        created_by: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        setting_name: Optional[StrictStr]
        updated: Optional[datetime]
        updated_by: Optional[StrictStr]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when the Shared Setting was created, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    created_by: Optional[StrictStr] = Field(
        None,
        description="The User who created the Shared Setting, represented by a KRN.",
        examples=["krn:user:email@kelvin.ai"],
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The Shared Settings. The structure of this `payload` object depends on the type of Shared Setting being defined.",
    )
    setting_name: Optional[StrictStr] = Field(
        None, description="Unique identifier Shared Setting key `setting_name`.", examples=["kelvin-notifications"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Shared Setting keys were last updated, formatted in RFC 3339.",
        examples=["2024-12-18T18:22:18.582724Z"],
    )
    updated_by: Optional[StrictStr] = Field(
        None,
        description="The User who updated the Shared Setting, represented by a KRN.",
        examples=["krn:user:email@kelvin.ai"],
    )


class RolePolicyActions(BaseModelRoot[List[enum.RolePolicyAction]]):
    root: List[enum.RolePolicyAction]


class RoleConditionExpr(DataModelBase):
    """
    RoleConditionExpr object.

    Parameters
    ----------
        expr: StrictStr

    """

    expr: StrictStr


class RoleConditionExprList(DataModelBase):
    """
    RoleConditionExprList object.

    Parameters
    ----------
        of: List[RoleConditionExpr]

    """

    of: List[RoleConditionExpr] = Field(..., min_length=1)


class Match(DataModelBase):
    """
    Match object.

    Parameters
    ----------
        all: RoleConditionExprList

    """

    model_config = ConfigDict(extra="forbid")
    all: RoleConditionExprList


class MatchModel(DataModelBase):
    """
    MatchModel object.

    Parameters
    ----------
        any: RoleConditionExprList

    """

    model_config = ConfigDict(extra="forbid")
    any: RoleConditionExprList


class RolePolicyCondition(DataModelBase):
    """
    RolePolicyCondition object.

    Parameters
    ----------
        match: Union[RoleConditionExpr, Match, MatchModel]

    """

    match: Union[RoleConditionExpr, Match, MatchModel]


class LegacyAppVersion(DataModelBase):
    """
    LegacyAppVersion object.

    Parameters
    ----------
        created: Optional[datetime]
        id: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        updated: Optional[datetime]
        version: Optional[StrictStr]

    """

    created: Optional[datetime] = Field(
        None,
        description="UTC time when this App version was first uploaded to the App Registry, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    id: Optional[StrictStr] = Field(
        None,
        description="Unique identifier for this version of the App in the App Registry.",
        examples=["58ba052085dfd66545bf24a4957f6c8fd4af3c27"],
    )
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary with keys for app inputs/outputs, info, spec version and system packages. Each key represents specific settings and parameters for the App.",
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any App keys for this App version in the App Registry were last updated, formatted in RFC 3339.",
        examples=["2023-06-26T18:22:18.582724Z"],
    )
    version: Optional[StrictStr] = Field(
        None, description="Version number of this App in the App Registry.", examples=["1.2.0"]
    )


class LegacyApp(DataModelBase):
    """
    LegacyApp object.

    Parameters
    ----------
        created: Optional[datetime]
        description: Optional[StrictStr]
        latest_version: Optional[StrictStr]
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        type: Optional[enum.LegacyAppType]
        updated: Optional[datetime]
        versions: Optional[List[LegacyAppVersion]]

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
    versions: Optional[List[LegacyAppVersion]] = Field(
        None, description="Array of all App versions available in the App Registry."
    )


class AppYaml(DataModelBase):
    """
    AppYaml object.

    Parameters
    ----------

    """


class Bridge(DataModelBase):
    """
    Bridge object.

    Parameters
    ----------
        cluster_name: Optional[StrictStr]
        created: Optional[datetime]
        enabled: Optional[StrictBool]
        name: Optional[StrictStr]
        node_name: Optional[StrictStr]
        payload: Optional[AppYaml]
        status: Optional[WorkloadStatus]
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
    payload: Optional[AppYaml] = Field(
        None,
        description="Dictionary with keys for configuration, language, logging level, metrics mapping, protocol, and system packages. Each key represents specific settings and parameters for the Bridge (Connection).",
    )
    status: Optional[WorkloadStatus] = None
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


class ResourceParameters(DataModelBase):
    """
    ResourceParameters object.

    Parameters
    ----------
        resource: KRN
        parameters: List[ParameterItem]

    """

    resource: KRN = Field(..., description="The target Asset to which the parameters are to be applied.")
    parameters: List[ParameterItem]


class NetworkingAddressItem(DataModelBase):
    """
    NetworkingAddressItem object.

    Parameters
    ----------
        address: Optional[StrictStr]
        interface: Optional[StrictStr]
        port: Optional[StrictInt]

    """

    address: Optional[StrictStr] = Field(None, description="IPV4 address to reach the Service.", examples=["172.0.0.2"])
    interface: Optional[StrictStr] = Field(
        None, description="Interface responsible for hosting the Service.", examples=["eth0"]
    )
    port: Optional[StrictInt] = Field(None, description="Port designated for accessing the Service.", examples=[8080])


class NetworkingItem(DataModelBase):
    """
    NetworkingItem object.

    Parameters
    ----------
        addresses: Optional[List[NetworkingAddressItem]]
        name: Optional[StrictStr]
        protocol: Optional[enum.Protocol]

    """

    addresses: Optional[List[NetworkingAddressItem]] = Field(None, description="Array of ports exposed by the Service.")
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Service.", examples=["http-service"]
    )
    protocol: Optional[enum.Protocol] = None


class LegacyWorkloadStatus(DataModelBase):
    """
    LegacyWorkloadStatus object.

    Parameters
    ----------
        last_seen: Optional[datetime]
        message: Optional[StrictStr]
        state: Optional[enum.WorkloadStatus]
        warnings: Optional[List[StrictStr]]

    """

    last_seen: Optional[datetime] = Field(
        None,
        description="UTC time when the Workload was last seen by the Cloud, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    message: Optional[StrictStr] = Field(
        None, description="Descriptive, human-readable string for `state`.", examples=["Pending for deploy"]
    )
    state: Optional[enum.WorkloadStatus] = Field(
        None, description="Current status of the Workload.", examples=["pending_deploy"]
    )
    warnings: Optional[List[StrictStr]] = Field(
        None,
        description="All warnings received for any Workload operations.",
        examples=[
            [
                "back-off 5m0s restarting failed container=motor-speed-control-sjfhksdfhks67",
                "back-off 5m0s restarting failed container=gateway",
            ]
        ],
    )


class LegacyWorkloadStaged(DataModelBase):
    """
    LegacyWorkloadStaged object.

    Parameters
    ----------
        ready: Optional[StrictBool]
        app_version: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        instantly_apply: Optional[StrictBool]
        status: Optional[StagedStatus]

    """

    ready: Optional[StrictBool] = Field(None, description="Staged workload ready to be applied.", examples=[True])
    app_version: Optional[StrictStr] = Field(
        None, description="Version Number of the Kelvin App used for the Staged Workload.", examples=["1.2.0"]
    )
    payload: Optional[Dict[str, Any]] = Field(
        None, description="Internal Kelvin configuration information for deployment of the Staged Workload."
    )
    instantly_apply: Optional[StrictBool] = Field(
        None, description="Whether the staged workload should be instantly applied or not.", examples=[True]
    )
    status: Optional[StagedStatus] = None


class LegacyWorkload(DataModelBase):
    """
    LegacyWorkload object.

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
        name: Optional[StrictStr]
        networking: Optional[List[NetworkingItem]]
        node_name: Optional[StrictStr]
        payload: Optional[Dict[str, Any]]
        pre_download: Optional[StrictBool]
        status: Optional[LegacyWorkloadStatus]
        title: Optional[StrictStr]
        updated: Optional[datetime]
        staged: Optional[LegacyWorkloadStaged]

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
    name: Optional[StrictStr] = Field(
        None, description="Unique identifier `name` of the Workload.", examples=["motor-speed-control-ubdhwnshdy67"]
    )
    networking: Optional[List[NetworkingItem]] = Field(None, description="Array of services exposed by the workload.")
    node_name: Optional[StrictStr] = Field(
        None,
        description="Unique identifier `name` of the Node in the Cluster hosting the Workload.",
        examples=["docs-demo-node-01"],
    )
    payload: Optional[Dict[str, Any]] = Field(
        None, description="Internal Kelvin configuration information for deployment of the Workload."
    )
    pre_download: Optional[StrictBool] = Field(
        None,
        description="If true, deploy process is handled by Kelvin and all Workloads wil be downloaded to Edge System before deploy. If false, deploy process is handled by Kubernetes through default settings.",
        examples=[True],
    )
    status: Optional[LegacyWorkloadStatus] = None
    title: Optional[StrictStr] = Field(
        None, description="Display name (`title`) of the Workload.", examples=["Motor Speed Control"]
    )
    updated: Optional[datetime] = Field(
        None,
        description="UTC time when any Workload keys were last updated, formatted in RFC 3339.",
        examples=["2023-12-18T18:22:18.582724Z"],
    )
    staged: Optional[LegacyWorkloadStaged] = None


class ThreadContent(DataModelBase):
    """
    ThreadContent object.

    Parameters
    ----------
        attachments: Optional[List[ThreadAttachment]]
        mentions: Optional[List[StrictStr]]
        replies: Optional[List[ThreadReply]]
        text: Optional[StrictStr]

    """

    attachments: Optional[List[ThreadAttachment]] = None
    mentions: Optional[List[StrictStr]] = None
    replies: Optional[List[ThreadReply]] = None
    text: Optional[StrictStr] = None


class ThreadReply(DataModelBase):
    """
    ThreadReply object.

    Parameters
    ----------
        content: Optional[ThreadContent]
        created: Optional[datetime]
        id: Optional[StrictStr]
        updated: Optional[datetime]
        user_id: Optional[StrictStr]

    """

    content: Optional[ThreadContent] = None
    created: Optional[datetime] = None
    id: Optional[StrictStr] = None
    updated: Optional[datetime] = None
    user_id: Optional[StrictStr] = None


class Thread(DataModelBase):
    """
    Thread object.

    Parameters
    ----------
        content: Optional[ThreadContent]
        created: Optional[datetime]
        follows: Optional[Dict[str, ThreadUserFollow]]
        id: Optional[StrictStr]
        related_to: Optional[StrictStr]
        type: Optional[StrictStr]
        updated: Optional[datetime]
        user_id: Optional[StrictStr]

    """

    content: Optional[ThreadContent] = None
    created: Optional[datetime] = None
    follows: Optional[Dict[str, ThreadUserFollow]] = None
    id: Optional[StrictStr] = None
    related_to: Optional[StrictStr] = None
    type: Optional[StrictStr] = None
    updated: Optional[datetime] = None
    user_id: Optional[StrictStr] = None


ThreadContent.model_rebuild()
