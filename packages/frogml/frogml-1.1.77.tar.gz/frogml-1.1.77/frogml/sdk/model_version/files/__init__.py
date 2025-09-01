import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

from frogml.sdk.model_version.constants import ModelFramework
from frogml.sdk.model_version.model_loggers.files_model_version_manager import (
    FilesModelVersionManager,
)
from frogml.sdk.model_version.utils.storage_helper import _get_model_framework
from frogml.sdk.model_version.utils.validations import (
    _validate_load_model,
)
from frogml.storage.frog_ml import FrogMLStorage

_logger = logging.getLogger(__name__)


def log_model(
    source_path: str,
    repository: str,
    model_name: str,
    version: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    dependencies: Optional[List[str]] = None,
    code_dir: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    predict_file: Optional[str] = None,
    *,
    register_in_jml: bool = True,
) -> None:
    """
    Log model to a repository in Artifactory.
    :param source_path: Path to the model to be logged
    :param repository: Repository to log the model to
    :param model_name: The model's name
    :param version: The model's version
    :param properties: Model properties
    :param dependencies: Model dependencies path
    :param code_dir: Model code directory path
    :param parameters: Model parameters
    :param metrics: Model metrics
    :param predict_file: Path to the predict file
    :param register_in_jml: Whether to register the model to JML
    :return: None
    """
    model_version_manager = FilesModelVersionManager(source_path)
    model_version_manager.log_model_to_artifactory(
        model=None,  # No model object is passed for file-based models
        repository=repository,
        model_name=model_name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
        parameters=parameters,
        metrics=metrics,
        predict_file=predict_file,
        model_path=source_path,
        register_in_jml=register_in_jml,
    )


def load_model(
    repository: str, model_name: str, version: str, target_path: Optional[str] = None
) -> Path:
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :param target_path: Path to save the model
    :return: Path to the model file
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    model_info = get_model_info(
        repository=repository, model_name=model_name, version=version
    )
    model_framework = _get_model_framework(model_info)

    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework_stored=model_framework,
        model_framework=ModelFramework.FILES,
    )

    target_path = target_path if target_path else tempfile.mkdtemp()

    FrogMLStorage().download_model_version(
        repository=repository,
        model_name=model_name,
        version=version,
        target_path=target_path,
    )

    return Path(target_path)


def get_model_info(repository: str, model_name: str, version: str) -> Dict:
    """
    Get model information
    :param repository: Repository key where the model is stored
    :param model_name: The model's name
    :param version: The model's version
    :return: The model information as a dictionary
    """
    model_version_manager = FilesModelVersionManager(source_path="")

    return model_version_manager.get_model_info_from_artifactory(
        repository=repository, model_name=model_name, model_version=version
    )
