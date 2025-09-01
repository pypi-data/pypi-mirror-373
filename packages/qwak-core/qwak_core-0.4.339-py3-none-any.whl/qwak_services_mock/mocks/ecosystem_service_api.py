from _qwak_proto.qwak.ecosystem.v0.credentials_pb2 import (
    AwsTemporaryCredentials,
    CloudCredentials,
)
from _qwak_proto.qwak.ecosystem.v0.ecosystem_runtime_service_pb2 import (
    GetAuthenticatedUserContextResponse,
    GetCloudCredentialsResponse,
)
from _qwak_proto.qwak.ecosystem.v0.ecosystem_runtime_service_pb2_grpc import (
    QwakEcosystemRuntimeServicer,
)
from qwak_services_mock.mocks.utils.exception_handlers import raise_internal_grpc_error


class EcoSystemServiceMock(QwakEcosystemRuntimeServicer):
    def __init__(self):
        self._aws_temp_credentials = None
        self._authenticated_user_context = None
        super(EcoSystemServiceMock, self).__init__()

    def given_credentials(self, aws_temp_credentials: AwsTemporaryCredentials):
        self._aws_temp_credentials: AwsTemporaryCredentials = aws_temp_credentials

    def GetCloudCredentials(self, request, context):
        """get cloud credentials"""
        try:
            return GetCloudCredentialsResponse(
                cloud_credentials=CloudCredentials(
                    aws_temporary_credentials=self._aws_temp_credentials
                )
            )
        except Exception as e:
            raise_internal_grpc_error(context, e)

    def given_authenticated_user_context(
        self, authenticated_user_context: GetAuthenticatedUserContextResponse
    ):
        self._authenticated_user_context = authenticated_user_context

    def GetAuthenticatedUserContext(
        self, request, context
    ) -> GetAuthenticatedUserContextResponse:
        return self._authenticated_user_context
