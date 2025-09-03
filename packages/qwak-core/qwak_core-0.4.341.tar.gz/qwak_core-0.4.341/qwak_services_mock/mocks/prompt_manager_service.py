from typing import Dict, List, Tuple

import grpc
from _qwak_proto.qwak.prompt.v1.prompt.prompt_manager_service_pb2 import (
    CreatePromptRequest as ProtoCreatePromptRequest,
    CreatePromptResponse as ProtoCreatePromptResponse,
    CreatePromptVersionRequest as ProtoCreatePromptVersionRequest,
    CreatePromptVersionResponse as ProtoCreatePromptVersionResponse,
    DeletePromptRequest as ProtoDeletePromptRequest,
    DeletePromptResponse as ProtoDeletePromptResponse,
    DeletePromptVersionRequest as ProtoDeletePromptVersionRequest,
    DeletePromptVersionResponse as ProtoDeletePromptVersionResponse,
    GetPromptByNameRequest as ProtoGetPromptByNameRequest,
    GetPromptByNameResponse as ProtoGetPromptByNameResponse,
    GetPromptVersionByPromptNameRequest as ProtoGetPromptVersionByPromptNameRequest,
    GetPromptVersionByPromptNameResponse as ProtoGetPromptVersionByPromptNameResponse,
    SetDefaultPromptVersionRequest as ProtoSetDefaultPromptVersionRequest,
    SetDefaultPromptVersionResponse as ProtoSetDefaultPromptVersionResponse,
    UpdatePromptRequest as ProtoUpdatePromptRequest,
    UpdatePromptResponse as ProtoUpdatePromptResponse,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_manager_service_pb2_grpc import (
    PromptManagerServiceServicer,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_pb2 import (
    Prompt as ProtoPrompt,
    PromptMetadata as ProtoPromptMetadata,
    PromptSpec as ProtoPromptSpec,
    PromptVersion as ProtoPromptVersion,
    PromptVersionDefinition as ProtoPromptVersionDefinition,
    PromptVersionMetadata as ProtoPromptVersionMetadata,
)
from google.protobuf.timestamp_pb2 import Timestamp


class PromptManagerServiceMock(PromptManagerServiceServicer):
    prompts: Dict[str, ProtoPrompt] = {}
    prompts_versions: Dict[Tuple[str, int], ProtoPromptVersionDefinition] = {}
    prompts_next_version: Dict[str, int] = {}

    def clear(self):
        self.prompts = {}
        self.prompts_versions = {}
        self.prompts_next_version = {}

    def _is_prompt_name_valid(self, test_str: str) -> bool:
        import re

        regex = r"^[a-z0-9](?:[-_]?[a-z0-9]+)+$"
        return re.match(pattern=regex, string=test_str) is not None

    def _raise_on_missing_prompt(self, prompt_name: str, context):
        if prompt_name not in self.prompts:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Prompt name does not exist")
            raise ValueError("Prompt name does not exist")

    def _raise_on_missing_prompt_version(self, prompt_name: str, version: int, context):
        if (
            prompt_name not in self.prompts
            or (prompt_name, version) not in self.prompts_versions
        ):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Prompt version does not exist")
            raise ValueError("Prompt version does not exist")

    def CreatePrompt(self, request: ProtoCreatePromptRequest, context):
        """Create a new prompt"""

        if request.prompt_name in self.prompts:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Prompt name already exists")
            raise ValueError("Prompt name already exists")

        if not self._is_prompt_name_valid(request.prompt_name):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad Prompt name")
            raise ValueError("Bad Prompt name")

        prompt_version_definition = ProtoPromptVersionDefinition(
            version_number=1,
            version_spec=request.prompt_version_spec,
            version_metadata=ProtoPromptVersionMetadata(
                created_by="nirh@qwak.com", created_at=Timestamp().GetCurrentTime()
            ),
        )

        prompt = ProtoPrompt(
            name=request.prompt_name,
            default_version_definition=prompt_version_definition,
            metadata=ProtoPromptMetadata(
                created_at=Timestamp().GetCurrentTime(), created_by="nirh@qwak.com"
            ),
            prompt_spec=ProtoPromptSpec(description=request.prompt_spec.description),
        )

        self.prompts[prompt.name] = prompt
        self.prompts_next_version[prompt.name] = 2
        self.prompts_versions[
            (prompt.name, prompt.default_version_definition.version_number)
        ] = prompt_version_definition

        return ProtoCreatePromptResponse(prompt=prompt)

    def CreatePromptVersion(self, request: ProtoCreatePromptVersionRequest, context):
        """
        Create new prompt version.
        Set new version in versions dict.
        Bump prompt next version.
        Set default version if needed
        """
        self._raise_on_missing_prompt(prompt_name=request.prompt_name, context=context)

        existing_prompt: ProtoPrompt = self.prompts[request.prompt_name]
        new_prompt_version_number: int = self.prompts_next_version[request.prompt_name]
        prompt_version_definition = ProtoPromptVersionDefinition(
            version_number=new_prompt_version_number,
            version_spec=request.prompt_version_spec,
            version_metadata=ProtoPromptVersionMetadata(
                created_by="nirh@qwak.com", created_at=Timestamp().GetCurrentTime()
            ),
        )

        self.prompts_next_version[request.prompt_name] = new_prompt_version_number + 1

        if request.set_default:
            existing_prompt.default_version_definition.CopyFrom(
                prompt_version_definition
            )

        self.prompts_versions[
            (request.prompt_name, new_prompt_version_number)
        ] = prompt_version_definition
        return ProtoCreatePromptVersionResponse(
            prompt_version=ProtoPromptVersion(
                prompt_name=request.prompt_name,
                prompt_version_definition=prompt_version_definition,
            )
        )

    def UpdatePrompt(self, request: ProtoUpdatePromptRequest, context):
        """Update Prompt"""
        self._raise_on_missing_prompt(prompt_name=request.prompt_name, context=context)

        existing_prompt: ProtoPrompt = self.prompts[request.prompt_name]
        existing_prompt.prompt_spec.CopyFrom(request.prompt_spec)

        return ProtoUpdatePromptResponse()

    def GetPromptByName(self, request: ProtoGetPromptByNameRequest, context):
        """Get prompt with its default version by name"""
        self._raise_on_missing_prompt(prompt_name=request.prompt_name, context=context)

        existing_prompt: ProtoPrompt = self.prompts[request.prompt_name]
        return ProtoGetPromptByNameResponse(prompt=existing_prompt)

    def GetPromptVersionByPromptName(
        self, request: ProtoGetPromptVersionByPromptNameRequest, context
    ):
        """Get prompt version by name and optional version number"""

        self._raise_on_missing_prompt(
            prompt_name=request.prompt_name,
            context=context,
        )

        self._raise_on_missing_prompt_version(
            prompt_name=request.prompt_name,
            version=request.version_number,
            context=context,
        )

        return ProtoGetPromptVersionByPromptNameResponse(
            prompt_version=ProtoPromptVersion(
                prompt_name=request.prompt_name,
                prompt_version_definition=self.prompts_versions[
                    (request.prompt_name, request.version_number)
                ],
            )
        )

    def DeletePrompt(self, request: ProtoDeletePromptRequest, context):
        """Delete prompt"""
        self._raise_on_missing_prompt(prompt_name=request.prompt_name, context=context)

        del self.prompts[request.prompt_name]
        del self.prompts_next_version[request.prompt_name]

        versions_to_delete: List[int] = [
            version
            for (name, version) in self.prompts_versions.keys()
            if name == request.prompt_name
        ]

        for v in versions_to_delete:
            del self.prompts_versions[(request.prompt_name, v)]

        return ProtoDeletePromptResponse()

    def DeletePromptVersion(self, request: ProtoDeletePromptVersionRequest, context):
        """Delete prompt version"""
        self._raise_on_missing_prompt(
            prompt_name=request.prompt_name,
            context=context,
        )

        self._raise_on_missing_prompt_version(
            prompt_name=request.prompt_name,
            version=request.version_number,
            context=context,
        )

        prompt_default_version: ProtoPrompt = self.prompts[request.prompt_name]
        if (
            prompt_default_version.default_version_definition.version_number
            == request.version_number
        ):
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Can't delete prompt default version")
            raise ValueError("Can't delete prompt default version")

        del self.prompts_versions[(request.prompt_name, request.version_number)]
        return ProtoDeletePromptVersionResponse()

    def SetDefaultPromptVersion(
        self, request: ProtoSetDefaultPromptVersionRequest, context
    ):
        """Set default prompt version"""
        self._raise_on_missing_prompt(
            prompt_name=request.prompt_name,
            context=context,
        )

        self._raise_on_missing_prompt_version(
            prompt_name=request.prompt_name,
            version=request.version_number,
            context=context,
        )
        existing_prompt: ProtoPrompt = self.prompts[request.prompt_name]
        prompt_version_definition: ProtoPromptVersionDefinition = self.prompts_versions[
            (request.prompt_name, request.version_number)
        ]
        existing_prompt.default_version_definition.CopyFrom(prompt_version_definition)
        return ProtoSetDefaultPromptVersionResponse()
