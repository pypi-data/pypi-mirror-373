import logging
from platform import python_version
from typing import List, Optional, Dict, Union, Tuple

from dependency_injector.wiring import Provide
from grpc import RpcError
from typing_extensions import Self

from frogml.core.clients.model_version_manager.build_model_version_dto import (
    BuildConfigDTO,
)
from frogml.core.clients.model_version_manager.build_model_version_request_mapper import (
    map_build_conf_to_build_spec,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer
from frogml.core.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper
from frogml.core.utils.model_utils import get_model_id_from_model_name
from frogml.core.utils.proto_utils import ProtoUtils
from frogml._proto.jfml.model_version.v1.artifact_pb2 import Artifact as ArtifactProto
from frogml._proto.jfml.model_version.v1.model_repository_spec_pb2 import (
    ModelRepositorySpec,
)
from frogml._proto.jfml.model_version.v1.model_version_framework_pb2 import (
    ModelVersionFramework,
)
from frogml._proto.jfml.model_version.v1.model_version_manager_service_pb2 import (
    CreateModelVersionRequest,
    CreateModelVersionResponse,
    PromoteModelVersionToBuildRequest,
    PromoteModelVersionToBuildResponse,
)
from frogml._proto.jfml.model_version.v1.model_version_manager_service_pb2_grpc import (
    ModelVersionManagerServiceStub,
)
from frogml._proto.jfml.model_version.v1.model_version_pb2 import (
    ModelVersionSpec,
    MlBomData,
    ParameterValue,
    MetricValue,
)
from frogml._proto.jfml.model_version.v1.build_spec_pb2 import BuildSpec
from frogml.storage.models.entity_manifest import Artifact


logger = logging.getLogger(__name__)


class ModelVersionManagerClient:
    """
    Used for interacting with the model version manager's endpoints
    """

    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self.__model_version_manager_stub = ModelVersionManagerServiceStub(grpc_channel)

    @staticmethod
    def __build_mlbom_data_kwargs(
        model_artifact: List[ArtifactProto],
        code_artifacts: Optional[List[ArtifactProto]] = None,
        dependency_artifacts: Optional[List[ArtifactProto]] = None,
        metrics: Optional[Dict[str, str]] = None,
        parameters: Optional[Dict[str, str]] = None,
    ) -> Dict[
        str, Union[List[ArtifactProto], Dict[str, Union[ParameterValue, MetricValue]]]
    ]:
        kwargs = {"model_artifact": model_artifact}

        if dependency_artifacts:
            kwargs["dependency_artifacts"] = dependency_artifacts

        if code_artifacts:
            kwargs["code_artifacts"] = code_artifacts

        if parameters:
            kwargs["parameters"] = {
                key: ParameterValue(value=str(value))
                for key, value in parameters.items()
            }

        if metrics:
            kwargs["metrics"] = {
                key: MetricValue(value=str(value)) for key, value in metrics.items()
            }

        return kwargs

    def __build_create_model_version_request(
        self,
        project_key: str,
        repository_key: str,
        model_name: str,
        model_version_name: str,
        model_version_framework: ModelVersionFramework,
        dry_run: bool,
        model_artifacts: List[ArtifactProto],
        dependency_artifacts: Optional[List[ArtifactProto]] = None,
        code_artifacts: Optional[List[ArtifactProto]] = None,
        parameters: Optional[Dict[str, str]] = None,
        metrics: Optional[Dict[str, str]] = None,
    ) -> CreateModelVersionRequest:
        kwargs: dict = self.__build_mlbom_data_kwargs(
            model_artifacts, code_artifacts, dependency_artifacts, metrics, parameters
        )

        return CreateModelVersionRequest(
            dry_run=dry_run,
            model_version=ModelVersionSpec(
                repository_spec=ModelRepositorySpec(
                    project_key=project_key,
                    repository_key=repository_key,
                    model_id=get_model_id_from_model_name(model_name),
                    model_name=model_name,
                ),
                name=model_version_name,
                framework=model_version_framework,
                python_version=python_version(),
            ),
            ml_bom_data=MlBomData(**kwargs),
        )

    def validate_create_model_version(
        self,
        project_key: str,
        repository_key: str,
        model_name: str,
        model_version_name: str,
        model_version_framework: ModelVersionFramework,
        model_artifact: List[Artifact],
        dependency_artifacts: Optional[List[Artifact]] = None,
        code_artifacts: Optional[List[Artifact]] = None,
        parameters: Optional[Dict[str, str]] = None,
        metrics: Optional[Dict[str, str]] = None,
    ):
        try:
            (
                code_artifacts_proto,
                dependency_artifacts_proto,
                model_artifact_proto,
            ) = self.convert_artifacts(
                model_artifact, dependency_artifacts, code_artifacts
            )

            create_model_request = self.__build_create_model_version_request(
                project_key=project_key,
                repository_key=repository_key,
                model_name=model_name,
                model_version_name=model_version_name,
                model_version_framework=model_version_framework,
                dry_run=True,
                model_artifacts=model_artifact_proto,
                dependency_artifacts=dependency_artifacts_proto,
                code_artifacts=code_artifacts_proto,
                parameters=parameters,
                metrics=metrics,
            )
            self.__model_version_manager_stub.CreateModelVersion(create_model_request)
        except RpcError as e:
            message = f"Failed to validate model version, details [{e.details()}]"
            raise FrogmlException(message)

        except Exception as e:
            message = f"Failed to validate model version, details [{e}]"
            raise FrogmlException(message)

    def create_model_version(
        self,
        project_key: str,
        repository_key: str,
        model_name: str,
        model_version_name: str,
        model_version_framework: ModelVersionFramework,
        model_artifact: List[Artifact],
        dependency_artifacts: Optional[List[Artifact]] = None,
        code_artifacts: Optional[List[Artifact]] = None,
        parameters: Optional[Dict[str, str]] = None,
        metrics: Optional[Dict[str, str]] = None,
    ) -> CreateModelVersionResponse:
        try:
            (
                code_artifacts_proto,
                dependency_artifacts_proto,
                model_artifact_proto,
            ) = self.convert_artifacts(
                model_artifact, dependency_artifacts, code_artifacts
            )

            create_model_request = self.__build_create_model_version_request(
                project_key=project_key,
                repository_key=repository_key,
                model_name=model_name,
                model_version_name=model_version_name,
                model_version_framework=model_version_framework,
                dry_run=False,
                model_artifacts=model_artifact_proto,
                dependency_artifacts=dependency_artifacts_proto,
                code_artifacts=code_artifacts_proto,
                parameters=parameters,
                metrics=metrics,
            )
            create_model_version_response: CreateModelVersionResponse = (
                self.__model_version_manager_stub.CreateModelVersion(
                    create_model_request
                )
            )

            return create_model_version_response
        except RpcError as e:
            message = f"Failed to validate model version, details [{e.details()}]"
            raise FrogmlException(message)

        except Exception as e:
            message = f"Failed to validate model version, details [{e}]"
            raise FrogmlException(message)

    @staticmethod
    def convert_artifacts(
        model_artifact: List[Artifact],
        dependency_artifacts: Optional[List[Artifact]] = None,
        code_artifacts: Optional[List[Artifact]] = None,
    ) -> Tuple[
        Optional[List[ArtifactProto]],
        Optional[List[ArtifactProto]],
        List[ArtifactProto],
    ]:
        model_artifact_proto: List[ArtifactProto] = (
            ProtoUtils.convert_artifacts_to_artifacts_proto(model_artifact)
        )
        dependency_artifacts_proto = (
            ProtoUtils.convert_artifacts_to_artifacts_proto(dependency_artifacts)
            if dependency_artifacts
            else None
        )
        code_artifacts_proto = (
            ProtoUtils.convert_artifacts_to_artifacts_proto(code_artifacts)
            if code_artifacts
            else None
        )
        return code_artifacts_proto, dependency_artifacts_proto, model_artifact_proto

    @grpc_try_catch_wrapper("Failed to promote model version to build")
    def promote_to_build(
        self: Self,
        build_config: BuildConfigDTO,
        model_version_id: Optional[str] = None,
        model_id: Optional[str] = None,
        model_version_name: Optional[str] = None,
    ) -> str:
        """
        Promote a model version to build.
        :param build_config: The build configuration for the promotion (required)
        :param model_version_id: Model version ID (alternative to model_id + model_version_name)
        :param model_id: Model ID (required if model_version_id is not provided)
        :param model_version_name: Model version name (required if model_version_id is not provided)
        :return The build ID of the promoted model version
        :raises FrogmlException: If the promotion fails or parameters are invalid
        """
        logger.info("Promote model version to build %s", build_config)
        is_missing_required_model_version_params: bool = not model_version_id and (
            not model_id or not model_version_name
        )
        if is_missing_required_model_version_params:
            raise FrogmlException(
                "Either model_version_id must be provided, or both model_id and model_version_name must be provided"
            )

        build_spec: BuildSpec = map_build_conf_to_build_spec(build_config)
        logger.debug("build_spec = %s", build_spec)

        if model_version_id:
            promote_request = PromoteModelVersionToBuildRequest(
                model_version_id=model_version_id, build_spec=build_spec
            )
        else:
            model_version_spec = ModelVersionSpec(
                repository_spec=ModelRepositorySpec(model_id=model_id),
                name=model_version_name,
            )
            promote_request = PromoteModelVersionToBuildRequest(
                model_version_spec=model_version_spec, build_spec=build_spec
            )

        promote_response: PromoteModelVersionToBuildResponse = (
            self.__model_version_manager_stub.PromoteModelVersionToBuild(
                promote_request
            )
        )

        logger.info("promote_response = %s", promote_response)
        return promote_response.build_id
