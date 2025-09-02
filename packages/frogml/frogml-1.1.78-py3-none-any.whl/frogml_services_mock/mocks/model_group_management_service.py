from typing import Optional

import grpc
from frogml._proto.qwak.model_group.model_group_pb2 import CreateIfNotExistsModelGroupRequest, \
    ModelGroupBriefInfoResponse
from frogml._proto.qwak.model_group.model_group_pb2_grpc import ModelGroupManagementServiceServicer
from typing_extensions import Self


class ModelGroupManagementServiceMock(ModelGroupManagementServiceServicer):

    def __init__(self):
        super().__init__()
        self.model_group_id: Optional[str] = None
        self.model_group_name: Optional[str] = None
        self.model_group_description: Optional[str] = None
        self.grpc_exception: Optional[grpc.RpcError] = None
        self.jfrog_project_key: Optional[str] = None

    def set_variables(self: Self, model_group_id: str, model_group_description: str,
                      grpc_exception: Optional[grpc.RpcError] = None):
        self.model_group_id = model_group_id
        self.model_group_description = model_group_description
        self.grpc_exception = grpc_exception

    def CreateIfNotExistsModelGroup(self, request: CreateIfNotExistsModelGroupRequest,
                                    _) -> ModelGroupBriefInfoResponse:
        self.jfrog_project_key = request.jfrog_project_key
        self.model_group_name = request.model_group_name
        if self.grpc_exception:
            raise self.grpc_exception
        return ModelGroupBriefInfoResponse(model_group_id=self.model_group_id,
                                           model_group_description=self.model_group_description)
