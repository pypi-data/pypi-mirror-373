from typing import Dict, Tuple

from frogml._proto.qwak.admiral.secret.v0.secret_pb2 import (
    EnvironmentSecretIdentifier,
    SetSystemEnvironmentSecretOptions,
    SystemSecretDefinition,
)
from frogml._proto.qwak.admiral.secret.v0.system_secret_service_pb2 import (
    DeleteSystemSecretRequest,
    DeleteSystemSecretResponse,
    GetSystemSecretRequest,
    GetSystemSecretResponse,
    SetSystemSecretRequest,
    SetSystemSecretResponse,
)
from frogml._proto.qwak.admiral.secret.v0.system_secret_service_pb2_grpc import (
    SystemSecretServiceServicer,
)


class SystemSecretServiceMock(SystemSecretServiceServicer):
    _secrets: Dict[Tuple[str, str], SystemSecretDefinition] = dict()

    def clear(self):
        self._secrets.clear()

    def SetSystemSecret(self, request: SetSystemSecretRequest, context):
        """Set a value for a secret"""

        options: SetSystemEnvironmentSecretOptions = request.options
        identifier: EnvironmentSecretIdentifier = options.identifier
        definition: SystemSecretDefinition = SystemSecretDefinition(
            identifier=identifier, spec=options.spec
        )

        self._secrets[(identifier.name, identifier.environment_id)] = definition
        return SetSystemSecretResponse()

    def DeleteSystemSecret(self, request: DeleteSystemSecretRequest, context):
        """Delete secret"""
        name: str = request.identifier.name
        env_id: str = request.identifier.environment_id

        if (name, env_id) in self._secrets:
            del self._secrets[(name, env_id)]

        return DeleteSystemSecretResponse()

    def GetSystemSecret(self, request: GetSystemSecretRequest, context):
        """Get secret"""
        name: str = request.identifier.name
        env_id: str = request.identifier.environment_id
        return GetSystemSecretResponse(secret_definition=self._secrets[(name, env_id)])
