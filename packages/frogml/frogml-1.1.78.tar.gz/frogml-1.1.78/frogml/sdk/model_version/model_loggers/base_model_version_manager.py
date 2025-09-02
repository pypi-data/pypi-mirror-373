import tempfile
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, Dict, List, Any

from pydantic import ValidationError
from typing_extensions import Self

from frogml.core.exceptions import FrogmlException
from frogml.core.inner.singleton_meta import SingletonABCMeta
from frogml.core.tools.logger import get_frogml_logger
from frogml.sdk.model_version.constants import ModelFramework, STORAGE_MODEL_ENTITY_TYPE
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig
from frogml.sdk.model_version.utils.storage import _log_model
from frogml.storage.exceptions.validation_error import FrogMLValidationError
from frogml.storage.frog_ml import FrogMLStorage


class BaseModelVersionManager(ABC, metaclass=SingletonABCMeta):
    """
    Base class for model loggers.
    This class provides a common interface for logging model-related information.
    """

    _MODEL_FRAMEWORK: ModelFramework
    _SERIALIZATION_FORMAT: str

    def __init__(self: Self):
        self._logger: Logger = get_frogml_logger(type(self).__name__)

    def log_model_to_artifactory(
        self: Self,
        model: Any,
        repository: str,
        model_name: str,
        version: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        dependencies: Optional[List[str]] = None,
        code_dir: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        predict_file: Optional[str] = None,
        model_path: Optional[str] = None,
        register_in_jml: bool = True,
    ):
        """
        Log model to a repository in Artifactory.
        :param model: The model to be logged
        :param repository: Repository to log the model to
        :param model_name: The model's name
        :param version: The model's version
        :param properties: The model's properties
        :param dependencies: Model dependencies path
        :param code_dir: Model code directory path
        :param parameters: Model parameters
        :param metrics: Model metrics
        :param predict_file: Path to the predict file
        :param model_path: Path to the model file (for file-based models)
        :param register_in_jml: Whether to register the model as a registered model to JML.
        :return: None
        """
        self._logger.debug("About to import and define framework version")
        framework_version: str = self._import_and_get_framework_version()

        with tempfile.TemporaryDirectory() as target_dir:
            self._logger.debug("Temporary directory created at %s", target_dir)
            model_log_config: ModelLogConfig = self._build_model_log_config(
                repository=repository,
                model_name=model_name,
                version=version,
                properties=properties,
                dependencies=dependencies,
                code_dir=code_dir,
                parameters=parameters,
                metrics=metrics,
                predict_file=predict_file,
                model_path=model_path,
                target_dir=target_dir,
                framework_version=framework_version,
                register_in_jml=register_in_jml,
            )
            self._logger.info(
                "Logging model %s to %s",
                model_log_config.model_name,
                model_log_config.repository,
            )
            self._save_model(model=model, config=model_log_config)

            try:
                _log_model(config=model_log_config)
            except Exception as e:
                self._logger.error(
                    "An error occurred while logging model %s to %s",
                    model_name,
                    repository,
                )
                raise FrogmlException(f"An error occurred: {e}") from e

    def get_model_info_from_artifactory(
        self: Self, repository: str, model_name: str, model_version: str
    ) -> Dict:
        """
        Get model information
        :param repository: Repository key where the model is stored
        :param model_name: The model's name
        :param model_version: The model's version
        :return: The model information as a dictionary
        """
        self._logger.info(f"Getting model {model_name} information from {repository}")
        return FrogMLStorage().get_entity_manifest(
            entity_type=STORAGE_MODEL_ENTITY_TYPE,
            repository=repository,
            entity_name=model_name,
            version=model_version,
            namespace=None,
        )

    @abstractmethod
    def _import_and_get_framework_version(self: Self) -> str:
        """
        Import the framework required for logging the model.
        This method should be implemented by subclasses to import the specific framework.
        """
        ...

    @abstractmethod
    def _save_model(self: Self, model: Any, config: ModelLogConfig):
        """
        Save the model using the provided configuration.
        This method should be implemented by subclasses to handle the saving logic.
        """
        ...

    def _build_model_log_config(
        self: Self,
        repository: str,
        model_name: str,
        version: Optional[str],
        properties: Optional[Dict[str, str]],
        dependencies: Optional[List[str]],
        code_dir: Optional[str],
        parameters: Optional[Dict[str, Any]],
        metrics: Optional[Dict[str, Any]],
        predict_file: Optional[str],
        model_path: Optional[str],
        target_dir: str,
        framework_version: str,
        register_in_jml: bool = True,
    ) -> ModelLogConfig:
        """Build and return a ModelLogConfig instance with the provided model logging parameters.

        This method creates a configuration for logging
        a model by initializing a ModelLogConfig instance with the specified values.
        If validation fails during configuration creation,
        a FrogMLValidationError is raised with detailed errors.
        """
        self._logger.debug("Creating model log configuration")

        try:
            return ModelLogConfig(
                model_name=model_name,
                target_dir=target_dir,
                model_framework=self._MODEL_FRAMEWORK,
                framework_version=framework_version,
                serialization_format=self._SERIALIZATION_FORMAT,
                repository=repository,
                version=version,
                properties=properties,
                dependencies=dependencies,
                code_dir=code_dir,
                parameters=parameters,
                metrics=metrics,
                predict_file=predict_file,
                model_path=model_path,
                register_in_jml=register_in_jml,
            )
        except ValidationError as ve:
            errors: dict[str, str] = {"errors": ve.json()}

            error_message: str = (
                f"Model log configuration validation failed for model '{model_name}' "
                f"in repository '{repository}'. Validation errors: '{errors['errors']}'"
            )

            raise FrogMLValidationError(error_message, errors=errors) from ve
