import logging
import os
from platform import python_version
from typing import Dict, Optional, Callable, cast, Any

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import (
    FROGML_LOG_LEVEL_ENVAR_NAME,
    ModelFramework,
    STORAGE_MODEL_ENTITY_TYPE,
)
from frogml.sdk.model_version.finders.model_class_info import ModelClassInfo
from frogml.sdk.model_version.finders.model_finder import ModelFinder
from frogml.sdk.model_version.modifiers.model_modifier import ModelModifier
from frogml.sdk.model_version.utils.dependencies_tools import _dependency_files_handler
from frogml.sdk.model_version.utils.files_tools import (
    _zip_dir,
    _copy_dir_without_ignored_files,
    _remove_dir,
    _copy_template_files,
    SetupTemplateFilesManager,
)
from frogml.sdk.model_version.utils.jml.customer_client import JmlCustomerClient
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig
from frogml.sdk.model_version.utils.validations import (
    _validate_load_model,
)
from frogml.storage.frog_ml import SerializationMetadata, FrogMLStorage
from frogml.storage.models.frogml_model_version import FrogMLModelVersion
from frogml.storage.models.model_manifest import ModelManifest
from frogml._proto.jfml.model_version.v1.model_version_framework_pb2 import (
    ModelVersionFramework,
    CatboostFramework,
    HuggingFaceFramework,
    OnnxFramework,
    PythonPickleFramework,
    PytorchFramework,
    ScikitLearnFramework,
)
from frogml.sdk.model_version.constants import (
    CATBOOST_SERIALIZED_TYPE,
    HUGGINGFACE_FRAMEWORK_FORMAT,
    ONNX_FRAMEWORK_FORMAT,
    PYTHON_FRAMEWORK_FORMAT,
    PYTORCH_FRAMEWORK_FORMAT,
    SCIKIT_LEARN_FRAMEWORK_FORMAT,
)

_PYTHON_RUNTIME = "python"

_logger = logging.getLogger(__name__)
_logger.setLevel(os.getenv(FROGML_LOG_LEVEL_ENVAR_NAME) or logging.INFO)


def _get_model_metadata(
    model_framework: str,
    framework_version: str,
    serialization_format: str,
) -> SerializationMetadata:
    return SerializationMetadata(
        framework=model_framework,
        framework_version=framework_version,
        serialization_format=serialization_format,
        runtime=_PYTHON_RUNTIME,
        runtime_version=python_version(),
    )


def _get_model_info_from_artifactory(
    repository: str,
    model_name: str,
    version: str,
) -> Dict:
    return FrogMLStorage().get_entity_manifest(
        entity_type=STORAGE_MODEL_ENTITY_TYPE,
        repository=repository,
        entity_name=model_name,
        version=version,
        namespace=None,
    )


def _download_model_version_from_artifactory(
    model_framework: ModelFramework,
    repository: str,
    model_name: str,
    version: str,
    model_framework_stored: str,
    download_target_path: str,
    deserializer: Callable,
):
    """
    Download model version from artifactory
    :param model_framework: model flavor files/catboost etc.
    :param repository: repository name
    :param model_name: the name of the model
    :param version: version of the model
    :param download_target_path: the path to download the model to
    :param model_framework_stored: The model framework stored in the manifest
    :return: Loaded model
    """
    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework_stored=model_framework_stored,
        model_framework=model_framework,
    )

    FrogMLStorage().download_model_version(
        repository=repository,
        model_name=model_name,
        version=version,
        target_path=download_target_path,
    )
    return deserializer()


def _log_model(config: ModelLogConfig) -> None:
    jml_customer_client = JmlCustomerClient()

    model_version_framework: ModelVersionFramework = __model_framework_from_file_format(
        config.serialization_format, config.framework_version
    )

    is_customer_exists_in_jml: bool = (
        config.register_in_jml and jml_customer_client.check_if_customer_exists_in_jml()
    )

    if is_customer_exists_in_jml:
        project_key: str = jml_customer_client.get_project_key(config.repository)
        jml_customer_client.validate_model_version(
            project_key,
            config.repository,
            config.model_name,
            config.version,
            model_version_framework,
        )

    properties = merge_properties_parameters_metrics(
        config.metrics, config.parameters, config.properties
    )
    dependencies: list[str] = _dependency_files_handler(
        dependencies=config.dependencies, target_dir=config.target_dir
    )
    metadata = _get_model_metadata(
        config.model_framework, config.framework_version, config.serialization_format
    )
    SetupTemplateFilesManager(
        config=config, dependencies=dependencies
    ).setup_template_files()

    zipped_code_path: Optional[str] = build_zip_code_path(
        code_dir_path=config.code_dir,
        parent_dir_path=config.target_dir,
    )

    frog_ml_model_version: FrogMLModelVersion = (
        jml_customer_client.log_model_to_artifactory(
            dependencies,
            config.full_model_path,
            config.model_name,
            properties,
            config.repository,
            config.version,
            metadata,
            zipped_code_path,
        )
    )

    if is_customer_exists_in_jml:
        jml_customer_client.register_model_version_in_jml(
            project_key,
            config.repository,
            config.model_name,
            config.version,
            model_version_framework,
            cast(ModelManifest, frog_ml_model_version.entity_manifest),
            config.parameters,
            config.metrics,
        )


