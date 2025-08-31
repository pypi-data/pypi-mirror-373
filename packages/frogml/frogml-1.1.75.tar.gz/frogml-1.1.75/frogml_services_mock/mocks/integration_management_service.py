import uuid
from typing import Dict

import grpc

from frogml._proto.qwak.integration.integration_pb2 import Integration, IntegrationSpec
from frogml._proto.qwak.integration.integration_service_pb2 import (
    CreateIntegrationRequest,
    CreateIntegrationResponse,
    DeleteIntegrationRequest,
    DeleteIntegrationResponse,
    GetIntegrationRequest,
    GetIntegrationResponse,
    ListIntegrationRequest,
    ListIntegrationsResponse,
)
from frogml._proto.qwak.integration.integration_service_pb2_grpc import (
    IntegrationManagementServiceServicer,
)
from frogml._proto.qwak.integration.open_a_i_integration_pb2 import (
    OpenAIApiKeySystemSecretDescriptor,
    OpenAIIntegration,
)


class IntegrationManagementServiceMock(IntegrationManagementServiceServicer):
    _integrations: Dict[str, Integration] = dict()

    def clear(self):
        self._integrations.clear()

    def CreateIntegration(self, request: CreateIntegrationRequest, context):
        """Create a new integration in account level"""
        spec: IntegrationSpec = request.integration_spec
        if spec.WhichOneof("spec") != "openai_integration_spec":
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Method not implemented!")
            raise NotImplementedError("Method not implemented!")

        integration_id: str = str(uuid.uuid4())
        integration_name: str = str(uuid.uuid4())
        secret_name: str = str(uuid.uuid4())
        api_key_secret_key: str = str(uuid.uuid4())

        integration = Integration(
            integration_id=integration_id,
            name=integration_name,
            openai_integration=OpenAIIntegration(
                openai_api_key_system_secret_descriptor=OpenAIApiKeySystemSecretDescriptor(
                    secret_name=secret_name, api_key_secret_key=api_key_secret_key
                )
            ),
        )
        self._integrations[integration_id] = integration
        return CreateIntegrationResponse(
            integration_id=integration_id, is_successful=True
        )

    def GetIntegration(self, request: GetIntegrationRequest, context):
        """Get integration by id"""
        return GetIntegrationResponse(
            integration=self._integrations[request.integration_id]
        )

    def ListIntegrations(self, request: ListIntegrationRequest, context):
        """List Integrations for account"""
        return ListIntegrationsResponse(integrations=self._integrations.values())

    def DeleteIntegration(self, request: DeleteIntegrationRequest, context):
        """Delete Integration by id"""
        if request.integration_id in self._integrations:
            del self._integrations[request.integration_id]
        return DeleteIntegrationResponse()
