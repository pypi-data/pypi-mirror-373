from __future__ import annotations

from enum import Enum


class AppType(Enum):
    app = "app"
    importer = "importer"
    exporter = "exporter"
    docker = "docker"


class GatewayMode(Enum):
    socket = "socket"
    legacy = "legacy"


class Way(Enum):
    output = "output"
    input_cc = "input-cc"
    input_cc_output = "input-cc+output"
    input = "input"
    output_cc = "output-cc"
    input_output_cc = "input+output-cc"


class Storage(Enum):
    node_and_cloud = "node-and-cloud"
    node = "node"
    none = "none"


class DynamicIOOwnership(Enum):
    both = "both"
    owned = "owned"
    remote = "remote"


class DynamicIOType(Enum):
    both = "both"
    data = "data"
    control = "control"


class ParameterDataType(Enum):
    string = "string"
    number = "number"
    boolean = "boolean"


class CAWay(Enum):
    input_ca = "input-ca"
    output_ca = "output-ca"


class DQWay(Enum):
    output = "output"
    input = "input"


class DeploymentType(Enum):
    standard = "standard"
    staged_instant_apply = "staged+instant-apply"
    staged_only = "staged-only"


class DeploymentTargetType(Enum):
    cluster = "cluster"
    resource_cluster = "resource-cluster"


class LivenessProbeType(Enum):
    http_get = "http_get"
    tcp_socket = "tcp_socket"
    exec = "exec"


class URIScheme(Enum):
    http = "http"
    https = "https"


class PortType(Enum):
    host = "host"
    service = "service"


class VolumeType(Enum):
    persistent = "persistent"
    host = "host"
    text = "text"


class VolumeEncoding(Enum):
    utf_8 = "utf-8"
    ascii = "ascii"
    latin_1 = "latin_1"


class AppStatus(Enum):
    running = "running"
    stopped = "stopped"
    updating = "updating"
    requires_attention = "requires_attention"


class ParameterType(Enum):
    number = "number"
    string = "string"
    boolean = "boolean"


class ParameterScheduleState(Enum):
    scheduled = "scheduled"
    scheduled_revert = "scheduled-revert"
    completed = "completed"
    error = "error"


class ParameterScheduleApplyType(Enum):
    schedule = "schedule"
    schedule_revert = "schedule-revert"


class WorkloadDownloadStatus(Enum):
    pending = "pending"
    scheduled = "scheduled"
    processing = "processing"
    downloading = "downloading"
    ready = "ready"
    failed = "failed"


class WorkloadStatus(Enum):
    pending_deploy = "pending_deploy"
    pending_update = "pending_update"
    pending_start = "pending_start"
    pending_stop = "pending_stop"
    pending_apply = "pending_apply"
    deploying = "deploying"
    running = "running"
    stopping = "stopping"
    stopped = "stopped"
    failed = "failed"
    starting = "starting"
    applying = "applying"
    received = "received"
    downloading = "downloading"
    ready = "ready"
    unreachable = "unreachable"
    staged = "staged"


class GuardrailRelativeType(Enum):
    VALUE = "value"
    PERCENTAGE = "percentage"


class AssetState(Enum):
    online = "online"
    offline = "offline"
    unknown = "unknown"


class AssetInsightsOperator(Enum):
    Equal = "=="
    NotEqual = "!="
    Lower = "<"
    Greater = ">"
    GreaterOrEqual = ">="
    LowerOrEqual = "<="
    Has = "has"
    NotHas = "!has"
    Contains = "contains"
    NotContains = "!contains"
    StartsWith = "starts_with"
    NotStartsWith = "!starts_with"
    EndsWith = "ends_with"
    NotEndsWith = "!ends_with"


class PropertyType(Enum):
    boolean = "boolean"
    number = "number"
    string = "string"
    timestamp = "timestamp"
    list_boolean_ = "list[boolean]"
    list_number_ = "list[number]"
    list_string_ = "list[string]"
    list_timestamp_ = "list[timestamp]"


class ControlChangeState(Enum):
    pending = "pending"
    ready = "ready"
    sent = "sent"
    processed = "processed"
    applied = "applied"
    failed = "failed"
    rejected = "rejected"


class CustomActionState(Enum):
    pending = "pending"
    ready = "ready"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"


class AssetInsightsAgg(Enum):
    count = "count"
    mean = "mean"
    sum = "sum"
    max = "max"
    min = "min"


class RecommendationState(Enum):
    pending = "pending"
    accepted = "accepted"
    auto_accepted = "auto_accepted"
    rejected = "rejected"
    expired = "expired"


class AssetInsightsParameterScheduleType(Enum):
    permanent = "permanent"
    temporary = "temporary"


class AssetInsightsSortByDirection(Enum):
    asc = "asc"
    desc = "desc"


class AssetInsightsState(Enum):
    online = "online"
    offline = "offline"
    unknown = "unknown"


class ControlChangeSource(Enum):
    bridge = "bridge"
    ccm = "ccm"


class CustomActionFailureReason(Enum):
    none = "none"
    other = "other"
    reported_failed = "reported_failed"
    expired = "expired"
    lost = "lost"
    executor_gone = "executor_gone"


class OutlierDetectionModel(Enum):
    z_score = "z_score"


class WindowIntervalUnit(Enum):
    sec = "sec"
    min = "min"
    hour = "hour"
    day = "day"


class DataType(Enum):
    boolean = "boolean"
    number = "number"
    object = "object"
    string = "string"


class DataStreamType(Enum):
    computed = "computed"
    measurement = "measurement"
    data_quality = "data_quality"
    set_point = "set_point"


class ClusterType(Enum):
    k3s = "k3s"
    kubernetes = "kubernetes"
    docker = "docker"


class OrchestrationClusterStatus(Enum):
    pending_provision = "pending_provision"
    pending = "pending"
    online = "online"
    unreachable = "unreachable"
    requires_attention = "requires_attention"


class UpgradeStatusState(Enum):
    idle = "idle"
    downloading = "downloading"
    ready = "ready"


class OrchestrationNodeStatus(Enum):
    online = "online"
    unreachable = "unreachable"
    not_ready = "not_ready"


class ServiceType(Enum):
    cluster_ip = "cluster_ip"
    node_port = "node_port"
    host_port = "host_port"


class RecommendationEvidenceType(Enum):
    markdown = "markdown"
    image = "image"
    iframe = "iframe"
    chart = "chart"
    line_chart = "line-chart"
    bar_chart = "bar-chart"
    dynacard = "dynacard"
    data_explorer = "data-explorer"


class RecommendationStateCreate(Enum):
    pending = "pending"
    auto_accepted = "auto_accepted"


class RecommendationActionStatus(Enum):
    none = "none"
    dispatched = "dispatched"
    dispatch_error = "dispatch_error"


class TimeseriesAgg(Enum):
    none = "none"
    count = "count"
    distinct = "distinct"
    integral = "integral"
    mean = "mean"
    median = "median"
    mode = "mode"
    spread = "spread"
    stddev = "stddev"
    sum = "sum"
    max = "max"
    min = "min"
    first = "first"
    last = "last"


class TimeseriesOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


class ResourceType(Enum):
    asset = "asset"
    datastream = "datastream"
    app = "app"
    app_parameter = "app-parameter"


class RolePolicyAction(Enum):
    field_ = "*"
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


class LegacyAppType(Enum):
    kelvin = "kelvin"
    docker = "docker"
    bridge = "bridge"


class ErrorLegacyType(Enum):
    system = "system"


class Protocol(Enum):
    TCP = "TCP"
    UDP = "UDP"
