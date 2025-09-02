from typing import Optional

import grpc
from dependency_injector.wiring import Provide
from frogml.core.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper

from frogml.core.utils.model_utils import get_model_id_from_model_name
from frogml._proto.qwak.models.models_pb2 import (
    CreateModelRequest,
    DeleteModelRequest,
    DeleteModelResponse,
    GetModelMetadataRequest,
    GetModelMetadataResponse,
    GetModelRequest,
    GetModelResponse,
    ListModelsMetadataRequest,
    ListModelsMetadataResponse,
    ListModelsRequest,
    ListModelsResponse,
    Model,
    ModelSpec,
)
from frogml._proto.qwak.models.models_pb2_grpc import ModelsManagementServiceStub
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer
from frogml._proto.qwak.projects.jfrog_project_spec_pb2 import ModelRepositoryJFrogSpec


class ModelsManagementClient:
    """
    Used for interacting with Feature Registry endpoints
    """

    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._models_management_service = ModelsManagementServiceStub(grpc_channel)

    def get_model(
        self, model_id: str, exception_on_missing: bool = True
    ) -> Optional[Model]:
        try:
            response: GetModelResponse = self._models_management_service.GetModel(
                GetModelRequest(model_id=model_id)
            )
            return response.model

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND and not exception_on_missing:
                return None
            raise FrogmlException(f"Failed to get model, error is {e.details()}")

    def get_model_by_uuid(
        self, model_uuid, exception_on_missing: bool = True
    ) -> Optional[Model]:
        try:
            return self._models_management_service.GetModel(
                GetModelRequest(model_uuid=model_uuid)
            ).model

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND and not exception_on_missing:
                return None
            raise FrogmlException(f"Failed to get model, error is {e.details()}")

    def get_model_uuid(self, model_id: str) -> str:
        model: Optional[Model] = self.get_model(model_id)
        return model.uuid

    @grpc_try_catch_wrapper("Failed to create model")
    def create_model(
        self,
        project_id: str,
        model_name: str,
        model_description: str,
        jfrog_project_key: Optional[str] = None,
    ):
        return self._models_management_service.CreateModel(
            CreateModelRequest(
                model_spec=ModelSpec(
                    model_named_id=get_model_id_from_model_name(model_name),
                    display_name=model_name,
                    project_id=project_id,
                    model_description=model_description,
                ),
                jfrog_project_spec=ModelRepositoryJFrogSpec(
                    jfrog_project_key=jfrog_project_key,
                ),
            )
        )

    @grpc_try_catch_wrapper("Failed to delete model")
    def delete_model(self, project_id: str, model_id: str) -> DeleteModelResponse:
        return self._models_management_service.DeleteModel(
            DeleteModelRequest(model_id=model_id, project_id=project_id)
        )

    def is_model_exists(self, model_id: str) -> bool:
        """Check if model exists in environment

        Args:
            model_id: the model id to check if exists.

        Returns: if model exists.
        """
        try:
            # noinspection PyStatementEffect
            self._models_management_service.GetModel(
                GetModelRequest(model_id=model_id)
            ).model
            return True
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise FrogmlException(
                f"Failed to check if model {model_id} is exists, error is {e.details()}"
            )

    @grpc_try_catch_wrapper("Failed to list models metadata")
    def list_models_metadata(self, project_id: str) -> ListModelsMetadataResponse:
        return self._models_management_service.ListModelsMetadata(
            ListModelsMetadataRequest(project_id=project_id)
        )

    @grpc_try_catch_wrapper("Failed to list models")
    def list_models(self, project_id: str) -> ListModelsResponse:
        return self._models_management_service.ListModels(
            ListModelsRequest(project_id=project_id)
        )

    @grpc_try_catch_wrapper("Failed to get model metadata")
    def get_model_metadata(self, model_id: str) -> GetModelMetadataResponse:
        return self._models_management_service.GetModelMetadata(
            GetModelMetadataRequest(model_id=model_id)
        )
