"""
Kelvin API Client 2.
"""

from .base_client import ClientConfiguration, History
from .client import MODELS, Client
from .data_model import DataModelBase
from .error import ClientError
from .version import version as __version__

__all__ = ["Client", "ClientConfiguration", "ClientError", "History", "DataModelBase", *MODELS]

locals().update(MODELS)

del MODELS
