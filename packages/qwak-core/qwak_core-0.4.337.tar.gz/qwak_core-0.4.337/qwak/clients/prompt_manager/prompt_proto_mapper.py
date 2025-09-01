from typing import List, Optional

from _qwak_proto.qwak.model_descriptor.open_ai_descriptor_pb2 import (
    OpenAIModelDescriptor as ProtoOpenAIModelDescriptor,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_pb2 import (
    AIPromptMessageRole as ProtoAIPromptMessageRole,
    ChatMessage as ProtoChatMessage,
    ChatMessageTemplate as ProtoChatMessageTemplate,
    ChatPromptTemplate as ProtoChatPromptTemplate,
    HumanPromptMessageRole as ProtoHumanPromptMessageRole,
    PromptMessageRole as ProtoPromptMessageRole,
    PromptModelDescriptor as ProtoPromptModelDescriptor,
    PromptOpenAIProvider as ProtoPromptOpenAIProvider,
    PromptTemplate as ProtoPromptTemplate,
    PromptVersionDefinition as ProtoPromptVersionDefinition,
    PromptVersionSpec as ProtoPromptVersionSpec,
    SystemPromptMessageRole as ProtoSystemPromptMessageRole,
    TextTemplate as ProtoTextTemplate,
)
from qwak.clients.prompt_manager.model_descriptor_mapper import ModelDescriptorMapper
from qwak.exceptions import QwakException
from qwak.llmops.model.descriptor import ChatModelDescriptor, ModelDescriptor
from qwak.llmops.prompt.base import BasePrompt, ChatPrompt, RegisteredPrompt
from qwak.llmops.prompt.chat.message import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from qwak.llmops.prompt.chat.template import (
    AIMessagePromptTemplate,
    BaseStringMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from qwak.llmops.prompt.template import BasePromptTemplate


class PromptProtoMapper:
    @staticmethod
    def from_chat_prompt_template(
        chat_prompt_template: ProtoChatPromptTemplate,
    ) -> ChatPromptTemplate:
        messages: List[BaseStringMessagePromptTemplate] = []
        for chat_message in chat_prompt_template.chat_messages:
            template: str = chat_message.template.text_template.template
            role_type: str = chat_message.role.WhichOneof("role")
            if role_type == "human_role":
                messages.append(HumanMessagePromptTemplate(template=template))
            elif role_type == "system_role":
                messages.append(SystemMessagePromptTemplate(template=template))
            elif role_type == "ai_role":
                messages.append(AIMessagePromptTemplate(template=template))
            else:
                raise QwakException(
                    f"Got unsupported chat message type: {repr(chat_message)}"
                )

        return ChatPromptTemplate(messages=messages)

    @staticmethod
    def from_prompt_template(
        prompt_template: ProtoPromptTemplate,
    ) -> BasePromptTemplate:
        if prompt_template.WhichOneof("type") == "chat_prompt_template":
            return PromptProtoMapper.from_chat_prompt_template(
                chat_prompt_template=prompt_template.chat_prompt_template
            )
        else:
            raise QwakException(
                f"Got unsupported prompt template: {repr(prompt_template)}"
            )

    @staticmethod
    def to_prompt_model_descriptor(
        model_descriptor: ModelDescriptor,
    ) -> ProtoPromptModelDescriptor:
        proto_model_descriptor = ModelDescriptorMapper.to_model_descriptor(
            model_descriptor=model_descriptor
        )
        if isinstance(proto_model_descriptor, ProtoOpenAIModelDescriptor):
            return ProtoPromptModelDescriptor(
                open_ai_provider=ProtoPromptOpenAIProvider(
                    open_ai_model_descriptor=proto_model_descriptor
                )
            )

        raise QwakException(
            f"Got unsupported model descriptor: {repr(model_descriptor)}"
        )

    @staticmethod
    def _prompt_template_to_chat_message(
        msg: BaseStringMessagePromptTemplate,
    ) -> ProtoChatMessage:
        role: ProtoPromptMessageRole
        text_template: str = msg.template.template

        if isinstance(msg, SystemMessagePromptTemplate):
            role = ProtoPromptMessageRole(system_role=ProtoSystemPromptMessageRole())
        elif isinstance(msg, HumanMessagePromptTemplate):
            role = ProtoPromptMessageRole(human_role=ProtoHumanPromptMessageRole())
        elif isinstance(msg, AIMessagePromptTemplate):
            role = ProtoPromptMessageRole(ai_role=ProtoAIPromptMessageRole())
        else:
            raise QwakException(f"Got unsupported prompt template role: {repr(msg)}")

        return ProtoChatMessage(
            role=role,
            template=ProtoChatMessageTemplate(
                text_template=ProtoTextTemplate(template=text_template)
            ),
        )

    @staticmethod
    def _base_message_to_chat_message(msg: BaseMessage) -> ProtoChatMessage:
        role: ProtoPromptMessageRole
        text_template: str = msg.content

        if isinstance(msg, AIMessage):
            role = ProtoPromptMessageRole(ai_role=ProtoAIPromptMessageRole())
        elif isinstance(msg, HumanMessage):
            role = ProtoPromptMessageRole(human_role=ProtoHumanPromptMessageRole())
        elif isinstance(msg, SystemMessage):
            role = ProtoPromptMessageRole(system_role=ProtoSystemPromptMessageRole())
        else:
            raise QwakException(f"Got unsupported prompt template role: {repr(msg)}")

        return ProtoChatMessage(
            role=role,
            template=ProtoChatMessageTemplate(
                text_template=ProtoTextTemplate(template=text_template)
            ),
        )

    @staticmethod
    def to_proto_chat_prompt_template(
        prompt_template: ChatPromptTemplate,
    ) -> ProtoPromptTemplate:
        chat_messages: List[ProtoChatMessage] = []

        for msg in prompt_template.messages:
            if isinstance(msg, BaseStringMessagePromptTemplate):
                chat_messages.append(
                    PromptProtoMapper._prompt_template_to_chat_message(msg=msg)
                )
            elif isinstance(msg, BaseMessage):
                chat_messages.append(
                    PromptProtoMapper._base_message_to_chat_message(msg=msg)
                )

        return ProtoPromptTemplate(
            chat_prompt_template=ProtoChatPromptTemplate(chat_messages=chat_messages)
        )

    @staticmethod
    def to_proto_prompt_template(
        prompt_template: BasePromptTemplate,
    ) -> ProtoPromptTemplate:
        if isinstance(prompt_template, ChatPromptTemplate):
            return PromptProtoMapper.to_proto_chat_prompt_template(
                prompt_template=prompt_template
            )

        raise QwakException(f"Got unsupported prompt template: {repr(prompt_template)}")

    @staticmethod
    def to_prompt_version_spec(
        version_description: str,
        prompt_template: BasePromptTemplate,
        model_descriptor: Optional[ModelDescriptor],
    ) -> ProtoPromptVersionSpec:
        prompt_model_descriptor: Optional[ProtoPromptModelDescriptor] = None

        if model_descriptor:
            prompt_model_descriptor: ProtoPromptModelDescriptor = (
                PromptProtoMapper.to_prompt_model_descriptor(
                    model_descriptor=model_descriptor
                )
            )

        proto_prompt_template: ProtoPromptTemplate = (
            PromptProtoMapper.to_proto_prompt_template(prompt_template=prompt_template)
        )

        return ProtoPromptVersionSpec(
            description=version_description,
            prompt_template=proto_prompt_template,
            model_descriptor=prompt_model_descriptor,
        )

    @staticmethod
    def from_prompt_version_definition(
        prompt_version_def: ProtoPromptVersionDefinition,
    ) -> BasePrompt:
        model_descriptor: Optional[ModelDescriptor] = None
        prompt_template: ProtoPromptTemplate = (
            prompt_version_def.version_spec.prompt_template
        )
        base_prompt_template: BasePromptTemplate = (
            PromptProtoMapper.from_prompt_template(prompt_template)
        )

        if prompt_version_def.version_spec.HasField("model_descriptor"):
            model_descriptor: ModelDescriptor = (
                ModelDescriptorMapper.from_prompt_model_descriptor(
                    model_descriptor=prompt_version_def.version_spec.model_descriptor
                )
            )

        if isinstance(base_prompt_template, ChatPromptTemplate) and (
            not model_descriptor or isinstance(model_descriptor, ChatModelDescriptor)
        ):
            return ChatPrompt(template=base_prompt_template, model=model_descriptor)

    @staticmethod
    def from_prompt(
        name: str,
        prompt_description: str,
        version_description: str,
        version: int,
        target_default_version: bool,
        prompt_version_definition: ProtoPromptVersionDefinition,
    ) -> RegisteredPrompt:
        return RegisteredPrompt(
            name=name,
            prompt_description=prompt_description,
            version_description=version_description,
            version=version,
            _target_default_version=target_default_version,
            prompt=PromptProtoMapper.from_prompt_version_definition(
                prompt_version_def=prompt_version_definition
            ),
        )
