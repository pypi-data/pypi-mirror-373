from __future__ import annotations

from typing import List, Optional

from pydantic import Field, StrictStr

from kelvin.api.client.data_model import DataModelBase
from kelvin.krn import KRN


class App(DataModelBase):
    """
    App object.

    Parameters
    ----------
        name: StrictStr
        version: Optional[StrictStr]

    """

    name: StrictStr = Field(
        ...,
        description="A filter on the list based on the key `app_name`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    version: Optional[StrictStr] = Field(
        None,
        description="A filter on the list based on the key `app_version`. The filter is on the full name only. The string can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )


class AppVersionParameterListBase(DataModelBase):
    """
    AppVersionParameterListBase object.

    Parameters
    ----------
        apps: Optional[List[App]]
        resources: Optional[List[KRN]]
        parameter_names: Optional[List[StrictStr]]

    """

    apps: Optional[List[App]] = Field(
        None,
        description="A filter on the list for Apps and its Versions. Multiple Apps and Versions can be given. All App Versions in the array are treated as `OR`.",
    )
    resources: Optional[List[KRN]] = Field(
        None,
        description="A filter on the list showing only current Parameter values associated with any Assets in the array. The filter is on the full name only. All strings in the array are treated as `OR`. Each Asset name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
    parameter_names: Optional[List[StrictStr]] = Field(
        None,
        description="A filter on the list for Parameters. The filter is on the full name only. All strings in the array are treated as `OR`. Each Parameter name can only contain lowercase alphanumeric characters and `.`, `_` or `-` characters.",
    )
