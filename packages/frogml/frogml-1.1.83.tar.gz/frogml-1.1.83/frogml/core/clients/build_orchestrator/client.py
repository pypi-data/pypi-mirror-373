from dataclasses import dataclass
from typing import Dict, List, Optional

import grpc
from dependency_injector.wiring import Provide

from frogml._proto.qwak.build.v1.build_api_pb2 import (
    GetBuildRequest,
    GetBuildResponse,
    ListBuildsRequest,
    ListBuildsResponse,
    LogPhaseStatusRequest,
    PhaseStatus,
    RegisterExperimentTrackingRequest,
    RegisterExperimentTrackingResponse,
    RegisterModelSchemaRequest,
    RegisterModelSchemaResponse,
    RegisterTagsRequest,
    RegisterTagsResponse,
    SaveFrameworkModelsRequest,
    SaveFrameworkModelsResponse,
    UpdateBuildStatusRequest,
    UpdateBuildStatusResponse,
)
from frogml._proto.qwak.build.v1.build_api_pb2_grpc import BuildAPIStub
from frogml._proto.qwak.build.v1.build_pb2 import (
    BuildFilter,
    BuildStatus,
    FrameworkModel,
    FrameworkModelsSpec,
    HuggingFaceModelSpec,
    ModelSchema,
)
from frogml._proto.qwak.build_settings.build_settings_api_pb2 import (
    GetBuildSettingsRequest,
    GetBuildSettingsResponse,
)
from frogml._proto.qwak.build_settings.build_settings_api_pb2_grpc import (
    BuildSettingsApiStub,
)
from frogml._proto.qwak.builds.build_pb2 import BaseDockerImageType, DataTableDefinition
from frogml._proto.qwak.builds.build_url_pb2 import (
    BuildVersioningTagsType,
    BuildVersioningUrlParams,
)
from frogml._proto.qwak.builds.builds_orchestrator_service_pb2 import (
    BuildModelRequest,
    CancelBuildModelRequest,
    CreateDataTableRequest,
    CreateDataTableResponse,
    GetBaseDockerImageNameRequest,
    GetBaseDockerImageNameResponse,
    GetBuildVersioningDownloadURLRequest,
    GetBuildVersioningDownloadURLResponse,
    GetBuildVersioningUploadURLRequest,
    GetBuildVersioningUploadURLResponse,
)
from frogml._proto.qwak.builds.builds_orchestrator_service_pb2_grpc import (
    BuildsOrchestratorServiceStub,
)
from frogml.core.clients.build_orchestrator.build_model_request_getter import (
    _get_build_model_spec,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer
from frogml.core.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper


@dataclass
class FrameworkModelDataClass:
    pass


@dataclass
class HuggingModelDataClass(FrameworkModelDataClass):
    models_name_to_versions: Dict[str, List[str]]
    repository: Optional[str] = None


@dataclass
class HuggingFaceModel(FrameworkModelDataClass):
    model_name: str
    version: str
    repository: str
    sha1: str


class BuildOrchestratorClient:
    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._builds_orchestrator_stub_build_api = BuildAPIStub(grpc_channel)
        self._builds_orchestrator_stub = BuildsOrchestratorServiceStub(grpc_channel)
        self._build_settings_stub = BuildSettingsApiStub(grpc_channel)

    @grpc_try_catch_wrapper("Failed to update build status")
    def update_build_status(
        self, build_id: str, build_status: BuildStatus
    ) -> UpdateBuildStatusResponse:
        request = UpdateBuildStatusRequest(buildId=build_id, build_status=build_status)
        return self._builds_orchestrator_stub_build_api.UpdateBuildStatus(request)

    @grpc_try_catch_wrapper("Failed to register model schema")
    def register_model_schema(
        self, build_id: str, model_schema: ModelSchema
    ) -> RegisterModelSchemaResponse:
        request = RegisterModelSchemaRequest(
            build_id=build_id, model_schema=model_schema
        )
        return self._builds_orchestrator_stub_build_api.RegisterModelSchema(request)

    @grpc_try_catch_wrapper("Failed to register experiment tracking values")
    def register_experiment_tracking(
        self,
        build_id: str,
        params: Dict[str, str] = None,
        metrics: Dict[str, float] = None,
    ) -> RegisterExperimentTrackingResponse:
        params = params if params else {}
        metrics = metrics if metrics else {}

        transformed_params = {k: str(v) for k, v in params.items()}
        transformed_metrics = {k: float(v) for k, v in metrics.items()}

        request = RegisterExperimentTrackingRequest(
            build_id=build_id, params=transformed_params, metrics=transformed_metrics
        )
        return self._builds_orchestrator_stub_build_api.RegisterExperimentTracking(
            request
        )

    @grpc_try_catch_wrapper("Failed to save framework models")
    def save_framework_models(
        self, build_id: str, frameworks_model_data_class: List[FrameworkModelDataClass]
    ) -> SaveFrameworkModelsResponse:
        framework_models = []
        for framework_model_data_class in frameworks_model_data_class:
            if isinstance(framework_model_data_class, HuggingModelDataClass):
                for (
                    huggingface_model_name,
                    versions,
                ) in framework_model_data_class.models_name_to_versions.items():
                    for version in versions:
                        framework_models.append(
                            FrameworkModel(
                                huggingface_model_spec=HuggingFaceModelSpec(
                                    version=version,
                                    model_name=huggingface_model_name,
                                    repository=framework_model_data_class.repository,
                                )
                            )
                        )

        request = SaveFrameworkModelsRequest(
            spec=FrameworkModelsSpec(
                build_id=build_id, framework_models=framework_models
            )
        )

        return self._builds_orchestrator_stub_build_api.SaveFrameworkModels(request)

    @grpc_try_catch_wrapper("Failed to save framework models")
    def save_used_framework_models(
        self, build_id: str, models: List[HuggingFaceModel]
    ) -> SaveFrameworkModelsResponse:
        framework_models = []
        for model in models:
            if isinstance(model, HuggingFaceModel):
                framework_models.append(
                    FrameworkModel(
                        huggingface_model_spec=HuggingFaceModelSpec(
                            version=model.version,
                            model_name=model.model_name,
                            sha1=model.sha1,
                            repository=model.repository,
                        )
                    )
                )
        request = SaveFrameworkModelsRequest(
            spec=FrameworkModelsSpec(
                build_id=build_id, framework_models=framework_models
            )
        )

        return self._builds_orchestrator_stub_build_api.SaveFrameworkModels(request)

    @grpc_try_catch_wrapper("Failed to register tags")
    def register_tags(
        self,
        build_id: str,
        tags: List[str],
    ) -> RegisterTagsResponse:
        request = RegisterTagsRequest(build_id=build_id, tags=tags)
        return self._builds_orchestrator_stub_build_api.RegisterTags(request)

    @grpc_try_catch_wrapper("Failed to list builds")
    def list_builds(
        self, model_uuid: str = "", build_filter: BuildFilter = None, **kwargs
    ) -> ListBuildsResponse:
        _model_uuid = model_uuid if model_uuid else kwargs.get("branch_id")
        if not _model_uuid:
            raise FrogmlException("missing argument model uuid or branch id.")

        request = ListBuildsRequest(model_uuid=_model_uuid, filter=build_filter)
        return self._builds_orchestrator_stub_build_api.ListBuilds(request)

    @grpc_try_catch_wrapper("Failed to get build")
    def get_build(self, build_id: str) -> GetBuildResponse:
        request = GetBuildRequest(build_id=build_id)
        return self._builds_orchestrator_stub_build_api.GetBuild(request)

    def is_build_exists(self, build_id: str) -> bool:
        try:
            build: GetBuildResponse = self.get_build(build_id)
            if build.build.build_spec.build_id == build_id:
                return True
            return False
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise FrogmlException(
                f"Failed to check if build {build_id} is exists, error is {e.details()}"
            )

    @grpc_try_catch_wrapper("Failed to get build versioning upload url")
    def get_build_versioning_upload_url(
        self,
        build_id: str,
        model_id: str,
        tag: str,
        tag_type: BuildVersioningTagsType = BuildVersioningTagsType.INVALID_TAG_TYPE,
    ) -> GetBuildVersioningUploadURLResponse:
        """Get Upload pre signed url

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: the tag to save the artifact by
            tag_type: the type of the file to upload

        Returns:
            the upload url
        """
        return self._builds_orchestrator_stub.GetBuildVersioningUploadURL(
            GetBuildVersioningUploadURLRequest(
                params=BuildVersioningUrlParams(
                    build_id=build_id,
                    model_id=model_id,
                    tag=tag,
                    tag_type=tag_type,
                )
            )
        )

    def get_build_versioning_download_url(
        self,
        build_id: str,
        model_id: str,
        tag: str,
        tag_type: BuildVersioningTagsType = BuildVersioningTagsType.INVALID_TAG_TYPE,
    ) -> GetBuildVersioningDownloadURLResponse:
        """Get Download url

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: the tag to save the artifact by
            tag_type: the type of the file to download

        Returns:
            the pre signed download url
        """
        try:
            return self._builds_orchestrator_stub.GetBuildVersioningDownloadURL(
                GetBuildVersioningDownloadURLRequest(
                    params=BuildVersioningUrlParams(
                        build_id=build_id, model_id=model_id, tag=tag, tag_type=tag_type
                    )
                )
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(
                    "The specified file cannot be found. Please verify the file name before trying again"
                )
                raise FrogmlException(
                    "The specified file cannot be found. Please verify the file name before trying again"
                )
            else:
                print(f"Failed to get build versioning download url. Error is {e}")
                raise FrogmlException(
                    f"The specified file cannot be loaded. Error is {e}"
                )

        except Exception as e:
            print(f"Failed to get build versioning download url. Error is {e}")
            raise FrogmlException(
                f"Failed to get build versioning download url. Error is {e}"
            )

    @grpc_try_catch_wrapper("Failed to get build settings")
    def get_build_settings(self, environment_id: str) -> GetBuildSettingsResponse:
        """Get BuildSettings

        Args:
            environment_id: Environment ID

        Returns:
            the build settings by the environment ID
        """
        return self._build_settings_stub.GetBuildSettings(
            GetBuildSettingsRequest(
                environment_id=environment_id,
            )
        )

    @grpc_try_catch_wrapper("Failed to define a table for the data")
    def define_build_data_table(
        self, build_id: str, model_id: str, tag: str, table: DataTableDefinition
    ) -> CreateDataTableResponse:
        """Define Build Data Table

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: tag for the data
            table: the data to save the table for

        Returns:
            the pre signed download url
        """
        return self._builds_orchestrator_stub.CreateDataTable(
            CreateDataTableRequest(
                build_id=build_id,
                model_id=model_id,
                tag=tag,
                table=table,
            )
        )

    @grpc_try_catch_wrapper("Failed to log build phase status")
    def log_phase_status(
        self,
        build_id: str,
        phase_id: str,
        phase_status: PhaseStatus,
        duration_in_seconds: int,
    ) -> None:
        if build_id:
            request = LogPhaseStatusRequest(
                build_id=build_id,
                phase_id=phase_id,
                status=phase_status,
                phase_duration_in_seconds=duration_in_seconds,
            )
            self._builds_orchestrator_stub_build_api.LogPhaseStatus(request)

        else:
            print(f"No build id. Cannot log phase status: {phase_id} {phase_status}")

    def build_model(
        self,
        build_conf,
        verbose: int = 3,
        git_commit_id: str = "",
        resolved_model_url: str = "",
        build_code_path: str = "",
        build_v1_flag: bool = False,
        build_config_url: str = "",
        frogml_cli_wheel_url: str = "",
        frogml_cli_version_url: str = "",
        build_steps: Optional[List[str]] = None,
        cli_version: str = "",
    ):
        """Initiate remote build

        Args:
            verbose: log verbosity level
            git_commit_id: commit id
            resolved_model_url: the url of model
            build_conf: the build configuration
            build_code_path: The code  path saved by frogml
            build_v1_flag:
            build_config_url:
            frogml_cli_wheel_url: Url for wheel file
            frogml_cli_version_url: The cli version
            build_steps: List of the steps the build is comprised from
            cli_version: The cli version to build the

        Raises:
            FrogmlException: In case of failing to connect the service
        """
        build_steps = build_steps if build_steps else []

        try:
            build_spec = _get_build_model_spec(
                build_conf,
                verbose,
                git_commit_id,
                resolved_model_url,
                build_code_path,
                build_v1_flag,
                build_config_url,
                frogml_cli_wheel_url,
                frogml_cli_version_url,
                build_steps,
                cli_version,
            )
            self._builds_orchestrator_stub.BuildModel(
                BuildModelRequest(build_spec=build_spec)
            )
        except grpc.RpcError as e:
            message = (
                f"Failed to build model, status [{e.code()}] details [{e.details()}]"
            )
            raise FrogmlException(message)

        except Exception as e:
            message = f"Failed to build model, details [{e}]"
            raise FrogmlException(message)

    def cancel_build_model(self, build_id: str):
        """cancel remote build process

        Args:
            build_id: The build ID to cancel

        Raises:
            FrogmlException: In case of failing to connect the service
        """
        try:
            self._builds_orchestrator_stub.CancelBuildModel(
                CancelBuildModelRequest(build_id=build_id)
            )
        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to cancel build, status [{e.code()}] details [{e.details()}]"
            )

    def fetch_base_docker_image_name(
        self, type: BaseDockerImageType
    ) -> GetBaseDockerImageNameResponse:
        """Retrieve the base docker image name for a given build type
        Args:
            type: The build type (CPU or GPU)
        Returns:
            The base docker image name
        Raises:
            FrogmlException: In case of failing to connect the service
        """
        try:
            return self._builds_orchestrator_stub.GetBaseDockerImageName(
                GetBaseDockerImageNameRequest(base_docker_image_type=type)
            )
        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to retrieve base docker image name, status [{e.code()}] details [{e.details()}]"
            )
