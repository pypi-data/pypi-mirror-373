from typing import Optional

from _qwak_proto.qwak.prompt.v1.prompt.prompt_pb2 import (
    Prompt as ProtoPrompt,
    PromptVersion as ProtoPromptVersion,
    PromptVersionDefinition as ProtoPromptVersionDefinition,
    PromptVersionSpec as ProtoPromptVersionSpec,
)
from qwak.clients.prompt_manager.prompt_manager_client import PromptManagerClient
from qwak.clients.prompt_manager.prompt_proto_mapper import PromptProtoMapper
from qwak.exceptions import QwakException
from qwak.llmops.prompt.base import BasePrompt, ChatPrompt, RegisteredPrompt


class PromptManager:
    _prompt_manager_client: PromptManagerClient

    def __init__(self):
        self._prompt_manager_client = PromptManagerClient()

    def register(
        self,
        name: str,
        prompt: BasePrompt,
        prompt_description: Optional[str] = None,
        version_description: Optional[str] = None,
    ) -> RegisteredPrompt:
        """
        Registers a new prompt in Qwak platform. Name must be unique
         and conform to ^[a-z0-9](?:[-_]?[a-z0-9]+)+$
        """
        if not isinstance(prompt, ChatPrompt):
            raise QwakException(f"Got unsupported prompt type: {prompt}")

        version_spec: ProtoPromptVersionSpec = PromptProtoMapper.to_prompt_version_spec(
            version_description=version_description,
            prompt_template=prompt.template,
            model_descriptor=prompt.model,
        )

        registered_prompt: ProtoPrompt = self._prompt_manager_client.create_prompt(
            name=name, prompt_description=prompt_description, version_spec=version_spec
        )

        return PromptProtoMapper.from_prompt(
            name=registered_prompt.name,
            prompt_description=registered_prompt.prompt_spec.description,
            version_description=registered_prompt.default_version_definition.version_spec.description,
            version=registered_prompt.default_version_definition.version_number,
            target_default_version=True,
            prompt_version_definition=registered_prompt.default_version_definition,
        )

    def update(
        self,
        name: str,
        prompt: BasePrompt,
        version_description: Optional[str] = None,
        set_default: bool = False,
    ) -> RegisteredPrompt:
        """
        Creates a new version for an existing prompt, prompt name must already exist.
        `set_default` set to True if this version is to become the default one immediately.
        """
        if not isinstance(prompt, ChatPrompt):
            raise QwakException(f"Got unsupported prompt type: {prompt}")

        version_spec: ProtoPromptVersionSpec = PromptProtoMapper.to_prompt_version_spec(
            version_description=version_description,
            prompt_template=prompt.template,
            model_descriptor=prompt.model,
        )

        prompt_version: ProtoPromptVersion = (
            self._prompt_manager_client.create_prompt_version(
                name=name, version_spec=version_spec, set_default=set_default
            )
        )

        version_for_get_request = (
            None
            if set_default
            else prompt_version.prompt_version_definition.version_number
        )
        return self.get_prompt(name=name, version=version_for_get_request)

    def set_default(self, name: str, version: int):
        """
        Set a version of a registered prompt named: `name`, as the default version
        """
        self._prompt_manager_client.set_default_prompt_version(
            name=name, version=version
        )

    def delete_prompt(self, name: str):
        """
        Delete all version of a prompt, by name
        """
        self._prompt_manager_client.delete_prompt(name=name)

    def delete_prompt_version(self, name: str, version: int):
        """
        Deletes a specific version of a registered prompt
        """
        self._prompt_manager_client.delete_prompt_version(name=name, version=version)

    def get_prompt(self, name: str, version: Optional[int] = None) -> RegisteredPrompt:
        """
        Get a registered prompt by name. To get the default version omit the `version` param, else
        fetch the specified version.
        """

        prompt_default_version: ProtoPrompt = (
            self._prompt_manager_client.get_prompt_by_name(name=name)
        )
        prompt_version_definition: ProtoPromptVersionDefinition = (
            prompt_default_version.default_version_definition
        )
        if version:
            prompt_version: ProtoPromptVersion = (
                self._prompt_manager_client.get_prompt_version_by_name(
                    name=name, version=version
                )
            )
            prompt_version_definition = prompt_version.prompt_version_definition

        return PromptProtoMapper.from_prompt(
            name=prompt_default_version.name,
            prompt_description=prompt_default_version.prompt_spec.description,
            version_description=prompt_version_definition.version_spec.description,
            version=prompt_version_definition.version_number,
            target_default_version=not bool(version),
            prompt_version_definition=prompt_version_definition,
        )
