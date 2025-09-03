from typing import Any

import joblib
from typing_extensions import Self, override

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import (
    ModelFramework,
    SCIKIT_LEARN_FRAMEWORK_FORMAT,
)
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class ScikitLearnModelVersionManager(BaseModelVersionManager):
    """
    A logger for Scikit-Learn models that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.SCIKIT_LEARN
    _SERIALIZATION_FORMAT = SCIKIT_LEARN_FRAMEWORK_FORMAT

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        try:
            import sklearn

            return sklearn.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get sklearn version: {e}")

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        joblib.dump(model, config.full_model_path)
