from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.api.client.data_model import DataModelBase

from . import enum


class ErrorObject(DataModelBase):
    """
    ErrorObject object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        solution: Optional[StrictStr]
        payload: Optional[Union[Dict[str, Any], List[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]]]

    """

    name: Optional[StrictStr] = Field(None, description="ID of the error.")
    title: Optional[StrictStr] = Field(None, description="Title of the error.")
    description: Optional[StrictStr] = Field(None, description="A description of what the problem may be.")
    solution: Optional[StrictStr] = Field(None, description="A possible solution to the problem.")
    payload: Optional[
        Union[Dict[str, Any], List[Union[StrictInt, StrictFloat, StrictStr, StrictBool, Dict[str, Any]]]]
    ] = Field(
        None,
        description="Optional additional information. For example an array of objects listing all the errors that triggered the 4XX response.",
    )


class Error(DataModelBase):
    """
    Error object.

    Parameters
    ----------
        errors: Optional[List[ErrorObject]]

    """

    errors: Optional[List[ErrorObject]] = Field(
        None, description="An array of all errors detected during the validation."
    )


class ErrorModel(DataModelBase):
    """
    ErrorModel object.

    Parameters
    ----------
        name: Optional[StrictStr]
        title: Optional[StrictStr]
        description: Optional[StrictStr]
        solution: Optional[StrictStr]
        payload: Optional[List[Dict[str, Any]]]
        type: Optional[enum.ErrorLegacyType]

    """

    name: Optional[StrictStr] = Field(None, description="Unique identifier name of the error.")
    title: Optional[StrictStr] = Field(None, description="The Display name (title) of the error.")
    description: Optional[StrictStr] = Field(None, description="Description of what the error is about.")
    solution: Optional[StrictStr] = Field(None, description="Possible solutions to resolve the error.")
    payload: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="A dictionary of all the individual error names, error titles, descriptions and solutions within the submitted information.",
    )
    type: Optional[enum.ErrorLegacyType] = None


class ErrorLegacy(DataModelBase):
    """
    ErrorLegacy object.

    Parameters
    ----------
        errors: Optional[List[ErrorModel]]

    """

    errors: Optional[List[ErrorModel]] = Field(
        None, description="An array of all errors detected during the validation."
    )
