from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.api.client.data_model import DataModelBase

from . import enum


class AppInfo(DataModelBase):
    """
    AppInfo object.

    Parameters
    ----------
        name: StrictStr
        title: StrictStr
        description: StrictStr
        category: Optional[StrictStr]
        type: enum.AppType

    """

    name: StrictStr = Field(
        ..., description="The name of the application. This is the unique identifier for the application."
    )
    title: StrictStr = Field(..., description="Human-readable name of the application.")
    description: StrictStr = Field(..., description="Human-readable description of the application.")
    category: Optional[StrictStr] = Field(None, description="The category of the application.")
    type: enum.AppType


class AppIO(DataModelBase):
    """
    AppIO object.

    Parameters
    ----------
        name: StrictStr
        data_type: Optional[StrictStr]
        way: Optional[enum.Way]
        storage: Optional[enum.Storage]
        unit: Optional[StrictStr]

    """

    name: StrictStr = Field(..., description="The name of the input/output used in the Application.")
    data_type: Optional[StrictStr] = Field(
        None,
        description="Primitive data types are: `string`, `number`, `boolean` and `object`. If another name is used, it will be considered an object with that name. It's highly recommended using a custom name when using objects.",
    )
    way: Optional[enum.Way] = None
    storage: Optional[enum.Storage] = None
    unit: Optional[StrictStr] = Field(
        None,
        description="The unit of the data. It's recommended to use the [UCUM](http://unitsofmeasure.org/ucum.html) standard for units.",
    )


class DynamicAppIO(DataModelBase):
    """
    DynamicAppIO object.

    Parameters
    ----------
        type_name: StrictStr
        data_types: Optional[List[StrictStr]]
        ownership: Optional[enum.DynamicIOOwnership]
        type: Optional[enum.DynamicIOType]

    """

    type_name: StrictStr = Field(..., description="Dynamic I/O type name.")
    data_types: Optional[List[StrictStr]] = Field(
        None, description="List of data types that the dynamic I/O type can have. If empty, any data type is allowed."
    )
    ownership: Optional[enum.DynamicIOOwnership] = None
    type: Optional[enum.DynamicIOType] = None


class Parameter(DataModelBase):
    """
    Parameter object.

    Parameters
    ----------
        name: StrictStr
        title: Optional[StrictStr]
        data_type: Optional[enum.ParameterDataType]
        default: Optional[Union[StrictStr, StrictInt, StrictFloat, StrictBool]]

    """

    name: StrictStr = Field(..., description="The name of the parameter.")
    title: Optional[StrictStr] = Field(None, description="Human-readable name of the parameter.")
    data_type: Optional[enum.ParameterDataType] = None
    default: Optional[Union[StrictStr, StrictInt, StrictFloat, StrictBool]] = None


class CustomAction(DataModelBase):
    """
    CustomAction object.

    Parameters
    ----------
        type: StrictStr
        way: Optional[enum.CAWay]

    """

    type: StrictStr = Field(..., description="The type of the custom action.")
    way: Optional[enum.CAWay] = None


class CustomDataQuality(DataModelBase):
    """
    CustomDataQuality object.

    Parameters
    ----------
        name: Optional[StrictStr]
        data_type: Optional[StrictStr]
        datastreams: Optional[List[StrictStr]]
        way: Optional[enum.DQWay]

    """

    name: Optional[StrictStr] = Field(None, description="The name of the data quality.")
    data_type: Optional[StrictStr] = Field(
        None,
        description="Primitive data types are: `string`, `number`, `boolean` and `object`. If another name is used, it will be considered an object with that name. It's highly recommended using a custom name when using objects.",
    )
    datastreams: Optional[List[StrictStr]] = None
    way: Optional[enum.DQWay] = None


class EnableRuntimeUpdate(DataModelBase):
    """
    EnableRuntimeUpdate object.

    Parameters
    ----------
        configuration: Optional[StrictBool]
        resource_parameters: Optional[StrictBool]
        resource_properties: Optional[StrictBool]

    """

    configuration: Optional[StrictBool] = False
    resource_parameters: Optional[StrictBool] = True
    resource_properties: Optional[StrictBool] = True


class Deployment(DataModelBase):
    """
    Deployment object.

    Parameters
    ----------
        allowed_resources: Optional[List[StrictStr]]

    """

    allowed_resources: Optional[List[StrictStr]] = None


