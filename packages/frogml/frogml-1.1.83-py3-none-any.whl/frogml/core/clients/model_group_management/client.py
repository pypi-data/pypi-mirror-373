from typing_extensions import Self

from frogml.core.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper
from frogml._proto.qwak.model_group.model_group_pb2 import (
    CreateIfNotExistsModelGroupRequest,
    ModelGroupBriefInfoResponse,
)
from dependency_injector.wiring import Provide
from frogml.core.inner.di_configuration import FrogmlContainer

from frogml._proto.qwak.model_group.model_group_pb2_grpc import (
    ModelGroupManagementServiceStub,
)


class ModelGroupManagementClient:

    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self.__model_group_management_service: ModelGroupManagementServiceStub = (
            ModelGroupManagementServiceStub(grpc_channel)
        )

    @grpc_try_catch_wrapper("Failed to create model")
    def create_if_not_exists_model_group(
        self: Self, project_key: str
    ) -> ModelGroupBriefInfoResponse:
        request: CreateIfNotExistsModelGroupRequest = (
            CreateIfNotExistsModelGroupRequest(
                jfrog_project_key=project_key, model_group_name=project_key
            )
        )
        return self.__model_group_management_service.CreateIfNotExistsModelGroup(
            request
        )
