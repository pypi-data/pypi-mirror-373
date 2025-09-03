from typing import List

from _qwak_proto.qwak.integration.integration_pb2 import Integration
from _qwak_proto.qwak.integration.integration_service_pb2 import (
    GetIntegrationRequest,
    GetIntegrationResponse,
    ListIntegrationRequest,
    ListIntegrationsResponse,
)
from _qwak_proto.qwak.integration.integration_service_pb2_grpc import (
    IntegrationManagementServiceStub,
)
from dependency_injector.wiring import Provide, inject
from qwak.inner.di_configuration import QwakContainer


class IntegrationManagerClient:
    @inject
    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
        self._grpc_client: IntegrationManagementServiceStub = (
            IntegrationManagementServiceStub(grpc_channel)
        )

    def list_integrations(self) -> List[Integration]:
        response: ListIntegrationsResponse = self._grpc_client.ListIntegrations(
            ListIntegrationRequest()
        )
        return response.integrations

    def get_by_id(self, integration_id: str) -> Integration:
        response: GetIntegrationResponse = self._grpc_client.GetIntegration(
            GetIntegrationRequest(integration_id=integration_id)
        )
        return response.integration
