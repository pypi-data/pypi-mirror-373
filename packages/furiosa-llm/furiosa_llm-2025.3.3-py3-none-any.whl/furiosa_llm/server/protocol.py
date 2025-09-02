# Adapted from
# https://github.com/vllm-project/vllm/blob/4ef41b84766670c1bd8079f58d35bf32b5bcb3ab/vllm/entrypoints/openai/protocol.py

import time
from typing import Any, Dict, List, Literal, Optional, Union

from openai.types.chat import ChatCompletionMessageParam
from openai.types.model import Model as OpenAIModel
from pydantic import BaseModel, ConfigDict, Field, model_validator

from furiosa_llm.api import LLM, SamplingParams
from furiosa_llm.outputs import Logprob
from furiosa_llm.sampling_params import GuidedDecodingParams
from furiosa_llm.server.utils import random_uuid


class OpenAIBaseModel(BaseModel):
    # OpenAI API does allow extra fields
    model_config = ConfigDict(extra="allow")


class CompletionTokenUsageInfo(OpenAIBaseModel):
    accepted_prediction_tokens: int = 0
    audio_tokens: int = 0
    reasoning_tokens: int = 0
    rejected_prediction_tokens: int = 0


class UsageInfo(OpenAIBaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0
    completion_tokens_details: Optional[CompletionTokenUsageInfo] = None


class StreamOptions(OpenAIBaseModel):
    include_usage: Optional[bool] = True


class FunctionDefinition(OpenAIBaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ChatCompletionToolsParam(OpenAIBaseModel):
    type: Literal["function"] = "function"
    function: FunctionDefinition


class ChatCompletionNamedFunction(OpenAIBaseModel):
    name: str


class ChatCompletionNamedToolChoiceParam(OpenAIBaseModel):
    function: ChatCompletionNamedFunction
    type: Literal["function"] = "function"


class JsonSchemaResponseFormat(OpenAIBaseModel):
    name: str
    description: Optional[str] = None
    # schema is the field in openai but that causes conflicts with pydantic so
    # instead use json_schema with an alias
    json_schema: Optional[dict[str, Any]] = Field(default=None, alias='schema')
    strict: Optional[bool] = None


class ResponseFormat(OpenAIBaseModel):
    # type must be "json_schema", "json_object", or "text"
    type: Literal["text", "json_object", "json_schema"]
    json_schema: Optional[JsonSchemaResponseFormat] = None


class ChatCompletionRequest(OpenAIBaseModel):
    messages: List[ChatCompletionMessageParam]
    model: str
    logprobs: Optional[bool] = False
    top_logprobs: Optional[int] = None
    n: Optional[int] = 1
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False
    stream_options: Optional[StreamOptions] = None
    top_p: Optional[float] = 1.0
    best_of: Optional[int] = 1
    use_beam_search: bool = False
    top_k: int = -1
    min_p: float = 0.0
    length_penalty: float = 1.0
    early_stopping: bool = False
    min_tokens: int = 0

    # TODO: completely remove max_tokens when OpenAI removes it
    max_tokens: Optional[int] = Field(
        default=None,
        deprecated="max_tokens is deprecated in favor of the max_completion_tokens field",
    )
    max_completion_tokens: Optional[int] = None

    tools: Optional[List[ChatCompletionToolsParam]] = None
    tool_choice: Optional[
        Union[
            Literal["none"],
            Literal["auto"],
            Literal["required"],
            ChatCompletionNamedToolChoiceParam,
        ]
    ] = "none"
    # NOTE this will be ignored -- the model determines the behavior
    parallel_tool_calls: Optional[bool] = True

    # Structured output
    # TODO: support structural_tag
    response_format: Optional[ResponseFormat] = None
    guided_json: Optional[Union[str, dict, BaseModel]] = Field(
        default=None,
        description=("If specified, the output will follow the JSON schema."),
    )
    guided_regex: Optional[str] = Field(
        default=None,
        description=("If specified, the output will follow the regex pattern."),
    )
    guided_choice: Optional[list[str]] = Field(
        default=None,
        description=("If specified, the output will be exactly one of the choices."),
    )
    guided_grammar: Optional[str] = Field(
        default=None,
        description=("If specified, the output will follow the context free grammar."),
    )

    add_generation_prompt: bool = True

    return_tokens_as_token_ids: Optional[bool] = Field(
        default=None,
        description="If specified with 'logprobs', tokens are represented as strings of the form 'token_id:{token_id}' so that tokens that are not JSON-encodable can be identified.",
    )

    # Parameters that is supported by OpenAI but not by Furiosa.
    # All of them are no-op, but declared as a placeholder.
    audio: Optional[Dict[str, Any]] = None
    frequency_penalty: Optional[float] = 0.0
    function_call: Optional[Union[str, Dict[str, Any]]] = None  # Deprecated
    functions: Optional[List[Any]] = None  # Deprecated
    logit_bias: Optional[Dict[int, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    modalities: Optional[List[str]] = None
    prediction: Optional[Dict[str, Any]] = None
    presence_penalty: Optional[float] = 0.0
    reasoning_effort: Optional[str] = "medium"
    seed: Optional[int] = None
    service_tier: Optional[str] = "auto"
    stop: Optional[Union[str, List[str]]] = None
    store: Optional[bool] = False
    user: Optional[str] = None
    web_search_options: Optional[Dict[str, Any]] = None

    def to_sampling_params(self) -> SamplingParams:
        max_tokens = self.max_completion_tokens or self.max_tokens

        # Structured output
        # TODO: support structural_tag
        guided_json_object = None
        if self.response_format is not None:
            if self.response_format.type == "json_object":
                guided_json_object = True
            elif self.response_format.type == "json_schema":
                json_schema = self.response_format.json_schema
                assert json_schema is not None
                self.guided_json = json_schema.json_schema
        guided_decoding = GuidedDecodingParams.from_optional(
            json=self._get_guided_json_from_tool() or self.guided_json,
            regex=self.guided_regex,
            choice=self.guided_choice,
            grammar=self.guided_grammar,
            json_object=guided_json_object,
        )

        return SamplingParams.from_optional(
            n=self.n,
            best_of=self.best_of,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            use_beam_search=self.use_beam_search,
            length_penalty=self.length_penalty,
            early_stopping=self.early_stopping,
            logprobs=self.top_logprobs if self.logprobs else None,
            max_tokens=max_tokens,
            min_tokens=self.min_tokens,
            guided_decoding=guided_decoding,
        )

    # Copied from https://github.com/vllm-project/vllm/blob/27e8d1ea3ea9864f371f639daaa5315bf3250364/vllm/entrypoints/openai/protocol.py#L712-L784
    def _get_guided_json_from_tool(self) -> Optional[Union[str, dict, BaseModel]]:
        # user has chosen to not use any tool
        if self.tool_choice == "none" or self.tools is None:
            return None

        # user has chosen to use a named tool
        if type(self.tool_choice) is ChatCompletionNamedToolChoiceParam:
            tool_name = self.tool_choice.function.name
            tools = {tool.function.name: tool.function for tool in self.tools}
            if tool_name not in tools:
                raise ValueError(f"Tool '{tool_name}' has not been passed in `tools`.")
            tool = tools[tool_name]
            return tool.parameters

        if self.tool_choice == "required":
            # Pydantic schema generation cannot be used since the JSON schema
            # has to be constructed for a specific instantiation of a tool list
            # so that parameters of a function are correctly generated
            # based on the chosen function name
            def get_tool_schema(tool: ChatCompletionToolsParam) -> dict:
                return {
                    "properties": {
                        "name": {"type": "string", "enum": [tool.function.name]},
                        # parameters are always generated as '{}' in the final
                        # output if they are missing from the request
                        # (i.e. are None or '{}') so the schema is
                        # updated to produce an empty object in that case
                        "parameters": (
                            tool.function.parameters
                            if tool.function.parameters
                            else {"type": "object", "properties": {}}
                        ),
                    },
                    "required": ["name", "parameters"],
                }

            def get_tool_schema_defs(tools: list[ChatCompletionToolsParam]) -> dict:
                all_defs = dict[str, dict[str, Any]]()
                for tool in tools:
                    if tool.function.parameters is None:
                        continue
                    defs = tool.function.parameters.pop("$defs", {})
                    for def_name, def_schema in defs.items():
                        if def_name in all_defs and all_defs[def_name] != def_schema:
                            raise ValueError(
                                f"Tool definition '{def_name}' has "
                                "multiple schemas, which is not "
                                "supported."
                            )
                        else:
                            all_defs[def_name] = def_schema
                return all_defs

            json_schema = {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "anyOf": [get_tool_schema(tool) for tool in self.tools],
                },
            }
            json_schema_defs = get_tool_schema_defs(self.tools)
            if json_schema_defs:
                json_schema["$defs"] = json_schema_defs
            return json_schema

        return None

    @model_validator(mode="before")
    @classmethod
    def check_tool_usage(cls, data):
        # if "tool_choice" is not set, set to the default value based on "tools"
        if "tool_choice" not in data or data["tool_choice"] is None:
            if data.get("tools"):
                data["tool_choice"] = "auto"
            else:
                data["tool_choice"] = "none"

        # if "tool_choice" is "none" -- no validation is needed for tools
        if "tool_choice" in data and data["tool_choice"] == "none":
            return data

        # if "tool_choice" is specified -- validation
        if "tool_choice" in data:
            # ensure that if "tool choice" is specified, tools are present
            if "tools" not in data or data["tools"] is None:
                raise ValueError("When using `tool_choice`, `tools` must be set.")

            # make sure that tool choice is either a named tool
            # OR that it's set to "auto" or "required"
            if data["tool_choice"] not in ["auto", "required"] and not isinstance(
                data["tool_choice"], dict
            ):
                raise NotImplementedError(
                    f'Invalid value for `tool_choice`: {data["tool_choice"]}! '
                    'Only named tools, "none", "auto" or "required" '
                    'are supported.'
                )

            # if tool_choice is "required" but the "tools" list is empty,
            # override the data to behave like "none" to align with
            # OpenAI’s behavior.
            if (
                data["tool_choice"] == "required"
                and isinstance(data["tools"], list)
                and len(data["tools"]) == 0
            ):
                data["tool_choice"] = "none"
                del data["tools"]
                return data

            # ensure that if "tool_choice" is specified as an object,
            # it matches a valid tool
            correct_usage_message = (
                'Correct usage: `{"type": "function",' ' "function": {"name": "my_function"}}`'
            )
            if isinstance(data["tool_choice"], dict):
                valid_tool = False
                function = data["tool_choice"].get("function")
                if not isinstance(function, dict):
                    raise ValueError(
                        f"Invalid value for `function`: `{function}` in "
                        f"`tool_choice`! {correct_usage_message}"
                    )
                if "name" not in function:
                    raise ValueError(
                        f"Expected field `name` in `function` in "
                        f"`tool_choice`! {correct_usage_message}"
                    )
                function_name = function["name"]
                if not isinstance(function_name, str) or len(function_name) == 0:
                    raise ValueError(
                        f"Invalid `name` in `function`: `{function_name}`"
                        f" in `tool_choice`! {correct_usage_message}"
                    )
                for tool in data["tools"]:
                    if tool["function"]["name"] == function_name:
                        valid_tool = True
                        break
                if not valid_tool:
                    raise ValueError(
                        "The tool specified in `tool_choice` does not match any"
                        " of the specified `tools`"
                    )
        return data

    @model_validator(mode="before")
    @classmethod
    def alias_functions_to_tools(cls, data):
        """
        Move `functions` and `function_call` (which are deprecated) to `tools` and `tool_choice` when necessary.
        This validator must be placed below `check_tool_usage` to ensure that
        this validator runs before `check_tool_usage`.
        """
        if "functions" not in data or "tools" in data:
            return data

        data["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": func["name"],
                    "description": func.get("description"),
                    "parameters": func.get("parameters"),
                },
            }
            for func in data["functions"]
        ]

        if "function_call" in data:
            function_call_value = data["function_call"]
        else:
            function_call_value = "auto" if data["tools"] else "none"
        if "tool_choice" not in data:
            data["tool_choice"] = function_call_value
        return data


class CompletionRequest(OpenAIBaseModel):
    model: str
    prompt: Union[str, List[str], List[int], List[List[int]]]
    best_of: Optional[int] = 1
    logprobs: Optional[int] = None
    max_tokens: Optional[int] = 16
    n: int = 1
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0

    stream: Optional[bool] = False
    # XXX: stream_options has no effect in the current implementation
    stream_options: Optional[StreamOptions] = None
    use_beam_search: bool = False
    top_k: int = -1
    min_p: float = 0.0
    length_penalty: float = 1.0
    early_stopping: bool = False
    min_tokens: int = 0

    return_tokens_as_token_ids: Optional[bool] = Field(
        default=None,
        description=(
            "If specified with 'logprobs', tokens are represented as strings of the form 'token_id:{token_id}' so that tokens that are not JSON-encodable can be identified."
        ),
    )

    # Structured output
    # TODO: support structural_tag
    response_format: Optional[ResponseFormat] = Field(
        default=None,
        description=(
            "Similar to chat completion, this parameter specifies the format "
            "of output. Only {'type': 'json_object'}, {'type': 'json_schema'}"
            ", {'type': 'structural_tag'}, or {'type': 'text' } is supported."
        ),
    )
    guided_json: Optional[Union[str, dict, BaseModel]] = Field(
        default=None,
        description="If specified, the output will follow the JSON schema.",
    )
    guided_regex: Optional[str] = Field(
        default=None,
        description=("If specified, the output will follow the regex pattern."),
    )
    guided_choice: Optional[list[str]] = Field(
        default=None,
        description=("If specified, the output will be exactly one of the choices."),
    )
    guided_grammar: Optional[str] = Field(
        default=None,
        description=("If specified, the output will follow the context free grammar."),
    )

    # Parameters that is supported by OpenAI but not by Furiosa.
    # All of them are no-op, but declared as a placeholder.
    echo: Optional[bool] = False
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[int, float]] = None
    presence_penalty: Optional[float] = 0.0
    seed: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    suffix: Optional[str] = None
    user: Optional[str] = None

    def to_sampling_params(self) -> SamplingParams:
        guided_json_object = None
        if self.response_format is not None:
            if self.response_format.type == "json_object":
                guided_json_object = True
            elif self.response_format.type == "json_schema":
                json_schema = self.response_format.json_schema
                assert json_schema is not None
                self.guided_json = json_schema.json_schema
        guided_decoding = GuidedDecodingParams.from_optional(
            json=self.guided_json,
            regex=self.guided_regex,
            choice=self.guided_choice,
            grammar=self.guided_grammar,
            json_object=guided_json_object,
        )

        return SamplingParams.from_optional(
            n=self.n,
            best_of=self.best_of,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            use_beam_search=self.use_beam_search,
            length_penalty=self.length_penalty,
            early_stopping=self.early_stopping,
            logprobs=self.logprobs,
            max_tokens=self.max_tokens,
            min_tokens=self.min_tokens,
            guided_decoding=guided_decoding,
        )


