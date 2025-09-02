"""
Utilities.
"""

from __future__ import annotations

import contextlib
import ipaddress
import json
import os
import random
import re
from datetime import timedelta
from functools import wraps
from io import IOBase
from itertools import islice, zip_longest
from mimetypes import guess_type
from operator import itemgetter
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import AnyUrl

from kelvin.krn import (
    KRN,
    KRNApp,
    KRNAppVersion,
    KRNAsset,
    KRNAssetDataQuality,
    KRNAssetDataStream,
    KRNAssetDataStreamDataQuality,
    KRNAssetMetric,
    KRNAssetParameter,
    KRNDatastream,
    KRNJob,
    KRNParameter,
    KRNRecommendation,
    KRNSchedule,
    KRNServiceAccount,
    KRNUser,
    KRNWorkload,
    KRNWorkloadAppVersion,
)

if TYPE_CHECKING:
    import pandas as pd

T = TypeVar("T")
FileTuple = Tuple[Optional[str], Union[IOBase, bytes], Optional[str]]

MICROSECOND = int(1e6)
SCALE = {
    "h": 60 * 60 * MICROSECOND,
    "m": 60 * MICROSECOND,
    "s": 1 * MICROSECOND,
    "ms": MICROSECOND // 1000,
    "us": 1,
}


def duration(x: timedelta) -> str:
    """Convert to Go Duration."""

    microseconds = int(x.total_seconds() * MICROSECOND)
    if not microseconds:
        return "0s"

    result: List[str] = []
    if microseconds < 0:
        microseconds *= -1
        result += ["-"]

    for unit, scale in SCALE.items():
        value, microseconds = divmod(microseconds, scale)
        if value:
            result += [f"{value}{unit}"]
        if not microseconds:
            break

    return "".join(result)


def snake_name(name: str) -> str:
    """Create underscore-separated name from camel-case."""

    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


@contextlib.contextmanager
def chdir(path: Optional[Path]) -> Iterator[None]:
    """Changes working directory and returns to previous on exit."""

    if path is None:
        yield
    else:
        prev_cwd = Path.cwd()
        try:
            os.chdir(path if path.is_dir() else path.parent)
            yield
        finally:
            os.chdir(prev_cwd)


def relative_to_home(path: Path) -> Path:
    """Make path relative to HOME."""

    try:
        return Path("~").joinpath(path.relative_to(Path.home()))
    except ValueError:
        return path


