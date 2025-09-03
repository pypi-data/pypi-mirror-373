import importlib
import logging
import os.path
import tempfile
from functools import partial
from typing import Dict, List, Optional, Any

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import (
    ModelFramework,
)
from frogml.sdk.model_version.model_loggers.huggingface_model_version_manager import (
    HuggingfaceModelVersionManager,
)
from frogml.sdk.model_version.utils.storage import (
    _download_model_version_from_artifactory,
)
from frogml.sdk.model_version.utils.storage_helper import (
    _get_model_framework,
    _get_model_framework_version,
)
from frogml.sdk.model_version.utils.validations import (
    _validate_load_model,
)

_logger = logging.getLogger(__name__)


def log_model(
    model,
    tokenizer,
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
    """
    Log Hugging face model to Artifactory
    :param model: Model to log
    :param tokenizer: Tokenizer to log
    :param model_name: Name of the model
    :param repository: Repository to log the model to
    :param version: Version of the model
    :param properties: Model properties
    :param dependencies: Model dependencies
    :param code_dir: Directory containing the code
    :param parameters: Model parameters
    :param metrics: Model metrics
    :param register_in_jml: Whether to register the model to JML
    :return:
    """
    model_version_manager = HuggingfaceModelVersionManager()
    model_version_manager.log_model_to_artifactory(
        model=(model, tokenizer),
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
    model_version_manager = HuggingfaceModelVersionManager()

    return model_version_manager.get_model_info_from_artifactory(
        repository=repository, model_name=model_name, model_version=version
    )


def __deserialize_model_and_tokenizer(model_path: str) -> tuple:
    """
    Deserialize a huggingface model and tokenizer from a predefined path

    :param model_path: The directory's path containing the configuration files
    :return: Tuple of model and tokenizer
    """
    model = __deserialize_model(model_path)
    tokenizer = __deserialize_tokenizer(model_path)

    return model, tokenizer


def __deserialize_model(model_path: str):
    """
    Get the Huggingface model from the model configuration file
    If an architecture is not found in the configuration file,
    the model will be loaded using Huggingface's AutoModel

    :param model_path: The directory's path containing the configuration file
    :return: The Huggingface model class
    """
    from transformers import AutoModel, PretrainedConfig

    pretrained_config: PretrainedConfig = PretrainedConfig.from_pretrained(model_path)
    if pretrained_config.architectures:
        for architecture in pretrained_config.architectures:
            try:
                model_class = getattr(
                    importlib.import_module("transformers"), architecture
                )

                return model_class.from_pretrained(model_path)
            except AttributeError:
                _logger.debug(
                    "Failed to load model class %s, using transformers.AutoModel",
                    architecture,
                )
            except Exception as e:
                _logger.error(
                    "Failed to load model %s, using transformers.AutoModel", e
                )

    return AutoModel.from_pretrained(model_path)


def __deserialize_tokenizer(model_path: str):
    """
    Get the Huggingface tokenizer from the tokenizer configuration file

    :param model_path: The directory's path containing the configuration file
    :return: The Huggingface tokenizer class
    """
    from transformers.models.auto.tokenization_auto import (
        get_tokenizer_config,
        tokenizer_class_from_name,
    )
    from transformers import PreTrainedTokenizerBase, AutoTokenizer

    tokenizer_config: dict = get_tokenizer_config(os.path.abspath(model_path))
    config_tokenizer_class = tokenizer_config.get("tokenizer_class")

    try:
        tokenizer_class: PreTrainedTokenizerBase = tokenizer_class_from_name(
            config_tokenizer_class
        )

        return tokenizer_class.from_pretrained(model_path)
    except AttributeError:
        _logger.debug(
            "Failed to load tokenizer class %s, using transformers.AutoTokenizer",
            config_tokenizer_class,
        )
    except Exception as e:
        _logger.error(
            "Failed to load tokenizer %s, using transformers.AutoTokenizer", e
        )

    return AutoTokenizer.from_pretrained(model_path)


def load_model(repository: str, model_name: str, version: str):
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :return: tuple of Model and tokenizer
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    with tempfile.TemporaryDirectory() as download_target_path:
        model_info = get_model_info(
            repository=repository, model_name=model_name, version=version
        )
        model_framework = _get_model_framework(model_info)
        framework_runtime_version = _get_model_framework_version(model_info)

        _validate_load_model(
            repository=repository,
            model_name=model_name,
            version=version,
            model_framework_stored=model_framework,
            model_framework=ModelFramework.HUGGINGFACE,
        )

        full_model_path = os.path.join(download_target_path, f"{model_name}")

        try:
            return _download_model_version_from_artifactory(
                model_framework=ModelFramework.HUGGINGFACE,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework_stored=model_framework,
                download_target_path=full_model_path,
                deserializer=partial(
                    __deserialize_model_and_tokenizer, full_model_path
                ),
            )
        except Exception as e:
            logging.error(
                f"Failed to load Model. Model was serialized with transformers using DistilBert version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")
