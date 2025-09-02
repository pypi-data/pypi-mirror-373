from typing import List

from _qwak_proto.qwak.integration.integration_pb2 import Integration
from qwak.clients.integration_management.integration_manager_client import (
    IntegrationManagerClient,
)
from qwak.clients.integration_management.openai.openai_system_secret import (
    OpenAIApiKeySystemSecret,
)


class IntegrationUtils:
    def __init__(self):
        self._client: IntegrationManagerClient = IntegrationManagerClient()

    def get_openai_api_keys(self) -> List[OpenAIApiKeySystemSecret]:
        all_integrations: List[Integration] = self._client.list_integrations()

        openai_integration: List[Integration] = [
            i for i in all_integrations if i.WhichOneof("type") == "openai_integration"
        ]

        openai_secrets: List[OpenAIApiKeySystemSecret] = [
            OpenAIApiKeySystemSecret.from_proto(proto=o) for o in openai_integration
        ]

        return [s for s in openai_secrets if s is not None]
