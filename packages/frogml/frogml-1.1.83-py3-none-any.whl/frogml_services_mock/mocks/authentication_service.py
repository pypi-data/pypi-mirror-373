from datetime import datetime, timedelta

from jose import jwt

from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2 import (
    AuthenticateRequest,
    AuthenticateResponse,
)
from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2_grpc import (
    AuthenticationServiceServicer,
)

epoch = datetime.timestamp(datetime.utcnow() + timedelta(days=1))

_payload = {
    "https://auth-token.qwak.ai/qwak-partner-id": "9",
    "https://auth-token.qwak.ai/qwak-user-id": "Test User",
    "https://auth-token.qwak.ai/mlflow-server": "http://localhost",
    "https://auth-token.qwak.ai/data-api": "http://localhost",
    "https://auth-token.qwak.ai/grpc-api": "localhost",
    "https://auth-token.qwak.ai/models-api": "localhost",
    "https://auth-token.qwak.ai/qwak-bucket": "core.bucket",
    "exp": epoch,
}

mock_jwt_token = jwt.encode(_payload, key="secret", algorithm="HS256")


class AuthenticationServiceMock(AuthenticationServiceServicer):
    def Authenticate(
        self, request: AuthenticateRequest, context
    ) -> AuthenticateResponse:
        return AuthenticateResponse(access_token=mock_jwt_token)
