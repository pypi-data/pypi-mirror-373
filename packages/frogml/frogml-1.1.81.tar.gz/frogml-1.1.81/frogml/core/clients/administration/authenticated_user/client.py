import grpc
from dependency_injector.wiring import Provide

from frogml._proto.qwak.administration.authenticated_user.v1.authenticated_user_service_pb2 import (
    GetCloudCredentialsRequest,
    GetCloudCredentialsResponse,
    GetDetailsRequest,
    GetDetailsResponse,
)
from frogml._proto.qwak.administration.authenticated_user.v1.authenticated_user_service_pb2_grpc import (
    AuthenticatedUserStub,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer


class AuthenticatedUserClient:
    """
    Used for interacting with JFrog ML Authenticated User service
    """

    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._authenticated_user = AuthenticatedUserStub(grpc_channel)

    def get_details(self) -> GetDetailsResponse:
        request = GetDetailsRequest()
        try:
            return self._authenticated_user.GetDetails(request)
        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to get authenticated user details, error is {e.details()}"
            )

    def get_cloud_credentials(self) -> GetCloudCredentialsResponse:
        request = GetCloudCredentialsRequest()
        try:
            return self._authenticated_user.GetCloudCredentials(request)
        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to get cloud credentials, error is {e.details()}"
            )
