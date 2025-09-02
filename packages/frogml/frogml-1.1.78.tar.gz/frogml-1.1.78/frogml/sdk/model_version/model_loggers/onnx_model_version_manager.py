from typing import Any

from typing_extensions import Self, override

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework, ONNX_FRAMEWORK_FORMAT
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class OnnxModelVersionManager(BaseModelVersionManager):
    """
    A logger for Onnx models that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.ONNX
    _SERIALIZATION_FORMAT = ONNX_FRAMEWORK_FORMAT

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        try:
            import onnx

            return onnx.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get onnx version: {e}")

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        import onnx

        onnx.save_model(model, config.full_model_path)
