from typing import Any

from typing_extensions import Self, override

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework, CATBOOST_SERIALIZED_TYPE
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class CatboostModelVersionManager(BaseModelVersionManager):
    """
    A logger for Catboost models that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.CATBOOST
    _SERIALIZATION_FORMAT = CATBOOST_SERIALIZED_TYPE

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        try:
            import catboost

            return catboost.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get catboost version: {e}")

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        model.save_model(config.full_model_path, format=CATBOOST_SERIALIZED_TYPE)