class Flags(DataModelBase):
    """
    Flags object.

    Parameters
    ----------
        spec_version: Optional[StrictStr]
        legacy_data_types: Optional[StrictBool]
        legacy_extras: Optional[Dict[str, Any]]
        gateway_mode: Optional[enum.GatewayMode]
        enable_runtime_update: Optional[EnableRuntimeUpdate]
        deployment: Optional[Deployment]
        resources_required: Optional[StrictBool]

    """

    spec_version: Optional[StrictStr] = Field(
        None, description="The version of the specification that the application is using."
    )
    legacy_data_types: Optional[StrictBool] = Field(
        False,
        description="If `true`, the application uses the legacy data types (e.g. `raw.float64`, `raw.int32`,...).",
    )
    legacy_extras: Optional[Dict[str, Any]] = None
    gateway_mode: Optional[enum.GatewayMode] = None
    enable_runtime_update: Optional[EnableRuntimeUpdate] = None
    deployment: Optional[Deployment] = None
    resources_required: Optional[StrictBool] = Field(
        None,
        description="Define whether the application is deployed to specific resources (e.g. assets) or not. Applications that have inputs or outputs always require resources.",
    )


class AppVersion(AppInfo):
    """
    AppVersion object.

    Parameters
    ----------
        version: StrictStr
        flags: Optional[Flags]
        io: Optional[List[AppIO]]
        dynamic_io: Optional[List[DynamicAppIO]]
        parameters: Optional[List[Parameter]]
        custom_actions: Optional[List[CustomAction]]
        data_quality: Optional[List[CustomDataQuality]]

    """

    version: StrictStr = Field(..., description="The version of the application being created.")
    flags: Optional[Flags] = Field(
        None,
        description="Flags that can be set to enable specific behaviours on the platform when managing the application.",
    )
    io: Optional[List[AppIO]] = None
    dynamic_io: Optional[List[DynamicAppIO]] = None
    parameters: Optional[List[Parameter]] = None
    custom_actions: Optional[List[CustomAction]] = None
    data_quality: Optional[List[CustomDataQuality]] = None


class IoConfiguration(DataModelBase):
    """
    IoConfiguration object.

    Parameters
    ----------
        type_name: Optional[StrictStr]
        schema_: Optional[Dict[str, Any]]

    """

    type_name: Optional[StrictStr] = Field(None, description="Dynamic I/O type name.")
    schema_: Optional[Dict[str, Any]] = Field(
        None, alias="schema", description="JSON Schema to build the configuration by the UI."
    )


class Schemas(DataModelBase):
    """
    Schemas object.

    Parameters
    ----------
        parameters: Optional[Dict[str, Any]]
        configuration: Optional[Dict[str, Any]]
        io_configurations: Optional[List[IoConfiguration]]

    """

    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema that defines the Resource Parameters that can be configured for the App. The schema is limited to the having an `object` with `properties` that are `number`, `boolean`, or `string`.",
    )
    configuration: Optional[Dict[str, Any]] = Field(None, description="JSON Schema used to generate the UI.")
    io_configurations: Optional[List[IoConfiguration]] = Field(
        None, description="JSON Schema of each asset's dynamic I/O configuration."
    )


class Cluster(DataModelBase):
    """
    Cluster object.

    Parameters
    ----------
        name: StrictStr
        node_name: Optional[StrictStr]

    """

    name: StrictStr = Field(..., description="Cluster to deploy the application to.")
    node_name: Optional[StrictStr] = Field(None, description="Node to deploy the application to.")


class DeploymentTarget(DataModelBase):
    """
    DeploymentTarget object.

    Parameters
    ----------
        type: Optional[enum.DeploymentTargetType]
        cluster: Optional[Cluster]

    """

    type: Optional[enum.DeploymentTargetType] = enum.DeploymentTargetType.cluster
    cluster: Optional[Cluster] = None


