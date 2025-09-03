from base64 import b64decode
from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.admiral.secret.v0.secret_pb2 import SystemSecretValue
from frogml._proto.qwak.integration.integration_pb2 import Integration
from frogml._proto.qwak.integration.open_a_i_integration_pb2 import (
    OpenAIApiKeySystemSecretDescriptor,
    OpenAIIntegration,
)
from frogml.core.clients.administration.eco_system.eco_system_utils import (
    EcosystemUtils,
)
from frogml.core.clients.system_secret.system_secret_client import SystemSecretClient


@dataclass
class OpenAIApiKeySystemSecret:
    integration_id: str
    integration_name: str
    secret_name: str
    secret_key: str

    @classmethod
    def from_proto(cls, proto: Integration) -> Optional["OpenAIApiKeySystemSecret"]:
        if proto.WhichOneof("type") != "openai_integration":
            raise ValueError(f"Got wrong type of integration: {proto}")
        openai_integration: OpenAIIntegration = proto.openai_integration

        if (
            openai_integration.WhichOneof("auth")
            != "openai_api_key_system_secret_descriptor"
        ):
            return None

        system_secret: OpenAIApiKeySystemSecretDescriptor = (
            openai_integration.openai_api_key_system_secret_descriptor
        )

        return cls(
            integration_id=proto.integration_id,
            integration_name=proto.name,
            secret_name=system_secret.secret_name,
            secret_key=system_secret.api_key_secret_key,
        )

    def get_api_key(self) -> str:
        system_secret_client = SystemSecretClient()
        default_environment_id: str = EcosystemUtils().get_default_environment_id()
        system_secret: SystemSecretValue = system_secret_client.get_system_secret(
            name=self.secret_name, env_id=default_environment_id
        )

        if system_secret.WhichOneof("value") != "opaque_pair":
            raise ValueError("Got unsupported system secret value type")

        encoded_api_key: str = system_secret.opaque_pair.pairs.get(key=self.secret_key)
        return b64decode(encoded_api_key).decode("utf-8")
