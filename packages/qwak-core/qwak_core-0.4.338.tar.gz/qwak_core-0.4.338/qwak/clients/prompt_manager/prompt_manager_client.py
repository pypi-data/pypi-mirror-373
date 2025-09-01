import grpc
from _qwak_proto.qwak.prompt.v1.prompt.prompt_manager_service_pb2 import (
    CreatePromptRequest as ProtoCreatePromptRequest,
    CreatePromptResponse as ProtoCreatePromptResponse,
    CreatePromptVersionRequest as ProtoCreatePromptVersionRequest,
    CreatePromptVersionResponse as ProtoCreatePromptVersionResponse,
    DeletePromptRequest as ProtoDeletePromptRequest,
    DeletePromptVersionRequest as ProtoDeletePromptVersionRequest,
    GetPromptByNameRequest as ProtoGetPromptByNameRequest,
    GetPromptByNameResponse as ProtoGetPromptByNameResponse,
    GetPromptVersionByPromptNameRequest as ProtoGetPromptVersionByPromptNameRequest,
    GetPromptVersionByPromptNameResponse as ProtoGetPromptVersionByPromptNameResponse,
    SetDefaultPromptVersionRequest as ProtoSetDefaultPromptVersionRequest,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_manager_service_pb2_grpc import (
    PromptManagerServiceStub,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_pb2 import (
    Prompt as ProtoPrompt,
    PromptSpec as ProtoPromptSpec,
    PromptVersion as ProtoPromptVersion,
    PromptVersionSpec as ProtoPromptVersionSpec,
)
from dependency_injector.wiring import Provide, inject
from qwak.exceptions import QwakException
from qwak.inner.di_configuration import QwakContainer


class PromptManagerClient:
    @inject
    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
        self._grpc_client: PromptManagerServiceStub = PromptManagerServiceStub(
            grpc_channel
        )

    def create_prompt(
        self,
        name: str,
        prompt_description: str,
        version_spec: ProtoPromptVersionSpec,
    ) -> ProtoPrompt:
        request = ProtoCreatePromptRequest(
            prompt_name=name,
            prompt_spec=ProtoPromptSpec(description=prompt_description),
            prompt_version_spec=version_spec,
        )
        try:
            response: ProtoCreatePromptResponse = self._grpc_client.CreatePrompt(
                request
            )
            return response.prompt
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise QwakException(f"Prompt with name: {name} already exists")
            elif call.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise QwakException(
                    f"Got an illegal prompt specification: {call.details()}"
                )
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def create_prompt_version(
        self,
        name: str,
        version_spec: ProtoPromptVersionSpec,
        set_default: bool,
    ) -> ProtoPromptVersion:
        request = ProtoCreatePromptVersionRequest(
            prompt_name=name, prompt_version_spec=version_spec, set_default=set_default
        )
        try:
            response: ProtoCreatePromptVersionResponse = (
                self._grpc_client.CreatePromptVersion(request)
            )
            return response.prompt_version
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(
                    f"Can not update prompt: '{name}', prompt was not found"
                )
            elif call.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise QwakException(
                    f"Got an illegal prompt specification: {call.details()}"
                )
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def delete_prompt(self, name: str):
        try:
            self._grpc_client.DeletePrompt(ProtoDeletePromptRequest(prompt_name=name))
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(f"Prompt named '{name}' was not found")
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def delete_prompt_version(self, name: str, version: int):
        try:
            self._grpc_client.DeletePromptVersion(
                ProtoDeletePromptVersionRequest(
                    prompt_name=name, version_number=version
                )
            )
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(str(call.details()))
            elif call.code() == grpc.StatusCode.FAILED_PRECONDITION:
                raise QwakException(
                    f"Cannot delete the default version '{version}' of a prompt '{name}',"
                    f" please set another version as the default to delete this version."
                )
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def get_prompt_by_name(self, name: str) -> ProtoPrompt:
        """
        Get prompt's default version
        """
        try:
            response: ProtoGetPromptByNameResponse = self._grpc_client.GetPromptByName(
                ProtoGetPromptByNameRequest(prompt_name=name)
            )
            return response.prompt
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(str(call.details()))
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def get_prompt_version_by_name(self, name: str, version: int) -> ProtoPromptVersion:
        """
        Get prompt specific version
        """
        try:
            response: ProtoGetPromptVersionByPromptNameResponse = (
                self._grpc_client.GetPromptVersionByPromptName(
                    ProtoGetPromptVersionByPromptNameRequest(
                        prompt_name=name, version_number=version
                    )
                )
            )
            return response.prompt_version
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(str(call.details()))
            else:
                raise QwakException(f"Internal Error: {call.details()}")

    def set_default_prompt_version(self, name: str, version: int):
        try:
            self._grpc_client.SetDefaultPromptVersion(
                ProtoSetDefaultPromptVersionRequest(
                    prompt_name=name, version_number=version
                )
            )
        except grpc.RpcError as error:
            call: grpc.Call = error  # noqa
            if call.code() == grpc.StatusCode.NOT_FOUND:
                raise QwakException(str(call.details()))
            else:
                raise QwakException(f"Internal Error: {call.details()}")
