__author__ = "jfrog"
__version__ = "1.1.80"

from frogml.sdk.model.decorators.api import api_decorator as api
from frogml.sdk.model_loggers.model_logger import load_model, log_model
from frogml.sdk.frogml_client.client import FrogMLClient
from frogml.sdk.model.base import BaseModel as FrogMlModel

from frogml.core.model_loggers.artifact_logger import (
    load_file,
    log_file,
)
from frogml.core.model_loggers.data_logger import load_data, log_data
from frogml.sdk.model.decorators.timer import frogml_timer
from frogml.sdk.model.model_version_tracking import (
    log_metric,
    log_param,
)
from frogml.sdk.model_version import *

from frogml.core.inner.di_configuration import wire_dependencies

_container = wire_dependencies()
