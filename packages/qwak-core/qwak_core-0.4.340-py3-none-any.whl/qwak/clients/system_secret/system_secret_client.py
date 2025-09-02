from _qwak_proto.qwak.admiral.secret.v0.secret_pb2 import (
    EnvironmentSecretIdentifier,
    SystemSecretValue,
)
from _qwak_proto.qwak.admiral.secret.v0.system_secret_service_pb2 import (
    GetSystemSecretRequest,
    GetSystemSecretResponse,
)
from _qwak_proto.qwak.admiral.secret.v0.system_secret_service_pb2_grpc import (
    SystemSecretServiceStub,
)
from dependency_injector.wiring import Provide, inject
from qwak.inner.di_configuration import QwakContainer


class SystemSecretClient:
    @inject
    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
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
