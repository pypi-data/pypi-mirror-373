"""
Data Model.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Generic, Iterator, List, Mapping, Sequence, TypeVar, Union, get_args, get_origin

import structlog
from pydantic import ConfigDict, ValidationError, ValidationInfo, field_validator

from .base_model import BaseModel
from .utils import get_innermost_model_type, parse_resource

if TYPE_CHECKING:
    import pandas as pd


logger = structlog.get_logger(__name__)

T = TypeVar("T")


class DataModel(BaseModel):
    """Model base-class."""

    if TYPE_CHECKING:
        fields: Any
        schema: Any
    model_config: ConfigDict = ConfigDict(extra="allow", populate_by_name=True)

    def __init__(self, **kwargs: Any) -> None:
        """Initialise model."""

        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith("_"):
            return super().__getattribute__(name)

        try:
            result = super().__getattribute__(name)
        except AttributeError:
            if "_" in name:
                # fall back to attribute on child field
                head, tail = name.rsplit("_", 1)
                if head in self.model_fields:
                    head = getattr(self, head)
                    try:
                        return getattr(head, tail)
                    except AttributeError:
                        pass
            raise

        return KList(result) if isinstance(result, list) else result

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""

        if name.startswith("_"):
            super().__setattr__(name, value)

        try:
            super().__setattr__(name, value)
        except ValueError:
            if "_" in name:
                # fall back to attribute on child field
                head, tail = name.rsplit("_", 1)
                if head in self.model_fields:
                    head = getattr(self, head)
                    try:
                        setattr(head, tail, value)
                    except ValueError:
                        pass
                    else:
                        return
            raise

    @field_validator("*", mode="before")
    def convert_datetime(cls, value: Any, info: ValidationInfo) -> Any:
        """Correct data-type for datetime values."""

        if not isinstance(value, datetime):
            return value
        field_type = get_innermost_model_type(cls.model_fields[info.field_name].annotation)

        if not isinstance(field_type, type):
            return value

        if issubclass(field_type, str):
            suffix = "Z" if value.microsecond else ".000000Z"
            return value.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + suffix
        elif issubclass(field_type, float):
            return value.timestamp()
        elif issubclass(field_type, int):
            return int(value.timestamp() * 1e9)
        else:
            return value


P = TypeVar("P", bound=DataModel)


class PaginatorDataModel(DataModel, Generic[P]):
    """Paginator data-model."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialise model."""

        super().__init__(**kwargs)

    @field_validator("data", mode="before", check_fields=False)
    def validate_data(cls, v: Sequence[Mapping[str, Any]], info: ValidationInfo) -> List[P]:
        """Validate data field."""

        T = get_innermost_model_type(cls.model_fields[info.field_name].annotation)
        results = []

        for item in v:
            try:
                results += [T(**item)]
            except ValidationError as e:
                logger.warning("Skipped invalid item", name=T.__name__, item=item, error=e)

        return results

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Get item."""

        if isinstance(item, int):
            return self.data[item]

        return super().__getitem__(item)

    def to_df(self) -> pd.DataFrame:
        """
        Converts the data in the object to a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the data.
        """
        import pandas as pd

        if len(self.data) == 0:
            return pd.DataFrame()

        headers: List[str] = sorted(list(self.data[0].model_dump().keys()))
        return pd.DataFrame([item.model_dump() for item in self.data], columns=headers)


class KList(List[P]):
    """
    Represents a list of objects of DataModel type.

    This class extends the built-in List class and provides additional functionality.

    Methods:
        to_df(): Converts the list to a pandas DataFrame.

    """

    def to_df(self) -> pd.DataFrame:
        """
        Convert a list of Pydantic models into a single, wide pandas DataFrame,
        preserving all fields (strings, bools, lists, numbers, datetimes, etc.),
        exploding `resource` via parse_resource(), and flattening any dict columns.
        """
        import pandas as pd

        if not self:
            return pd.DataFrame()

        records = [item.model_dump() for item in self]
        df = pd.json_normalize(records)

        for col in df.select_dtypes(include="object"):
            try:
                parsed = pd.to_datetime(df[col], format="%Y-%m-%dT%H:%M:%S.%f%z", utc=True).dt.tz_convert("UTC")
            except (ValueError, TypeError):
                continue
            # keep it if at least 90% non‐null
            if parsed.notna().mean() > 0.9:
                df[col] = parsed

        krn_cols = []
        for col in df.select_dtypes(include="object"):
            vals = df[col].dropna().astype(str)
            # require that *all* non-null values start with "krn:" (or adjust to .any())
            if not vals.empty and vals.str.startswith("krn:").all():
                krn_cols.append(col)

        for col in krn_cols:
            parsed = df.pop(col).apply(parse_resource).apply(pd.Series)
            parsed.index = df.index
            df = pd.concat([parsed, df], axis=1)

        dict_cols = [c for c in df.columns if df[c].map(lambda v: isinstance(v, dict)).all()]
        for col in dict_cols:
            flat = pd.json_normalize(df.pop(col))
            flat.index = df.index
            # no need to prefix if you know there are no name collisions
            df = pd.concat([flat, df], axis=1)

        date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
        df = df.sort_values(by=date_cols)
        dt_first = sorted(date_cols)
        others = sorted([c for c in df.columns if c not in date_cols])
        new_order = dt_first + others
        df = df[new_order]
        return df


class KIterator(Iterator[P]):
    """
    An iterator class that wraps another iterator and provides additional functionality.

    Args:
        iterator (Iterator[Any]): The iterator to be wrapped.

    Attributes:
        iterator (Iterator[Any]): The wrapped iterator.

    Methods:
        __iter__(): Returns the iterator object itself.
        __next__(): Returns the next item from the iterator.
        to_df(): Convert the iterator's data into a pandas DataFrame.

    """

    def __init__(self, iterator: Iterator[Any]) -> None:
        self.iterator: Iterator[Any] = iterator

    def __iter__(self) -> Any:
        return self.iterator.__iter__()

    def __next__(self) -> Any:
        return self.iterator.__next__()

    def to_df(self, datastreams_as_column: bool = False, data_quality_as_column: bool = False) -> pd.DataFrame:
        """
        Convert the iterator's data into a pandas DataFrame.

        By default returns long format:
            timestamp | asset_name | datastream_name | value

        If datastreams_as_column=True, returns wide format:
            timestamp | asset_name | <datastream1> | <datastream2> | …
        """
        import pandas as pd

        # build initial frame
        df = pd.DataFrame.from_records(self.iterator)
        if df.empty:
            return pd.DataFrame()

        # normalize timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("UTC")

        # explode resource into flat cols
        if "resource" in df.columns:
            resource = pd.json_normalize(df.pop("resource").apply(parse_resource))
            df = pd.concat([resource, df], axis=1)

        # now df has at least: timestamp, asset_name, datastream_name, payload, (maybe data_quality)
        # build the long form
        long_df = df[["timestamp", "asset_name", "datastream_name", "payload"]]
        if datastreams_as_column and data_quality_as_column:
            wide = long_df.pivot_table(
                index=["timestamp", "asset_name"],
                columns=["datastream_name", "data_quality"],
                values="payload",
                aggfunc="first",  # or another agg if you expect dupes
            ).reset_index()
            # flatten column index if needed
            wide.columns.name = None
            return wide

        elif datastreams_as_column:
            # pivot to wide
            wide = long_df.pivot_table(
                index=["timestamp", "asset_name"],
                columns="datastream_name",
                values="payload",
                aggfunc="first",  # or another agg if you expect dupes
            ).reset_index()
            # flatten column index if needed
            wide.columns.name = None
            return wide
        elif data_quality_as_column:
            wide = long_df.pivot_table(
                index=["timestamp", "asset_name"],
                columns="data_quality",
                values="payload",
                aggfunc="first",  # or another agg if you expect dupes
            ).reset_index()
            # flatten column index if needed
            wide.columns.name = None
            return wide

        long_df.reset_index(drop=True, inplace=True)

        return long_df


DataModelBase = DataModel
