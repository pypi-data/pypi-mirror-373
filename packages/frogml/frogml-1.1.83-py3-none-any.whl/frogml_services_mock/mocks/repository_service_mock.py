from datetime import datetime
from typing import Dict

from google.protobuf.timestamp_pb2 import Timestamp

from frogml._proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml._proto.qwak.jfrog.gateway.v0.repository_service_pb2 import (
    GetRepositoryConfigurationResponse,
    GetRepositoryConfigurationRequest,
)
from frogml._proto.qwak.jfrog.gateway.v0.repository_service_pb2_grpc import (
    RepositoryServiceServicer,
)
from frogml.core.exceptions import FrogmlNotFoundException
from frogml_services_mock.mocks.utils.exception_handlers import (
    raise_not_found_grpc_error,
)

timestamp = Timestamp()
timestamp.FromDatetime(datetime.now())


class RepositoryServiceMock(RepositoryServiceServicer):
    def __init__(self):
        super(RepositoryServiceMock, self).__init__()
        self.repositories: Dict[str, RepositorySpec] = {}

    def GetRepositoryConfiguration(
        self, request: GetRepositoryConfigurationRequest, context
    ) -> GetRepositoryConfigurationResponse:
        repository_key: str = request.repository_key

        if repository_key not in self.repositories:
            raise_not_found_grpc_error(
                context,
                FrogmlNotFoundException(f"Repository {repository_key} not found"),
            )

        return GetRepositoryConfigurationResponse(
            repository_spec=self.repositories[repository_key]
        )
