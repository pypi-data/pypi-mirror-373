from typing import List, Optional, Union

from _qwak_proto.qwak.model_descriptor.open_ai_descriptor_pb2 import (
    OpenAICapabilities as ProtoOpenAICapabilities,
    OpenAIChatAPI as ProtoOpenAIChatAPI,
    OpenAIChatModelParams as ProtoOpenAIChatModelParams,
    OpenAIModelDescriptor as ProtoOpenAIModelDescriptor,
    ToolChoice as ProtoToolChoice,
    Tools as ProtoTools,
)
from _qwak_proto.qwak.prompt.v1.prompt.prompt_pb2 import (
    PromptModelDescriptor as ProtoPromptModelDescriptor,
    PromptOpenAIProvider as ProtoPromptOpenAIProvider,
)
from google.protobuf import json_format
from google.protobuf.struct_pb2 import ListValue, Struct
from qwak.exceptions import QwakException
from qwak.llmops.generation.chat.openai.types.chat.chat_completion_named_tool_choice_param import (
    ChatCompletionNamedToolChoiceParam,
)
from qwak.llmops.generation.chat.openai.types.chat.chat_completion_tool_param import (
    ChatCompletionToolParam,
)
from qwak.llmops.model.descriptor import ModelDescriptor, OpenAIChat


class ModelDescriptorMapper:
    @staticmethod
    def _from_tool_choice(
        openai_chat_params: ProtoOpenAIChatModelParams,
    ) -> Optional[Union[str, ChatCompletionNamedToolChoiceParam]]:
        _tool_choice: Optional[Union[str, ChatCompletionNamedToolChoiceParam]] = None
        if openai_chat_params.HasField("tool_choice"):
            if openai_chat_params.tool_choice.WhichOneof("value_type") == "json":
                _tool_choice = json_format.MessageToDict(
                    openai_chat_params.tool_choice.json
                )
            elif openai_chat_params.tool_choice.WhichOneof("value_type") == "literal":
                _tool_choice = openai_chat_params.tool_choice.literal
        return _tool_choice

    @staticmethod
    def from_openai_chat_capability(
        model_id: str, openai_chat_params: ProtoOpenAIChatModelParams
    ) -> OpenAIChat:
        p = openai_chat_params
        _tool_choice: Union[str, ChatCompletionNamedToolChoiceParam] = (
            ModelDescriptorMapper._from_tool_choice(
                openai_chat_params=openai_chat_params
            )
        )
        _tools: List[ChatCompletionToolParam] = []

        if p.HasField("tools_spec"):
            for tool in p.tools_spec.tools:
                _tools.append(json_format.MessageToDict(tool))

        return OpenAIChat(
            model_id=model_id,
            frequency_penalty=(
                p.frequency_penalty if p.HasField("frequency_penalty") else None
            ),
            logit_bias=(
                {k: int(v) for k, v in p.logit_bias.items()}
                if p.HasField("logit_bias")
                else None
            ),
            logprobs=p.logprobs if p.HasField("logprobs") else None,
            max_tokens=p.max_tokens if p.HasField("max_tokens") else None,
            n=p.n if p.HasField("n") else None,
            presence_penalty=(
                p.presence_penalty if p.HasField("presence_penalty") else None
            ),
            response_format=(
                p.response_format if p.HasField("response_format") else None
            ),  # noqa
            seed=p.seed if p.HasField("seed") else None,
            stop=[_ for _ in p.stop] if p.HasField("stop") else None,
            temperature=p.temperature if p.HasField("temperature") else None,
            top_p=p.top_p if p.HasField("top_p") else None,
            top_logprobs=p.top_logprobs if p.HasField("top_logprobs") else None,
            user=p.user if p.HasField("user") else None,
            tool_choice=_tool_choice if p.HasField("tool_choice") else None,
            tools=_tools if p.HasField("tools_spec") else None,
        )

    @staticmethod
    def from_prompt_openai_provider(
        open_ai_provider: ProtoPromptOpenAIProvider,
    ) -> ModelDescriptor:
        descriptor: ProtoOpenAIModelDescriptor = (
            open_ai_provider.open_ai_model_descriptor
        )
        model_id: str = descriptor.model_id

        if descriptor.capabilities.WhichOneof("optional_chat"):
            return ModelDescriptorMapper.from_openai_chat_capability(
                model_id=model_id,
                openai_chat_params=descriptor.capabilities.chat_api.chat_params,
            )
        else:
            raise QwakException(
                f"Got unsupported openai capability: {repr(open_ai_provider)}"
            )

    @staticmethod
    def from_prompt_model_descriptor(
        model_descriptor: ProtoPromptModelDescriptor,
    ) -> ModelDescriptor:
        if model_descriptor.WhichOneof("model_provider") == "open_ai_provider":
            return ModelDescriptorMapper.from_prompt_openai_provider(
                model_descriptor.open_ai_provider
            )
        else:
            raise QwakException(
                f"Got unsupported model descriptor: {repr(model_descriptor)}"
            )

    @staticmethod
    def to_openai_chat(model_descriptor: OpenAIChat) -> ProtoOpenAIModelDescriptor:
        d: OpenAIChat = model_descriptor
        logit_bias_struct = Struct()

        logit_bias_struct.update(d.logit_bias) if d.logit_bias else None

        stop_list_value = ListValue()
        stop_list_value.extend(d.stop) if d.stop else None
        tool_choice_proto: ProtoToolChoice

        if isinstance(d.tool_choice, str):
            tool_choice_proto = ProtoToolChoice(literal=d.tool_choice)
        elif d.tool_choice is not None:
            tool_choice_struct = Struct()
            tool_choice_struct.update(d.tool_choice)
            tool_choice_proto = ProtoToolChoice(json=tool_choice_struct)

        tools_structs = []
        if d.tools:
            for tool in d.tools:
                s = Struct()
                s.update(tool)
                tools_structs.append(s)

        tools_proto = ProtoTools(tools=tools_structs)

        model_capabilities = ProtoOpenAICapabilities(
            chat_api=ProtoOpenAIChatAPI(
                chat_params=ProtoOpenAIChatModelParams(
                    frequency_penalty=d.frequency_penalty,
                    logit_bias=logit_bias_struct if d.logit_bias else None,
                    logprobs=d.logprobs,
                    max_tokens=d.max_tokens,
                    n=d.n,
                    presence_penalty=d.presence_penalty,
                    response_format=(
                        d.response_format if d.response_format else None
                    ),  # noqa
                    seed=d.seed,
                    stop=stop_list_value if d.stop else None,
                    temperature=d.temperature,
                    tool_choice=tool_choice_proto if d.tool_choice else None,
                    tools_spec=tools_proto if d.tools else None,
                    top_logprobs=d.top_logprobs,
                    top_p=d.top_p,
                    user=d.user,
                )
            )
        )

        return ProtoOpenAIModelDescriptor(
            model_id=model_descriptor.model_id, capabilities=model_capabilities
        )

    @staticmethod
    def to_model_descriptor(
        model_descriptor: ModelDescriptor,
    ) -> Union[ProtoOpenAIModelDescriptor]:
        if isinstance(model_descriptor, OpenAIChat):
            return ModelDescriptorMapper.to_openai_chat(model_descriptor)

        raise QwakException(
            f"Got unsupported model descriptor: {repr(model_descriptor)}"
        )
