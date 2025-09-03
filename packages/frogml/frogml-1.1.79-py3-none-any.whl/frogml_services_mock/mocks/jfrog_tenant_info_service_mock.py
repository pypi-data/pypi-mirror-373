from datetime import datetime
from typing import Dict

from google.protobuf.timestamp_pb2 import Timestamp

from frogml.core.exceptions import FrogmlNotFoundException
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_info_service_pb2 import (
    GetJFrogTenantInfoRequest,
    GetJFrogTenantInfoResponse,
)
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_info_service_pb2_grpc import (
    JFrogTenantInfoServiceServicer,
)
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_pb2 import JFrogTenantInfo
from frogml._proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.utils.exception_handlers import (
    raise_not_found_grpc_error,
)

timestamp = Timestamp()
timestamp.FromDatetime(datetime.now())


class JFrogTenantInfoServiceMock(JFrogTenantInfoServiceServicer):
    def __init__(self):
        super(JFrogTenantInfoServiceMock, self).__init__()
        self.repositories: Dict[str, RepositorySpec] = {}
        self.should_raise_exception: bool = False
        self.platform_url: str = "mock.jfrog.io"

    def GetJFrogTenantInfo(
        self, request: GetJFrogTenantInfoRequest, context
    ) -> GetJFrogTenantInfoResponse:
        if self.should_raise_exception:
            raise_not_found_grpc_error(
                context,
                FrogmlNotFoundException(f"JFrog tenant info not found"),
            )

        return GetJFrogTenantInfoResponse(
            tenant_info=JFrogTenantInfo(platform_url=self.platform_url)
        )