def build_zip_code_path(
    code_dir_path: Optional[str], parent_dir_path: str
) -> Optional[str]:
    """
    Build the path to the zipped code directory.
    Before zipping, the code directory is copied to a target directory and filtered to remove ignored files.
    Then, the code directory is processed to find and modify model classes.
    The resulting code directory is zipped and the path to the zipped code directory is returned.

    :param code_dir_path: The path to the code directory
    :param parent_dir_path: The parent directory of the zip file
    :return: The path to the zipped code directory
    """
    filtered_copied_dir_path: str = os.path.join(
        parent_dir_path, "filtered_model_files"
    )
    template_file_dir: str = os.path.join(parent_dir_path, "template_files")

    if code_dir_path:
        _copy_dir_without_ignored_files(
            source_dir=code_dir_path,
            dest_dir=filtered_copied_dir_path,
        )

    _copy_template_files(
        template_file_dir=template_file_dir,
        dest_dir=filtered_copied_dir_path,
    )

    try:
        # Jira Ticket: MLB-256 https://jfrog-int.atlassian.net/browse/MLB-256
        # process_code_directory(
        #     filtered_copied_dir_path, repository, model_name, version, model_framework
        # )
        zipped_code_path = _zip_dir(
            root_dir=parent_dir_path, dir_to_zip=filtered_copied_dir_path
        )
    except Exception as e:
        raise FrogmlException(f"Failed to zip code directory: {e}") from e
    finally:
        _remove_dir(filtered_copied_dir_path)
        _remove_dir(template_file_dir)

    return zipped_code_path


def merge_properties_parameters_metrics(
    metrics: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    properties: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    result = {}
    if properties is not None:
        result.update(properties)

    if parameters is not None:
        result.update(parameters)

    if metrics is not None:
        result.update(metrics)

    result = {key: str(value) for key, value in result.items()}

    return result


def process_code_directory(
    code_dir: str, repository: str, model_name: str, version: str, framework_name: str
):
    """
    Process a directory of Python files to find and modify model classes.

    :param code_dir: Directory containing Python files to analyze
    :param repository: Repository key to use in the template
    :param model_name: Model name to use in the template
    :param version: Model version to use in the template
    :param framework_name: The name of the framework used to train the model

    :raises ValueError: If no valid model class is found or if the model class doesn't have a model field
    """
    model_class_info: ModelClassInfo = ModelFinder.find_model_class(code_dir)

    if model_class_info is None:
        raise ValueError(
            "No class inheriting from FrogMlModel found in the code directory"
        )

    if model_class_info.model_field_name is None:
        raise ValueError(
            f"The class {model_class_info.class_name} does not have a model field (model, _model, or __model)"
        )

    ModelModifier.modify_model_file(
        model_class_info,
        repository,
        model_name,
        version,
        framework_name,
    )

    print(
        f"Successfully modified {model_class_info.file_path} for class {model_class_info.class_name}"
    )


def __model_framework_from_file_format(
    serialization_format: str, framework_version: str = ""
) -> ModelVersionFramework:
    framework_to_define: dict = {"version": framework_version}
    stripped_and_lowered_format = serialization_format.strip().lower()

    if stripped_and_lowered_format == CATBOOST_SERIALIZED_TYPE:
        framework_to_define["catboost"] = CatboostFramework()
    elif stripped_and_lowered_format == HUGGINGFACE_FRAMEWORK_FORMAT:
        framework_to_define["hugging_face"] = HuggingFaceFramework()
    elif stripped_and_lowered_format == ONNX_FRAMEWORK_FORMAT:
        framework_to_define["onnx"] = OnnxFramework()
    elif stripped_and_lowered_format == PYTHON_FRAMEWORK_FORMAT:
        framework_to_define["python_pickle"] = PythonPickleFramework()
    elif stripped_and_lowered_format == PYTORCH_FRAMEWORK_FORMAT:
        framework_to_define["pytorch"] = PytorchFramework()
    elif stripped_and_lowered_format == SCIKIT_LEARN_FRAMEWORK_FORMAT:
        framework_to_define["scikit_learn"] = ScikitLearnFramework()
    else:
        raise ValueError(f"Format {serialization_format} is not supported yet")

    return ModelVersionFramework(**framework_to_define)
