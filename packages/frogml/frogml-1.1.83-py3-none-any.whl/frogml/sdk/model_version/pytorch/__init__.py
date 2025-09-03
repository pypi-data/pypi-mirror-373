import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework
from frogml.sdk.model_version.model_loggers.pytorch_model_version_manager import (
    PytorchModelVersionManager,
)
from frogml.sdk.model_version.utils.storage import (
    _download_model_version_from_artifactory,
)
from frogml.sdk.model_version.utils.storage_helper import (
    _get_model_framework,
    _get_model_serialization_format,
    _get_model_framework_version,
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
    model_version_manager = PytorchModelVersionManager()
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
    model_version_manager = PytorchModelVersionManager()

    return model_version_manager.get_model_info_from_artifactory(
        repository=repository, model_name=model_name, model_version=version
    )


def load_model(repository: str, model_name: str, version: str):
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    """

    logging.info(f"Loading model {model_name} from {repository}")

    with tempfile.TemporaryDirectory() as download_target_path:
        model_info = get_model_info(
            repository=repository, model_name=model_name, version=version
        )
        model_framework = _get_model_framework(model_info)
        serialization_format = _get_model_serialization_format(model_info)

        def deserializer_model(model_path):
            import torch
            from frogml.sdk.model_version.pytorch import (
                pickle_module as pytorch_pickle_module,
            )

            return torch.load(
                f=model_path, pickle_module=pytorch_pickle_module
            )  # nosec B614

        try:
            return _download_model_version_from_artifactory(
                model_framework=ModelFramework.PYTORCH,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework_stored=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(
                    deserializer_model,
                    os.path.join(
                        download_target_path, f"{model_name}.{serialization_format}"
                    ),
                ),
            )
        except Exception as e:
            framework_runtime_version = _get_model_framework_version(model_info)
            logging.error(
                f"Failed to load Model. Model was serialized with Pytorch version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
