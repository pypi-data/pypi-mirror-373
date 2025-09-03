from pathlib import Path
from typing import Any

from typing_extensions import Self, override

from frogml.sdk.model_version.constants import ModelFramework
from frogml.sdk.model_version.model_loggers.base_model_version_manager import (
    BaseModelVersionManager,
)
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig


class FilesModelVersionManager(BaseModelVersionManager):
    """
    A logger for models stored in files that can be used
    to log model metadata and other relevant information.
    This class is a placeholder and can be extended
    with specific logging functionalities as needed.
    """

    _MODEL_FRAMEWORK = ModelFramework.FILES

    def __init__(self: Self, source_path: str):
        super().__init__()
        self._SERIALIZATION_FORMAT = self.__get_file_extension(source_path)

    @override
    def _import_and_get_framework_version(self: Self) -> str:
        self._logger.debug("No framework version to import for FILES.")

        return ""

    @override
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        self._logger.debug(
            "Skipping model saving to any file since it's already a file."
        )

    @staticmethod
    def __get_file_extension(file_path: str) -> str:
        """
        Get file extension
        :param file_path: File path
        :return: File extension
        """
        suffix: str = Path(file_path).suffix

        if suffix:
            suffix = suffix[1:]

        return suffix