def update(data: MutableMapping[str, Any], *more: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Merge mappings into data."""

    if data is None:
        data = {}

    for x in more:
        for k, v in x.items():
            if isinstance(v, Mapping):
                update(data.setdefault(k, {}), v)
            else:
                data[k] = v

    return data


def merge(*args: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
    """Merge dictionaries."""

    result: Dict[str, Any] = {}

    if kwargs:
        args += (kwargs,)

    for arg in args:
        if arg is None:
            continue
        for k, v in arg.items():
            result[k] = merge(result.get(k) or {}, v) if isinstance(v, Mapping) else v

    return result


def _make_key(k: str, q: str, sep: str = ".") -> str:
    """Make flattened key."""

    if not q:
        return k

    if not q.startswith("["):
        k += sep

    return f"{k}{q}"


def flatten(x: Any, sep: str = ".", sequence: bool = True) -> List[Tuple[str, Any]]:
    """Flatten nested mappings and sequences."""

    # basic conversions
    if isinstance(x, Mapping):
        x = x.items()
    elif sequence and isinstance(x, Sequence) and not isinstance(x, str):
        x = ((f"[{i}]", v) for i, v in enumerate(x))
    else:
        return [("", x)]

    return [(_make_key(k, q, sep), w) for k, v in x for q, w in flatten(v, sep, sequence)]


def inflate(x: Iterable[Tuple[str, Any]], separator: str = ".") -> Dict[str, Any]:
    """Re-inflate flattened keys into nested object."""

    result: Dict[str, Any] = {}
    inputs: List[Tuple[Sequence[Union[int, str]], Any]] = []

    delims = re.compile("|".join(re.escape(x) for x in [separator, "[", "]"]))

    for key_, value_ in x:
        split_key: List[Union[int, str]] = [
            int(k) if k.isnumeric() else k for k in delims.split(key_) if k and not delims.match(k)
        ]
        inputs += [(split_key, value_)]

    root: Any

    for key, value in sorted(inputs, key=itemgetter(0)):
        root = result
        for k, l in zip_longest(key, key[1:]):
            if isinstance(k, str):
                if not isinstance(root, Dict):
                    raise ValueError("Invalid structure")

                if k not in root:
                    if isinstance(l, str):
                        root[k] = {}
                    elif isinstance(l, int):
                        root[k] = []
            else:
                if not isinstance(root, List):
                    raise ValueError("Invalid structure")

                n = len(root)
                if k > n:
                    if isinstance(l, str):
                        root += [{} for _ in range(k - n + 1)]
                    elif isinstance(l, int):
                        root += [[] for _ in range(k - n + 1)]
                    else:
                        root += [None] * (k - n + 1)

            if l is None:
                root[k] = value
            else:
                root = root[k]

    return result


def chunks(x: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    """Yield successive n-sized chunks from l."""

    for i in range(0, len(x), n):
        yield x[i : (i + n)]


def map_chunks(chunk_size: int, f: Callable[..., Any], x: Iterable[T], **kwargs: Any) -> Iterator[Any]:
    """Map function to chunks or iterable."""

    while True:
        result = f(islice(x, chunk_size), **kwargs)
        if result is None:
            break
        yield result


def deep_itemgetter(path: str) -> Callable[[str], Any]:
    """Deep itemgetter, halting on first ``None``"""

    if "." not in path:
        return itemgetter(path)

    def getter(x: Any) -> Any:
        if x is None:
            return None
        for key in path.split("."):
            x = x[key]
            if x is None:
                break
        return x

    return getter


def file_tuple(x: Union[str, IOBase, bytes, Tuple]) -> FileTuple:
    """Create file tuple for multipart request."""

    if isinstance(x, tuple):
        name, data, *tail = x
        if not tail:
            mime_type = None
        elif len(tail) == 1:
            mime_type = tail[0]
        else:
            raise ValueError("Too many values")
    else:
        if isinstance(x, str):
            name = x
            data = open(x, "rb")
        elif isinstance(x, IOBase):
            name = getattr(x, "name", None)
            data = x
        else:
            name = None
            data = x

        mime_type = None

    if mime_type is None and name is not None:
        mime_type = guess_type(name)

    return (name, data, mime_type)


def metadata_tuple(x: Dict[str, Any]) -> Tuple[None, str]:
    """Convert metadata string to tuple.

    Args:
        x (Dict[str, Any]): Metadata string to be converted to tuple

    Returns:
        Tuple[None, str]: Tuple with None and metadata string
    """
    return (None, json.dumps(x))


def parse_resource(resource: Union[KRN, str]) -> Dict[str, str]:
    if isinstance(resource, str):
        krn_resource = KRN.from_string(resource)
    else:
        krn_resource = resource
    result: Dict[str, str] = {}
    if isinstance(krn_resource, KRNAssetDataStream):
        asset_name = krn_resource.asset
        datastream_name = krn_resource.data_stream
        result["asset_name"] = asset_name
        result["datastream_name"] = datastream_name
    elif isinstance(krn_resource, KRNAsset):
        asset_name = krn_resource.asset
        result["asset_name"] = asset_name
    elif isinstance(krn_resource, KRNAssetMetric):
        asset_name = krn_resource.asset
        metric_name = krn_resource.metric
        result["asset_name"] = asset_name
        result["metric_name"] = metric_name
    elif isinstance(krn_resource, KRNAssetParameter):
        asset_name = krn_resource.asset
        parameter_name = krn_resource.parameter
        result["asset_name"] = asset_name
        result["parameter_name"] = parameter_name
    elif isinstance(krn_resource, KRNDatastream):
        datastream_name = krn_resource.datastream
        result["datastream_name"] = datastream_name
    elif isinstance(krn_resource, KRNApp):
        app = krn_resource.app
        result["app_name"] = app
    elif isinstance(krn_resource, KRNAppVersion):
        app = krn_resource.app
        version = krn_resource.version
        result["app_name"] = app
        result["app_version"] = version
    elif isinstance(krn_resource, KRNParameter):
        parameter_name = krn_resource.parameter
        result["parameter_name"] = parameter_name
    elif isinstance(krn_resource, KRNRecommendation):
        recommendation_id = krn_resource.recommendation_id
        result["recommendation_id"] = recommendation_id
    elif isinstance(krn_resource, KRNJob):
        job = krn_resource.job
        job_run_id = krn_resource.job_run_id
        result["job_id"] = job
        result["job_run_id"] = job_run_id
    elif isinstance(krn_resource, KRNSchedule):
        schedule = krn_resource.schedule
        result["schedule"] = schedule
    elif isinstance(krn_resource, KRNServiceAccount):
        service_account = krn_resource.service_account
        result["service_account"] = service_account
    elif isinstance(krn_resource, KRNUser):
        user = krn_resource.user
        result["user"] = user
    elif isinstance(krn_resource, KRNAssetDataStreamDataQuality):
        splitted_krn = str(krn_resource).split(":")
        asset_datastream = splitted_krn[-1].split("/")
        data_quality = splitted_krn[2]
        asset_name = asset_datastream[0]
        datastream_name = asset_datastream[1]
        result["data_quality"] = f"dq:{data_quality}:{datastream_name}"
        result["asset_name"] = asset_name
    elif isinstance(krn_resource, KRNAssetDataQuality):
        splitted_krn = str(krn_resource).split(":")
        asset = splitted_krn[-1]
        data_quality = splitted_krn[2]
        result["data_quality"] = f"dq:{data_quality}"
        result["asset_name"] = asset

    return result


def get_exponential_backoff(retry_delay: float) -> Tuple[float, float]:
    """Get exponential backoff parameters.

    Args:
        retry_delay (float): Initial retry delay

    Returns:
        Tuple[float, float]: Exponential backoff parameters
    """
    delta = 0.5 * retry_delay

    retry_delay *= 1.5

    if retry_delay > 60:
        retry_delay = 60

    min_retry_delay = retry_delay - delta
    max_retry_delay = retry_delay + delta
    retry_delay_with_jitter = min_retry_delay + (random.uniform(0, 1) * (max_retry_delay - min_retry_delay + 1))
    return retry_delay, retry_delay_with_jitter


def get_host_type(url: AnyUrl) -> str:
    """
    Return 'ipv4' if url.host is a valid IPv4 address,
    'ipv6' if it's a valid IPv6 address,
    or 'domain' otherwise.
    """
    host = url.host
    if not host:
        return "unknown"

    try:
        parsed = ipaddress.ip_address(host)
        if isinstance(parsed, ipaddress.IPv4Address):
            return "ipv4"
        else:
            return "ipv6"
    except ValueError:
        # If ip_address() raises ValueError, it's not a valid IP address => domain
        return "domain"


def get_innermost_model_type(annotation: Any) -> Any:
    """
    Safely extract the inner model type from annotations like:
      Optional[List[MyModel]], Optional[MyModel], List[MyModel], etc.
    """
    # If it's Union (i.e., Optional[T] => Union[T, NoneType]), unwrap None:
    if get_origin(annotation) is Union:
        union_args = get_args(annotation)
        # Typically we want the non-NoneType argument
        non_none_args = [arg for arg in union_args if arg is not type(None)]
        # For Optional[T], there's only one non-None type
        if len(non_none_args) == 1:
            annotation = non_none_args[0]  # e.g. List[Asset]

    # If it's List[...] or another generic, unwrap that
    if get_origin(annotation) is list:
        (inner_type,) = get_args(annotation)  # e.g. Asset
        return inner_type

    if get_origin(annotation) is Optional:
        (inner_type,) = get_args(annotation)
        return inner_type
    # Otherwise, it's presumably already the model type
    return annotation