class CompletionLogProbs(OpenAIBaseModel):
    text_offset: List[int] = Field(default_factory=list)
    token_logprobs: List[Optional[float]] = Field(default_factory=list)
    tokens: List[str] = Field(default_factory=list)
    top_logprobs: List[Optional[Dict[str, float]]] = Field(default_factory=list)


class CompletionResponseChoice(OpenAIBaseModel):
    index: int
    text: str
    logprobs: Optional[CompletionLogProbs] = None
    finish_reason: Optional[str] = None
    prompt_logprobs: Optional[List[Optional[Dict[int, Logprob]]]] = None


class CompletionResponse(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{random_uuid()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionResponseChoice]
    usage: UsageInfo


class CompletionResponseStreamChoice(OpenAIBaseModel):
    index: int
    text: str
    logprobs: Optional[CompletionLogProbs] = None
    finish_reason: Optional[str] = None


class CompletionStreamResponse(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{random_uuid()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionResponseStreamChoice]
    usage: Optional[UsageInfo] = Field(default=None)


class EmbeddingResponseData(OpenAIBaseModel):
    index: int
    object: str = "embedding"
    embedding: Union[List[float], str]


class EmbeddingResponse(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{random_uuid()}")
    object: str = "list"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    data: List[EmbeddingResponseData]
    usage: UsageInfo


class FunctionCall(OpenAIBaseModel):
    name: str
    arguments: str


class ToolCall(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-tool-{random_uuid()}")
    type: Literal["function"] = "function"
    function: FunctionCall


class ChatMessage(OpenAIBaseModel):
    role: str
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)


class ChatCompletionLogProb(OpenAIBaseModel):
    token: str
    logprob: float = -9999.0
    bytes: Optional[List[int]] = None


class ChatCompletionLogProbsContent(ChatCompletionLogProb):
    top_logprobs: List[ChatCompletionLogProb] = Field(default_factory=list)


class ChatCompletionLogProbs(OpenAIBaseModel):
    content: Optional[List[ChatCompletionLogProbsContent]] = None


class ChatCompletionResponseChoice(OpenAIBaseModel):
    index: int
    message: ChatMessage
    logprobs: Optional[ChatCompletionLogProbs] = None
    finish_reason: Optional[str] = None


class ChatCompletionResponse(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{random_uuid()}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo
    prompt_logprobs: Optional[List[Optional[Dict[int, Logprob]]]] = None


class DeltaFunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


# a tool call delta where everything is optional
class DeltaToolCall(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-tool-{random_uuid()}")
    type: Literal["function"] = "function"
    index: int
    function: Optional[DeltaFunctionCall] = None


class DeltaMessage(OpenAIBaseModel):
    role: Optional[str] = None
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: List[DeltaToolCall] = Field(default_factory=list)


class ChatCompletionResponseStreamChoice(OpenAIBaseModel):
    index: int
    delta: DeltaMessage
    logprobs: Optional[ChatCompletionLogProbs] = None
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(OpenAIBaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{random_uuid()}")
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseStreamChoice]
    usage: Optional[UsageInfo] = Field(default=None)


class ExtractedToolCallInformation(BaseModel):
    # indicate if tools were called
    tools_called: bool

    # extracted tool calls
    tool_calls: List[ToolCall]

    # content - per OpenAI spec, content AND tool calls can be returned rarely
    # But some models will do this intentionally
    content: Optional[str] = None


class Model(OpenAIModel):
    artifact_id: str
    max_prompt_len: int
    max_context_len: int

    # TODO: Add runtime-related configuration data.
    @classmethod
    def from_llm(cls, llm: LLM) -> "Model":
        assert llm.max_seq_len_to_capture is not None
        return cls(
            id=llm.model_metadata.pretrained_id,
            created=int(time.time()),
            object="model",
            owned_by="furiosa-ai",
            artifact_id=llm.artifact_id,
            max_prompt_len=llm.prompt_max_seq_len,
            max_context_len=llm.max_seq_len_to_capture,
        )


class ModelsResponse(OpenAIBaseModel):
    object: Literal["list"] = "list"
    data: List[Model]

    @classmethod
    def from_llm(cls, llm: LLM) -> "ModelsResponse":
        return cls(data=[Model.from_llm(llm)])


class ErrorResponse(OpenAIBaseModel):
    object: str = "error"
    message: str
    type: str
    param: Optional[str] = None
    code: int
