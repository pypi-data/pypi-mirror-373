from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Type

from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    Authentication as ProtoAuthentication,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import Plain as ProtoPlain
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import Sasl as ProtoSasl
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    SaslMechanism as ProtoSaslMechanism,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    SecurityProtocol as ProtoSecurityProtocol,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import Ssl as ProtoSsl
from frogml.core.clients.secret_service import SecretServiceClient
from frogml.core.exceptions import FrogmlException


class SaslMechanism(Enum):
    SCRAMSHA256 = ProtoSaslMechanism.SCRAMSHA256
    SCRAMSHA512 = ProtoSaslMechanism.SCRAMSHA512
    PLAIN = ProtoSaslMechanism.PLAIN


class SecurityProtocol(Enum):
    SASL_SSL = ProtoSecurityProtocol.SASL_SSL


@dataclass
class BaseAuthentication(ABC):
    @abstractmethod
    def _to_proto(self) -> ProtoAuthentication:
        pass

    @classmethod
    def _from_proto(
        cls,
        proto_authentication_method: ProtoAuthentication,
    ) -> Type["BaseAuthentication"]:
        proto_authentication_method = getattr(
            proto_authentication_method,
            proto_authentication_method.WhichOneof("type"),
        )
        if isinstance(proto_authentication_method, ProtoPlain):
            return PlainAuthentication._from_proto(proto_authentication_method)
        elif isinstance(proto_authentication_method, ProtoSsl):
            return SslAuthentication._from_proto(proto_authentication_method)
        elif isinstance(proto_authentication_method, ProtoSasl):
            return SaslAuthentication._from_proto(proto_authentication_method)
        else:
            raise FrogmlException(
                f"Got unsupported authentication method {proto_authentication_method}"
            )


@dataclass
class PlainAuthentication(BaseAuthentication):
    def _to_proto(self) -> ProtoAuthentication:
        return ProtoAuthentication(plain_configuration=ProtoPlain())

    @classmethod
    def _from_proto(
        cls, proto_authentication_method: ProtoPlain
    ) -> Type["PlainAuthentication"]:
        return cls()


@dataclass
class SslAuthentication(BaseAuthentication):
    def _to_proto(self) -> ProtoAuthentication:
        return ProtoAuthentication(ssl_configuration=ProtoSsl())

    @classmethod
    def _from_proto(
        cls, proto_authentication_method: ProtoSsl
    ) -> Type["SslAuthentication"]:
        return cls()


@dataclass
class SaslAuthentication(BaseAuthentication):
    username_secret: str
    password_secret: str
    sasl_mechanism: SaslMechanism
    security_protocol: SecurityProtocol

    def _to_proto(self) -> ProtoAuthentication:
        self._validate()
        return ProtoAuthentication(
            sasl_configuration=ProtoSasl(
                username_secret=self.username_secret,
                password_secret=self.password_secret,
                sasl_mechanism=self.sasl_mechanism.value,
                security_protocol=self.security_protocol.value,
            )
        )

    @classmethod
    def _from_proto(
        cls, proto_authentication_method: ProtoSasl
    ) -> Type["SaslAuthentication"]:
        return cls(
            username_secret=proto_authentication_method.username_secret,
            password_secret=proto_authentication_method.password_secret,
            sasl_mechanism=SaslMechanism(proto_authentication_method.sasl_mechanism),
            security_protocol=SecurityProtocol(
                proto_authentication_method.security_protocol
            ),
        )

    def _validate(self):
        secret_service_client = SecretServiceClient()

        if not secret_service_client.get_secret(self.username_secret):
            raise FrogmlException(
                f"Secret for username {self.username_secret} does not exist"
            )
        if not secret_service_client.get_secret(self.password_secret):
            raise FrogmlException(
                f"Secret for password {self.password_secret} does not exist"
            )
