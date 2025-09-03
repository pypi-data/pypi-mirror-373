from typing import Any

from typing_extensions import Self, override

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import (
    ModelFramework,
    HUGGINGFACE_FRAMEWORK_FORMAT,
)
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class HuggingfaceModelVersionManager(BaseModelVersionManager):
    """
    A logger for Huggingface models that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.HUGGINGFACE
    _SERIALIZATION_FORMAT = HUGGINGFACE_FRAMEWORK_FORMAT

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        try:
            import transformers

            return transformers.__version__
        except Exception as e:
            raise FrogmlException(f"Failed to get transformers version: {e}")

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        if not isinstance(model, tuple):
            raise FrogmlException("Model must be a tuple containing (model, tokenizer)")

        model_obj, tokenizer = model  # Assuming model is a tuple of (model, tokenizer)
        model_obj.save_pretrained(config.full_model_path)
        tokenizer.save_pretrained(config.full_model_path)
