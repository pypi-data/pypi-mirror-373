import logging
import os
import sys
from typing import Optional, Dict, Any, TextIO, Union

import requests
from requests import Response

from frogml.storage.frog_ml import FrogMLStorage
from frogml.storage.models.serialization_metadata import SerializationMetadata
from frogml.storage.models.frogml_model_version import FrogMLModelVersion

from typing_extensions import Self

from frogml._proto.jfml.model_version.v1.model_version_framework_pb2 import (
    ModelVersionFramework,
)
from frogml.core.clients.jfrog_gateway import JfrogGatewayClient
from frogml.core.clients.model_version_manager import ModelVersionManagerClient
from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import FROGML_LOG_LEVEL_ENVAR_NAME
from frogml.storage.models.model_manifest import ModelManifest


class JmlCustomerClient:
    """
    A class to handle customer-related operations in the JML system.
    """

    def __init__(self: Self):
        """
        Initializes the JmlCustomerClient
        """
        self.__model_version_manager_client = ModelVersionManagerClient()
        self.__jfrog_gateway_client = JfrogGatewayClient()
        self.__logger = logging.getLogger(type(self).__name__)
        self.__ml_storage = FrogMLStorage()
        self.__define_client_logger()

    def __define_client_logger(self, stream: Union[TextIO, Any] = sys.stdout):
        if self.__logger.hasHandlers():
            return

        console_handler = logging.StreamHandler(stream)
        log_level: int = logging.getLevelName(
            os.getenv(FROGML_LOG_LEVEL_ENVAR_NAME) or logging.INFO
        )
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.__logger.addHandler(console_handler)
        self.__logger.setLevel(log_level)

    def check_if_customer_exists_in_jml(self) -> bool:
        try:
            self.__logger.debug("Checking if customer exists in JML...")
            self.__jfrog_gateway_client.get_jfrog_tenant_info()
            self.__logger.info("Customer exists in JML.")

            return True
        except FrogmlException:
            self.__logger.info("Customer does not exist in JML.")
            return False

    def validate_model_version(
        self: Self,
        project_key: str,
        repository: str,
        model_name: str,
        model_version: str,
        model_version_framework: ModelVersionFramework,
    ):
        try:
            self.__model_version_manager_client.validate_create_model_version(
                project_key=project_key,
                repository_key=repository,
                model_name=model_name,
                model_version_name=model_version,
                model_version_framework=model_version_framework,
                model_artifact=[],
            )
        except Exception as e:
            raise ValueError(str(e)) from e

    def get_project_key(self: Self, repository_key: str) -> str:
        self.__logger.info("Getting project key for repository %s", repository_key)
        repo_configuration_response: Response = (
            self.__ml_storage.get_repository_configuration(
                repository_key=repository_key
            )
        )
        try:
            repo_configuration_response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # Attach the response body for better error logging
            raise FrogmlException(f"{err}\nResponse body: {err.response.text}") from err

        configuration_json: dict[str, object] = repo_configuration_response.json()
        project_key: Optional[str] = configuration_json.get("projectKey")

        if project_key is None:
            raise ValueError(
                f"Repository '{repository_key}' does not belong to any project"
            )

        return project_key

    def log_model_to_artifactory(
        self: Self,
        dependencies: Optional[list[str]],
        full_model_path: str,
        model_name: str,
        properties: Optional[dict[str, str]],
        repository: str,
        version: str,
        metadata: SerializationMetadata,
        code_archive_file_path: Optional[str],
    ) -> FrogMLModelVersion:
        return self.__ml_storage.upload_model_version(
            repository=repository,
            model_name=model_name,
            model_path=full_model_path,
            model_type=metadata,
            version=version,
            properties=properties,
            dependencies_files_paths=dependencies,
            code_archive_file_path=code_archive_file_path,
        )

    def register_model_version_in_jml(
        self: Self,
        project_key: str,
        repository: str,
        model_name: str,
        model_version_name: str,
        model_version_framework: ModelVersionFramework,
        manifest: ModelManifest,
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a model version in JFrog ML."""
        try:
            self.__model_version_manager_client.create_model_version(
                project_key=project_key,
                repository_key=repository,
                model_name=model_name,
                model_version_name=model_version_name,
                model_version_framework=model_version_framework,
                model_artifact=manifest.artifacts,
                dependency_artifacts=manifest.dependency_artifacts,
                code_artifacts=(
                    [manifest.code_artifacts] if manifest.code_artifacts else None
                ),
                parameters=parameters,
                metrics=metrics,
            )
        except FrogmlException as e:
            self.__logger.exception(
                "Failed to create model version %s in JFML due to this following error: '%s'\n\n"
                "Before retrying, please delete the uploaded artifact from Artifactory",
                model_version_name,
                e.message,
            )
            raise e