class HttpHeader(DataModelBase):
    """
    HttpHeader object.

    Parameters
    ----------
        name: Optional[StrictStr]
        value: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(None, title="Header Name")
    value: Optional[StrictStr] = Field(None, title="Header Value")


class HttpGet(DataModelBase):
    """
    HttpGet object.

    Parameters
    ----------
        path: Optional[StrictStr]
        port: StrictInt
        scheme: Optional[enum.URIScheme]
        http_headers: Optional[List[HttpHeader]]

    """

    path: Optional[StrictStr] = Field(None, description="HTTP path to access.", title="Path")
    port: StrictInt = Field(..., description="Port for the HTTP server.", title="Port")
    scheme: Optional[enum.URIScheme] = None
    http_headers: Optional[List[HttpHeader]] = Field(
        None, description="Custom headers for the request.", title="HTTP Headers"
    )


class TcpSocket(DataModelBase):
    """
    TcpSocket object.

    Parameters
    ----------
        port: StrictInt

    """

    port: StrictInt = Field(..., description="TCP port to check.", title="Port")


class Exec(DataModelBase):
    """
    Exec object.

    Parameters
    ----------
        command: List[StrictStr]

    """

    command: List[StrictStr] = Field(..., description="Command to execute. Exit code 0 is healthy.", title="Command")


class LivenessProbe(DataModelBase):
    """
    LivenessProbe object.

    Parameters
    ----------
        initial_delay_seconds: Optional[StrictInt]
        period_seconds: Optional[StrictInt]
        timeout_seconds: Optional[StrictInt]
        failure_threshold: Optional[StrictInt]
        type: Optional[enum.LivenessProbeType]
        http_get: Optional[HttpGet]
        tcp_socket: Optional[TcpSocket]
        exec: Optional[Exec]

    """

    initial_delay_seconds: Optional[StrictInt] = Field(
        1, description="Seconds to wait before starting probes.", title="Initial Delay (s)"
    )
    period_seconds: Optional[StrictInt] = Field(
        10, description="Frequency of probe execution.", title="Probe Interval (s)"
    )
    timeout_seconds: Optional[StrictInt] = Field(
        1, description="Seconds before the probe times out.", title="Timeout (s)"
    )
    failure_threshold: Optional[StrictInt] = Field(
        3, description="Failures before restarting the container.", title="Failure Threshold"
    )
    type: Optional[enum.LivenessProbeType] = None
    http_get: Optional[HttpGet] = Field(
        None, description="Performs an HTTP GET request to check health.", title="HTTP GET Probe"
    )
    tcp_socket: Optional[TcpSocket] = Field(None, description="Checks if a TCP port is open.", title="TCP Socket Probe")
    exec: Optional[Exec] = Field(
        None, description="Runs a command inside the container to check health.", title="Exec Probe"
    )


class HealthCheck(DataModelBase):
    """
    HealthCheck object.

    Parameters
    ----------
        liveness_probe: Optional[LivenessProbe]

    """

    liveness_probe: Optional[LivenessProbe] = None


class Requests(DataModelBase):
    """
    Requests object.

    Parameters
    ----------
        cpu: Optional[StrictStr]
        memory: Optional[StrictStr]

    """

    cpu: Optional[StrictStr] = Field(None, description="Minimum CPU required.", title="CPU Request")
    memory: Optional[StrictStr] = Field(None, description="Minimum memory required.", title="Memory Request")


class Limits(DataModelBase):
    """
    Limits object.

    Parameters
    ----------
        cpu: Optional[StrictStr]
        memory: Optional[StrictStr]

    """

    cpu: Optional[StrictStr] = Field(None, description="Maximum CPU allowed.", title="CPU Limit")
    memory: Optional[StrictStr] = Field(None, description="Maximum memory allowed.", title="Memory Limit")


class Resources(DataModelBase):
    """
    Resources object.

    Parameters
    ----------
        requests: Optional[Requests]
        limits: Optional[Limits]

    """

    requests: Optional[Requests] = Field(None, title="Resource Requests")
    limits: Optional[Limits] = None


class EnvironmentVar(DataModelBase):
    """
    EnvironmentVar object.

    Parameters
    ----------
        name: Optional[StrictStr]
        value: Optional[StrictStr]

    """

    name: Optional[StrictStr] = Field(None, description="Name of the environment variable.", title="Variable Name")
    value: Optional[StrictStr] = Field(None, description="Value of the environment variable.", title="Variable Value")


class Host(DataModelBase):
    """
    Host object.

    Parameters
    ----------
        port: StrictInt

    """

    port: StrictInt = Field(..., description="Port on the host machine.", title="Host Port")


class Service(DataModelBase):
    """
    Service object.

    Parameters
    ----------
        port: StrictInt
        container_port: Optional[StrictInt]
        exposed: Optional[StrictBool]
        exposed_port: Optional[StrictInt]

    """

    port: StrictInt = Field(..., description="Port exposed by the service.", title="Service Port")
    container_port: Optional[StrictInt] = Field(
        None, description="Port exposed by the container.", title="Container Port"
    )
    exposed: Optional[StrictBool] = Field(False, description="Expose the port outside the cluster.", title="Exposed")
    exposed_port: Optional[StrictInt] = Field(
        None, description="Port exposed outside the cluster.", title="Exposed Port"
    )


class Port(DataModelBase):
    """
    Port object.

    Parameters
    ----------
        name: Optional[StrictStr]
        type: Optional[enum.PortType]
        host: Optional[Host]
        service: Optional[Service]

    """

    name: Optional[StrictStr] = Field(None, description="Name identifier for the port.", title="Port Name")
    type: Optional[enum.PortType] = None
    host: Optional[Host] = Field(None, title="Host Configuration")
    service: Optional[Service] = Field(None, title="Service Configuration")


class Text(DataModelBase):
    """
    Text object.

    Parameters
    ----------
        data: StrictStr
        base64: Optional[StrictBool]
        encoding: Optional[enum.VolumeEncoding]

    """

    data: StrictStr = Field(..., description="Text content of the volume.", title="Data")
    base64: Optional[StrictBool] = Field(False, description="Data is base64 encoded.", title="Base64 Encoded")
    encoding: Optional[enum.VolumeEncoding] = None


class HostModel(DataModelBase):
    """
    HostModel object.

    Parameters
    ----------
        source: StrictStr

    """

    source: StrictStr = Field(..., description="Path on the host machine.", title="Source Path")


class Volume(DataModelBase):
    """
    Volume object.

    Parameters
    ----------
        name: Optional[StrictStr]
        target: Optional[StrictStr]
        type: Optional[enum.VolumeType]
        text: Optional[Text]
        host: Optional[HostModel]

    """

    name: Optional[StrictStr] = Field(None, description="Name identifier for the volume.", title="Volume Name")
    target: Optional[StrictStr] = Field(None, description="Path where the volume is mounted.", title="Mount Path")
    type: Optional[enum.VolumeType] = None
    text: Optional[Text] = Field(None, title="Text Volume")
    host: Optional[HostModel] = Field(None, title="Host Volume")


class System(DataModelBase):
    """
    System object.

    Parameters
    ----------
        health_check: Optional[HealthCheck]
        resources: Optional[Resources]
        privileged: Optional[StrictBool]
        environment_vars: Optional[List[EnvironmentVar]]
        ports: Optional[List[Port]]
        volumes: Optional[List[Volume]]

    """

    health_check: Optional[HealthCheck] = Field(None, title="Health Check")
    resources: Optional[Resources] = Field(None, title="Resource Configuration")
    privileged: Optional[StrictBool] = Field(False, description="Run the container in privileged mode.")
    environment_vars: Optional[List[EnvironmentVar]] = Field(
        None, description="List of environment variables.", title="Environment Variables"
    )
    ports: Optional[List[Port]] = Field(
        None, description="List of ports exposed by the container.", title="Container Ports"
    )
    volumes: Optional[List[Volume]] = Field(
        None, description="List of volumes mounted by the container.", title="Volumes"
    )


class DeploymentModel(DataModelBase):
    """
    DeploymentModel object.

    Parameters
    ----------
        max_resources: Optional[StrictInt]
        deployment_type: Optional[enum.DeploymentType]
        target: Optional[DeploymentTarget]

    """

    max_resources: Optional[StrictInt] = Field(
        1, description="Maximum number of resources that a single workload handles when deploying the application."
    )
    deployment_type: Optional[enum.DeploymentType] = None
    target: Optional[DeploymentTarget] = None


class IoDatastreamMappingItem(DataModelBase):
    """
    IoDatastreamMappingItem object.

    Parameters
    ----------
        io: StrictStr
        datastream: StrictStr

    """

    io: StrictStr = Field(..., description="Name of the input/output used in the Application.")
    datastream: StrictStr = Field(
        ..., description="Name of the Data Stream linked to the input/output in the Application."
    )


class App(DataModelBase):
    """
    App object.

    Parameters
    ----------
        configuration: Optional[Dict[str, Any]]
        io_datastream_mapping: Optional[List[IoDatastreamMappingItem]]

    """

    configuration: Optional[Dict[str, Any]] = None
    io_datastream_mapping: Optional[List[IoDatastreamMappingItem]] = Field(
        None, description="Mapping of Application inputs and outputs to Data Streams."
    )


class Defaults(DataModelBase):
    """
    Defaults object.

    Parameters
    ----------
        deployment: Optional[DeploymentModel]
        app: Optional[App]
        system: Optional[System]

    """

    deployment: Optional[DeploymentModel] = Field(None, description="Default rules for application deployment.")
    app: Optional[App] = None
    system: Optional[System] = None


class AppManifest(AppVersion):
    """
    AppManifest object.

    Parameters
    ----------
        schemas: Optional[Schemas]
        defaults: Optional[Defaults]

    """

    schemas: Optional[Schemas] = None
    defaults: Optional[Defaults] = None
