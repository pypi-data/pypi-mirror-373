import grpc
from dependency_injector.wiring import Provide

from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2 import (
    AuthenticateRequest,
)
from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2 import (
    QwakApiKeyMethod,
)
from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2_grpc import (
    AuthenticationServiceStub,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer


class AuthenticationClient:
    """
    Used for interacting with Frogml's Authentication service
    """

    def __init__(
        self, grpc_channel=Provide[FrogmlContainer.unauthenticated_core_grpc_channel]
    ):
        self._authentication_service = AuthenticationServiceStub(grpc_channel)

    def authenticate(self, api_key=None):
        request = AuthenticateRequest(
            qwak_api_key_method=QwakApiKeyMethod(qwak_api_key=api_key)
        )
        try:
            return self._authentication_service.Authenticate(request)
        except grpc.RpcError as e:
            raise FrogmlException(f"Failed to login, error is {e.details()}")
