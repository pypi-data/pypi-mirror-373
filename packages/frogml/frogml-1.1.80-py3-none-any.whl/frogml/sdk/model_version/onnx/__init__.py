import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework
from frogml.sdk.model_version.model_loggers.onnx_model_version_manager import (
    OnnxModelVersionManager,
)
from frogml.sdk.model_version.utils.storage import (
    _download_model_version_from_artifactory,
)
from frogml.sdk.model_version.utils.storage_helper import (
    _get_model_framework,
    _get_model_serialization_format,
    _get_model_framework_version,
)
from frogml.sdk.model_version.utils.validations import (
    _validate_load_model,
)

_logger = logging.getLogger(__name__)


def log_model(
    model,
    model_name: str,
    repository: str,
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
    model_version_manager = OnnxModelVersionManager()
    model_version_manager.log_model_to_artifactory(
        model=model,
        repository=repository,
        model_name=model_name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
        parameters=parameters,
        metrics=metrics,
        predict_file=predict_file,
        register_in_jml=register_in_jml,
    )


def get_model_info(repository: str, model_name: str, version: str) -> Dict:
    """
    Get model information
    :param repository: Repository key where the model is stored
    :param model_name: The model's name
    :param version: The model's version
    :return: The model information as a dictionary
    """
    model_version_manager = OnnxModelVersionManager()

    return model_version_manager.get_model_info_from_artifactory(
        repository=repository, model_name=model_name, model_version=version
    )


def load_model(repository: str, model_name: str, version: str):
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :return: loaded model
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    model_info = get_model_info(
        repository=repository, model_name=model_name, version=version
    )
    model_framework = _get_model_framework(model_info)
    serialization_format = _get_model_serialization_format(model_info)
    framework_runtime_version = _get_model_framework_version(model_info)

    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework_stored=model_framework,
        model_framework=ModelFramework.ONNX,
    )

    with tempfile.TemporaryDirectory() as download_target_path:
        full_model_path = os.path.join(
            download_target_path, f"{model_name}.{serialization_format}"
        )

        def deserializer_model(model_path):
            import onnx

            model = onnx.load(model_path)
            onnx.checker.check_model(model)
            return model

        try:
            return _download_model_version_from_artifactory(
                model_framework=ModelFramework.ONNX,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework_stored=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(deserializer_model, full_model_path),
            )
        except Exception as e:
            logging.error(
                f"Failed to load Model. Model was serialized with onnx version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
