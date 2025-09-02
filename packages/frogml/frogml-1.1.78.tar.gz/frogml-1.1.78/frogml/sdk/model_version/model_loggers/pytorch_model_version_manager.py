from typing import Any

from typing_extensions import Self, override

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework, PYTORCH_FRAMEWORK_FORMAT
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class PytorchModelVersionManager(BaseModelVersionManager):
    """
    A logger for Pytorch models that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.PYTORCH
    _SERIALIZATION_FORMAT = PYTORCH_FRAMEWORK_FORMAT

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        try:
            import torch

            return torch.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get torch version: {e}")

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        import torch
        from frogml.sdk.model_version.pytorch import (
            pickle_module as pytorch_pickle_module,
        )

        torch.save(
            obj=model, f=config.full_model_path, pickle_module=pytorch_pickle_module
        )  # nosec B614
