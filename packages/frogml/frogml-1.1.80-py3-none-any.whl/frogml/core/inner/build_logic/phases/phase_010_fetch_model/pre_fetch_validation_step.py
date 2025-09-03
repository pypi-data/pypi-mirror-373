import uuid
from pathlib import Path

import grpc

from frogml.core.clients.secret_service import SecretServiceClient
from frogml.core.exceptions import FrogmlException, FrogmlSuggestionException
from frogml.core.inner.build_logic.constants.host_resource import HOST_TEMP_BUILD_DIR
from frogml.core.inner.build_logic.interface.step_inteface import Step
from frogml.core.inner.build_logic.tools.dependencies_tools import find_dependency_files
from frogml.core.inner.build_logic.tools.text import snake_case
from frogml.core.inner.instance_template.verify_template_id import verify_template_id
from frogml.core.inner.provider import Provider

import importlib


class PreFetchValidationStep(Step):
    STEP_DESCRIPTION = "Pre model fetch validation"
    DEFAULT_CPUS = 2
    DEFAULT_MEMORY = "4Gi"
    VALIDATION_FAILURE_CPU_AND_GPU_MESSAGE = (
        "CPU and GPU configured together, Invalid configuration."
    )
    VALIDATION_FAILURE_CPU_AND_GPU_SUGGESTION = "Please configure only CPU or GPU"
    VALIDATION_FAILURE_CPU_AND_INSTANCE_MESSAGE = (
        "CPU and instance configured together, Invalid configuration."
    )
    VALIDATION_FAILURE_CPU_AND_INSTANCE_SUGGESTION = (
        "Please configure only CPU or instance"
    )
    VALIDATION_FAILURE_GPU_AND_INSTANCE_MESSAGE = (
        "GPU and instance configured together, Invalid configuration."
    )
    VALIDATION_FAILURE_GPU_AND_INSTANCE_SUGGESTION = (
        "Please configure only GPU or instance"
    )
    EXISTING_MODEL_PASSED_MSG = "Build process was provided with pre built model"
    INVALID_FROGML_MODEL_MSG_FORMAT = (
        "The provided frogml model is not of {expected_class} but of {passed_class}"
    )
    SERVICE_ACCOUNT_NOT_FOUND = (
        "GCP service account key secret '{secret_name}' wasn't found"
    )
    SERVICE_ACCOUNT_NOT_FOUND_SUGGESTION = "Make sure your GCP service account key secret is configured correctly in the environment"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        self.validate_build_properties()
        self.create_build_id()
        self.collect_build_name()
        self.collect_model_id()
        self.create_build_dir()
        self.collect_git_credentials()
        self.validate_dependencies()
        self.validate_resources()
        self.validate_deployment_resources()
        self.validate_frogml_model()
        self.validate_gcp_service_account_secret()

    def validate_build_properties(self):
        if not self.config.build_properties.model_uri.uri:
            error_message = "Model uri wasn't set"
            self.build_logger.error(f"{error_message}, failing...")

            raise FrogmlSuggestionException(
                message=error_message,
                suggestion="Make sure your build properties object contains model uri argument",
            )
        if (
            self.config.build_properties.model_uri.git_credentials_secret
            and self.config.build_properties.model_uri.git_secret_ssh
        ):
            error_message = (
                "Only one of git credentials secret or git secret ssh can be configured"
            )
            raise FrogmlSuggestionException(
                message=error_message,
                suggestion="Make sure your git credentials or git secret ssh are configured correctly and only one of "
                "them is configured",
            )

    def collect_model_id(self):
        model_id = self.config.build_properties.model_id
        model = self.context.client_models_management.get_model(
            model_id=model_id,
            exception_on_missing=False,
        )
        if not model:
            suggestion = f"Create model {model_id} or check model ID spelling"
            snake_case_model_id = snake_case(model_id)
            if self.context.client_models_management.is_model_exists(
                snake_case_model_id
            ):
                suggestion = f"Try using model ID {snake_case_model_id} instead"
            raise FrogmlSuggestionException(
                message=f"Model ID {model_id} isn't found",
                suggestion=suggestion,
            )
        self.context.project_uuid = model.project_id
        self.context.model_uuid = model.uuid
        self.context.model_id = model_id

    def create_build_id(self):
        if not self.context.build_id:
            self.context.build_id = str(uuid.uuid4())
            self.build_logger.info(f"Generated build ID - {self.context.build_id}")
        else:
            self.build_logger.info(f"Using given build ID - {self.context.build_id}")

    def collect_build_name(self):
        build_name: str = self.config.build_properties.build_name

        if build_name:
            self.build_logger.info(f"Using given build name - {build_name}")
            self.context.build_name = build_name

    def create_build_dir(self):
        build_dir = HOST_TEMP_BUILD_DIR / self.context.model_id / self.context.build_id
        build_dir.mkdir(exist_ok=True, parents=True)
        self.context.host_temp_local_build_dir = build_dir
        self.build_logger.debug(f"Build directory created - {build_dir}")

    def collect_git_credentials(self):
        if self.config.build_properties.model_uri.git_credentials:
            self.context.git_credentials = (
                self.config.build_properties.model_uri.git_credentials
            )
        elif self.config.build_properties.model_uri.git_credentials_secret:
            self.context.git_credentials = SecretServiceClient().get_secret(
                self.config.build_properties.model_uri.git_credentials_secret
            )
        elif self.config.build_properties.model_uri.git_secret_ssh:
            self.context.git_ssh_key = SecretServiceClient().get_secret(
                self.config.build_properties.model_uri.git_secret_ssh
            )
        else:
            self.build_logger.debug("Git credentials isn't configured")

    def validate_dependencies(self):
        if (
            Path(self.config.build_properties.model_uri.uri).is_dir()
            and not self.config.build_env.python_env.dependency_file_path
        ):
            model_uri, main_dir = (
                Path(self.config.build_properties.model_uri.uri),
                self.config.build_properties.model_uri.main_dir,
            )
            (
                self.context.dependency_manager_type,
                self.context.model_relative_dependency_file,
                self.context.model_relative_dependency_lock_file,
            ) = find_dependency_files(model_uri, main_dir, self.build_logger)

            if (
                self.context.dependency_manager_type
                and self.context.model_relative_dependency_file
            ):
                return

            self.build_logger.error("Dependency file wasn't found, failing...")
            raise FrogmlSuggestionException(
                message="Dependency file isn't found",
                suggestion="Make sure your model include one of dependencies manager: pip/poetry/conda",
            )

    def validate_resources(self):
        gpu_configured = (
            self.config.build_env.remote.resources.gpu_type
            or self.config.build_env.remote.resources.gpu_amount
        )
        cpu_configured = (
            self.config.build_env.remote.resources.cpus
            or self.config.build_env.remote.resources.memory
        )
        instance_configured = self.config.build_env.remote.resources.instance

        if cpu_configured and gpu_configured:
            raise FrogmlSuggestionException(
                message=self.VALIDATION_FAILURE_CPU_AND_GPU_MESSAGE,
                suggestion=self.VALIDATION_FAILURE_CPU_AND_GPU_SUGGESTION,
            )
        if cpu_configured and instance_configured:
            raise FrogmlSuggestionException(
                message=self.VALIDATION_FAILURE_CPU_AND_INSTANCE_MESSAGE,
                suggestion=self.VALIDATION_FAILURE_CPU_AND_INSTANCE_SUGGESTION,
            )
        if gpu_configured and instance_configured:
            raise FrogmlSuggestionException(
                message=self.VALIDATION_FAILURE_GPU_AND_INSTANCE_MESSAGE,
                suggestion=self.VALIDATION_FAILURE_GPU_AND_INSTANCE_SUGGESTION,
            )

        if instance_configured:
            provider = self.__get_provider()
            verify_template_id(
                self.config.build_env.remote.resources.instance,
                self.context.client_instance_template,
                provider=provider,
            )

        if not (cpu_configured or gpu_configured or instance_configured):
            self.config.build_env.remote.resources.cpus = self.DEFAULT_CPUS
            self.config.build_env.remote.resources.memory = self.DEFAULT_MEMORY

    def __get_provider(self):
        user_context = self.context.client_ecosystem.get_authenticated_user_context()
        provider = None
        if (
            user_context.user.environment_details.configuration.cloud_configuration.WhichOneof(
                "configuration"
            )
            == "aws_cloud_configuration"
        ):
            provider = Provider.AWS
        elif (
            user_context.user.environment_details.configuration.cloud_configuration.WhichOneof(
                "configuration"
            )
            == "gcp_cloud_configuration"
        ):
            provider = Provider.GCP
        return provider

    def validate_deployment_resources(self):
        if self.config.deploy and self.config.deployment_instance:
            provider = self.__get_provider()
            verify_template_id(
                self.config.deployment_instance,
                self.context.client_instance_template,
                provider=provider,
            )

    def validate_frogml_model(self):
        if self.config.pre_built_model:
            self.build_logger.debug(self.EXISTING_MODEL_PASSED_MSG)
            base_model_class: object = getattr(
                importlib.import_module("frogml.sdk.model.base"), "BaseModel"
            )
            if not isinstance(self.config.pre_built_model, base_model_class):
                raise FrogmlException(
                    self.INVALID_FROGML_MODEL_MSG_FORMAT.format(
                        expected_class=base_model_class.__name__,
                        passed_class=self.config.pre_built_model.__class__,
                    )
                )

    def validate_gcp_service_account_secret(self):
        if self.config.build_env.docker.service_account_key_secret_name:
            self.build_logger.debug("Checking GCP service account key secret")
            try:
                SecretServiceClient().get_secret(
                    self.config.build_env.docker.service_account_key_secret_name
                )
            except FrogmlException as e:
                if e.status_code == grpc.StatusCode.NOT_FOUND:
                    raise FrogmlSuggestionException(
                        message=self.SERVICE_ACCOUNT_NOT_FOUND.format(
                            secret_name=self.config.build_env.docker.service_account_key_secret_name
                        ),
                        suggestion=self.SERVICE_ACCOUNT_NOT_FOUND_SUGGESTION,
                    )
                raise e

            self.build_logger.debug("service account key secret found")
