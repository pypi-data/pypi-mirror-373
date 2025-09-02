from typing import cast

from dependency_injector.wiring import Provide, inject

from frogml.core.inner.di_configuration import FrogmlContainer
from frogml.core.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_info_service_pb2 import (
    GetJFrogTenantInfoResponse,
    GetJFrogTenantInfoRequest,
)
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_info_service_pb2_grpc import (
    JFrogTenantInfoServiceStub,
)
from frogml._proto.qwak.jfrog.gateway.v0.repository_service_pb2_grpc import (
    RepositoryServiceStub,
)


class JfrogGatewayClient:
    """
    Used for interacting with Feature Registry endpoints
    """

    @inject
    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self.__repository_service = RepositoryServiceStub(grpc_channel)
        self.__jfrog_tenant_info_service = JFrogTenantInfoServiceStub(grpc_channel)

    @grpc_try_catch_wrapper("Failed to get JFrog tenant info")
    def get_jfrog_tenant_info(self) -> GetJFrogTenantInfoResponse:
        """
        Get the customer's JFrog tenant info
        :return: The JFrog tenant info response
        """
        return cast(
            GetJFrogTenantInfoResponse,
            self.__jfrog_tenant_info_service.GetJFrogTenantInfo(
                GetJFrogTenantInfoRequest()
            ),
        )
