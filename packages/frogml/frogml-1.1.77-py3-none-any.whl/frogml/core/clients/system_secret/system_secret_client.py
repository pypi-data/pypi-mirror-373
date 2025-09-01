from dependency_injector.wiring import Provide, inject

from frogml._proto.qwak.admiral.secret.v0.secret_pb2 import (
    EnvironmentSecretIdentifier,
    SystemSecretValue,
)
from frogml._proto.qwak.admiral.secret.v0.system_secret_service_pb2 import (
    GetSystemSecretRequest,
    GetSystemSecretResponse,
)
from frogml._proto.qwak.admiral.secret.v0.system_secret_service_pb2_grpc import (
    SystemSecretServiceStub,
)
from frogml.core.inner.di_configuration import FrogmlContainer


class SystemSecretClient:
    @inject
    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._grpc_client: SystemSecretServiceStub = SystemSecretServiceStub(
            grpc_channel
        )

    def get_system_secret(self, name: str, env_id: str) -> SystemSecretValue:
        response: GetSystemSecretResponse = self._grpc_client.GetSystemSecret(
            GetSystemSecretRequest(
                identifier=EnvironmentSecretIdentifier(name=name, environment_id=env_id)
            )
        )

        return response.secret_definition.spec.value
