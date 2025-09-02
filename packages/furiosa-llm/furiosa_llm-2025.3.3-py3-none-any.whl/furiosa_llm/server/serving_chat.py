import asyncio
from http import HTTPStatus
import json
from logging import Logger
import re
import time
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Final,
    List,
    Optional,
    Sequence,
    Union,
)

from fastapi import Request
import partial_json_parser  # type: ignore[import-untyped]
from pydantic import TypeAdapter

from furiosa_llm.api import LLM, RequestOutput
from furiosa_llm.llm_engine import AsyncLLMEngine
from furiosa_llm.outputs import CompletionOutput, RequestOutputKind
from furiosa_llm.server.metrics import RequestMetrics
from furiosa_llm.server.protocol import (
    ChatCompletionLogProb,
    ChatCompletionLogProbs,
    ChatCompletionLogProbsContent,
    ChatCompletionNamedToolChoiceParam,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    CompletionTokenUsageInfo,
    DeltaFunctionCall,
    DeltaMessage,
    DeltaToolCall,
    ErrorResponse,
    FunctionCall,
    FunctionDefinition,
    Logprob,
    ToolCall,
    UsageInfo,
)
from furiosa_llm.server.reasoning_parsers import ReasoningParser, ReasoningParserManager
from furiosa_llm.server.serving_base import OpenAIServing
from furiosa_llm.server.tool_parsers import ToolParser, ToolParserManager
from furiosa_llm.server.utils import (
    AnyTokenizer,
    ConversationMessage,
    handle_disconnect,
    random_tool_call_id,
    random_uuid,
)

logger = Logger(__name__)


class OpenAIServingChat(OpenAIServing):
    def __init__(
        self,
        llm: LLM,
        response_role: str = "assistant",
        *,
        chat_template: Optional[str],
        return_tokens_as_token_ids: bool = False,
        reasoning_parser: Optional[str] = None,
        enable_auto_tools: bool = False,
        tool_parser: Optional[str] = None,
    ):
        self.async_llm_engine: AsyncLLMEngine = AsyncLLMEngine.from_llm(llm)
        self.tokenizer: AnyTokenizer = llm.tokenizer
        self.model_name = llm.model_metadata.pretrained_id
        self.return_tokens_as_token_ids = return_tokens_as_token_ids

        self.response_role = response_role
        self.chat_template = chat_template
        self.reasoning_parser: Optional[Callable[[AnyTokenizer], ReasoningParser]] = None

        self.enable_auto_tools = enable_auto_tools
        if self.enable_auto_tools:
            try:
                # XXX(n0gu): Copied from vllm. Currently this code path is not used since only llama3_json parser is supported,
                # but it may be used in the future.
                if tool_parser == "pythonic" and self.model_name.startswith("meta-llama/Llama-3.2"):
                    logger.warning("Llama3.2 models may struggle to emit valid pythonic tool calls")
                self.tool_parser = ToolParserManager.get_tool_parser(tool_parser)
            except Exception as e:
                raise TypeError(
                    "Error: --enable-auto-tool-choice requires "
                    f"tool_parser:'{tool_parser}' which has not "
                    "been registered"
                ) from e

        if reasoning_parser:
            try:
                self.reasoning_parser = ReasoningParserManager.get_reasoning_parser(
                    reasoning_parser
                )
                assert self.reasoning_parser is not None
            except Exception as e:
                raise TypeError(f"{reasoning_parser=} has not been registered") from e

        # Hack to pre-warm tokenizer and pre-compile default chat template
        try:
            self.tokenizer.apply_chat_template(
                [ConversationMessage({"role": "user", "content": "Hello!"})],
                chat_template=self.chat_template,
                add_generation_prompt=True,
                tokenize=True,
            )
        except Exception as e:
            logger.warning("Error in pre-warming tokenizer and chat template: %s", e)

    async def create_chat_completion(
        self,
        request: ChatCompletionRequest,
        raw_request: Request,
        metrics: RequestMetrics,
    ) -> Union[AsyncGenerator[str, None], ChatCompletionResponse, ErrorResponse]:
        """
        Completion API similar to OpenAI's API.

        See https://platform.openai.com/docs/api-reference/chat/create
        for the API specification. This API mimics the OpenAI
        ChatCompletion API.
        """
        try:
            if request.tool_choice == "auto" and not (
                self.enable_auto_tools and self.tool_parser is not None
            ):
                # for hf tokenizers, "auto" tools requires
                # --enable-auto-tool-choice and --tool-call-parser
                return self.create_error_response(
                    "\"auto\" tool choice requires "
                    "--enable-auto-tool-choice and --tool-call-parser to be set"
                )

            messages = [ConversationMessage(m) for m in request.messages]  # type: ignore
            tools = (
                [tool.model_dump() for tool in request.tools]
                if (request.tools and request.tool_choice != "none")
                else None
            )
            # TODO: Support `chat_template` field in the request and use it as vllm does.
            prompt_text: str = self.tokenizer.apply_chat_template(
                messages,
                tools=tools,
                chat_template=self.chat_template,
                add_generation_prompt=True,
                tokenize=False,
            )
        except Exception as e:
            logger.error("Error in applying chat template from request: %s", e)
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))

        try:
            sampling_params = request.to_sampling_params()
            # XXX(n0gu):
            # We call .encode() here even though it will be called again in AsyncLLMEngine.generate().
            # This is because passing pre-encoded tokens (List[int]) to generate() results in higher latency (!)
            # due to issue in .decode() (https://github.com/huggingface/transformers/issues/36872).
            # So passing the raw string is currently optimal.
            sampling_params.verify_and_finalize_max_tokens(
                input_prompt_len=len(self.tokenizer.encode(prompt_text, add_special_tokens=False)),
                model_max_prompt_len=self.async_llm_engine.prompt_max_seq_len,
                model_max_context_len=self.async_llm_engine.max_seq_len_to_capture,
            )
            metrics.max_tokens_request = sampling_params.max_tokens
        except ValueError as e:
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))

        request_id = f"chat-{random_uuid()}"

        stream = (
            request.stream
            and (request.best_of is None or request.n == request.best_of)
            and not request.use_beam_search
        )
        if stream:
            sampling_params.output_kind = RequestOutputKind.DELTA
            result_generator = self.async_llm_engine.generate(
                prompt_text, sampling_params, request_id
            )
            asyncio.create_task(
                handle_disconnect(raw_request, lambda: self._abort_request(request_id))
            )
            return self.chat_completion_stream_generator(
                request,
                result_generator,
                request_id,
                metrics,
            )

        try:
            sampling_params.output_kind = RequestOutputKind.FINAL
            result_generator = self.async_llm_engine.generate(
                prompt_text, sampling_params, request_id
            )
            asyncio.create_task(
                handle_disconnect(raw_request, lambda: self._abort_request(request_id))
            )

            return await self.chat_completion_full_generator(
                request,
                result_generator,
                request_id,
                metrics,
            )
        except ValueError as e:
            # TODO(vllm): Use a vllm-specific Validation Error
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))

    async def chat_completion_stream_generator(
        self,
        request: ChatCompletionRequest,
        result_generator: AsyncIterator[RequestOutput],
        request_id: str,
        metrics: RequestMetrics,
    ) -> AsyncGenerator[str, None]:
        created_time = int(time.time())
        chunk_object_type: Final = "chat.completion.chunk"

        num_choices = 1 if request.n is None else request.n
        previous_num_tokens = [0] * num_choices
        finish_reason_sent = [False] * num_choices
        reasoning_full_text = [""] * num_choices
        usage_prompt_tokens = 0
        usage_completion_tokens = 0
        usage_completion_tokens_reasoning = 0

        reasoning_enabled = self.reasoning_parser is not None
        auto_tools_enabled = bool(self.enable_auto_tools and self.tool_parser)
        is_named_tool_call = isinstance(request.tool_choice, ChatCompletionNamedToolChoiceParam)
        is_tool_choice_required = request.tool_choice == "required"
        is_tool_choice_auto = request.tool_choice in ["auto", None]

        # Determine whether tools are in use with "auto" tool choice
        should_stream_with_auto_tool_parsing = (
            is_tool_choice_auto and auto_tools_enabled and request.tools
        )

        all_previous_token_ids: Optional[List[List[int]]]
        function_name_returned = [False] * num_choices

        # Always track previous_texts for comprehensive output logging
        previous_texts = [""] * num_choices

        # Only one of these will be used, thus previous_texts and
        # all_previous_token_ids will not be used twice in the same iteration.
        if should_stream_with_auto_tool_parsing or reasoning_enabled:
            # These are only required in "auto" tool choice case
            all_previous_token_ids = [[]] * num_choices
            # For reasoning parser and tool call all enabled
            added_content_delta_arr = [False] * num_choices
            reasoning_end_arr = [False] * num_choices
        else:
            all_previous_token_ids = None

        if reasoning_enabled:
            try:
                reasoning_parser = self.reasoning_parser(self.tokenizer)  # type: ignore
            except RuntimeError as e:
                logger.exception("Error in reasoning parser creation.")
                data = self.create_streaming_error_response(str(e))
                yield f"data: {data}\n\n"
                metrics.request_completed = time.monotonic()
                metrics.request_success = False
                yield "data: [DONE]\n\n"
                return

        # Prepare the tool parser if it's needed
        try:
            if should_stream_with_auto_tool_parsing:
                tool_parsers: List[Optional[ToolParser]] = [
                    self.tool_parser(self.tokenizer)
                ] * num_choices
            else:
                tool_parsers = [None] * num_choices
        except Exception as e:
            logger.exception("Error in tool parser creation.")
            data = self.create_streaming_error_response(str(e))
            yield f"data: {data}\n\n"

            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            yield "data: [DONE]\n\n"
            return

        first_iteration = True
        try:
            async for res in result_generator:
                if first_iteration:
                    metrics.set_running()
                    len_prompt_tokens = len(res.prompt_token_ids)
                    usage_prompt_tokens = len_prompt_tokens
                    metrics.increment_prompt_tokens(len_prompt_tokens)
                    role = self.get_chat_request_role(request)
                    for i in range(num_choices):
                        choice_data = ChatCompletionResponseStreamChoice(
                            index=i,
                            delta=DeltaMessage(
                                role=role,
                                content="",
                            ),
                            logprobs=None,
                            finish_reason=None,
                        )
                        chunk = ChatCompletionStreamResponse(
                            id=request_id,
                            object=chunk_object_type,
                            created=created_time,
                            choices=[choice_data],
                            model=self.model_name,
                        )

                        data = chunk.model_dump_json(exclude_unset=True)
                        yield f"data: {data}\n\n"
                    first_iteration = False

                for output in res.outputs:
                    len_completion_tokens = len(output.token_ids)
                    usage_completion_tokens += len_completion_tokens
                    metrics.increment_generation_tokens(len_completion_tokens)
                    i = output.index
                    tool_parser = tool_parsers[i]

                    if finish_reason_sent[i]:
                        continue

                    if request.logprobs and request.top_logprobs is not None:
                        assert output.logprobs is not None, "Did not output logprobs"
                        return_as_token_id = (
                            request.return_tokens_as_token_ids is not None
                            and request.return_tokens_as_token_ids
                        )
                        for token_id_to_logprob in output.logprobs:
                            for token_id, logprob in token_id_to_logprob.items():
                                logprob.decoded_token = self._get_decoded_token(
                                    logprob,
                                    token_id,
                                    self.tokenizer,
                                    return_as_token_id=return_as_token_id,
                                )
                        logprobs = self._create_chat_logprobs(
                            token_ids=output.token_ids,
                            top_logprobs=output.logprobs,
                            tokenizer=self.tokenizer,
                            num_output_top_logprobs=request.top_logprobs,
                            return_as_token_id=request.return_tokens_as_token_ids,
                        )
                    else:
                        logprobs = None

                    delta_text = output.text

                    if not delta_text and not output.token_ids and not previous_num_tokens[i]:
                        # Chunked prefill case, don't return empty chunks
                        continue
                    if delta_text == "" and output.finish_reason is None:
                        # EOS case, don't return empty content
                        continue

                    delta_message: Optional[DeltaMessage]

                    # just update current_text and current_token_ids
                    if should_stream_with_auto_tool_parsing or reasoning_enabled:
                        assert previous_texts is not None
                        assert all_previous_token_ids is not None
                        previous_text = previous_texts[i]
                        previous_token_ids = all_previous_token_ids[i]
                        current_text = previous_text + delta_text
                        current_token_ids = previous_token_ids + list(output.token_ids)

                    # handle streaming deltas for tools with named tool_choice
                    if is_named_tool_call:
                        # XXX(n0gu): as of release 2025.03, no model supports both tool calling and reasoning.
                        # Therefore this branch will not be tested until a model supports both.
                        if (
                            reasoning_enabled
                            and not reasoning_end_arr[i]
                            and not reasoning_parser.is_reasoning_end(previous_token_ids)
                        ):
                            delta_message = reasoning_parser.extract_reasoning_content_streaming(
                                previous_text,
                                current_text,
                                delta_text,
                                previous_token_ids,
                                current_token_ids,
                                output.token_ids,
                            )
                            # When encountering think end id in delta_token_ids
                            # or think end id in prompt_token_ids i.e {"enable_thinking": False},
                            # set reasoning status to end.
                            # Only keep 'content', remove 'reasoning_content'.
                            if reasoning_parser.is_reasoning_end(output.token_ids) or (
                                res.prompt_token_ids
                                and reasoning_parser.is_reasoning_end(res.prompt_token_ids)
                            ):
                                reasoning_end_arr[i] = True
                                if delta_message and delta_message.content:
                                    # This need to be added to next `delta_text`
                                    current_text = delta_message.content
                                    delta_message.content = None
                                else:
                                    current_text = ""
                        else:
                            # Just to add remaining `content`
                            if reasoning_enabled:
                                delta_text = previous_text + delta_text
                                current_text = ""

                            if function_name_returned[i]:
                                delta_tool_call = DeltaToolCall(
                                    index=i, function=DeltaFunctionCall(arguments=delta_text)
                                )
                            else:
                                delta_tool_call = DeltaToolCall(
                                    id=random_tool_call_id(),
                                    type="function",
                                    index=i,
                                    function=DeltaFunctionCall(
                                        name=request.tool_choice.function.name, arguments=delta_text  # type: ignore
                                    ),
                                )
                                function_name_returned[i] = True

                            delta_message = DeltaMessage(
                                tool_calls=[
                                    delta_tool_call,
                                ]
                            )

                    elif is_tool_choice_required:
                        assert previous_texts is not None
                        previous_text = previous_texts[i]
                        current_text = previous_text + delta_text
                        fn_name_returned = function_name_returned[i]

                        # XXX(n0gu): ditto (untested until a model supports both tool calling and reasoning)
                        if reasoning_enabled:
                            _, content = reasoning_parser.extract_reasoning_content(
                                current_text, request
                            )
                        else:
                            content = current_text
                        delta_message, function_name_returned[i] = (
                            self.extract_tool_call_required_streaming(
                                previous_text=previous_text,
                                current_text=content,
                                delta_text=delta_text,
                                function_name_returned=fn_name_returned,
                            )
                        )

                    # XXX(n0gu): ditto (untested until a model supports both tool calling and reasoning)
                    elif should_stream_with_auto_tool_parsing and reasoning_enabled:
                        assert tool_parser is not None
                        assert reasoning_parser is not None
                        assert added_content_delta_arr is not None
                        assert reasoning_end_arr is not None
                        output_token_ids = list(output.token_ids)
                        if not reasoning_end_arr[i]:
                            delta_message = reasoning_parser.extract_reasoning_content_streaming(
                                previous_text,
                                current_text,
                                delta_text,
                                previous_token_ids,
                                current_token_ids,
                                output_token_ids,
                            )
                            # When encountering think end id in prompt_token_ids
                            # i.e {"enable_thinking": False},
                            # set reasoning status to end.
                            # Remove the text and token ids related
                            # to 'reasoning_content'.
                            if res.prompt_token_ids and reasoning_parser.is_reasoning_end(
                                res.prompt_token_ids
                            ):
                                reasoning_end_arr[i] = True
                                current_token_ids = output_token_ids
                                if delta_message and delta_message.content:
                                    current_text = delta_message.content
                                    delta_message.content = None
                                else:
                                    current_text = ""
                            # When encountering think end id in delta_token_ids,
                            # set reasoning status to end.
                            # Remove the text and token ids related
                            # to 'reasoning_content'.
                            if reasoning_parser.is_reasoning_end(output_token_ids):
                                reasoning_end_arr[i] = True
                                current_token_ids = reasoning_parser.extract_content_ids(
                                    output_token_ids
                                )
                                if delta_message and delta_message.content:
                                    current_text = delta_message.content
                                    delta_message.content = None
                                else:
                                    current_text = ""

                        # handle tool calls only after reasoning is done,
                        else:
                            delta_token_ids = output_token_ids
                            # First time to tool call,
                            # add the remaining text and token ids
                            # to delta from previous
                            if not added_content_delta_arr[i]:
                                added_content_delta_arr[i] = True
                                previous_text = ""
                                previous_token_ids = []
                                delta_text = current_text
                                delta_token_ids = current_token_ids

                            delta_message = tool_parser.extract_tool_calls_streaming(
                                previous_text=previous_text,
                                current_text=current_text,
                                delta_text=delta_text,
                                previous_token_ids=previous_token_ids,
                                current_token_ids=current_token_ids,
                                delta_token_ids=delta_token_ids,
                                request=request,
                            )

                    # when only tool calls
                    elif should_stream_with_auto_tool_parsing:
                        assert tool_parser is not None
                        delta_message = tool_parser.extract_tool_calls_streaming(
                            previous_text=previous_text,
                            current_text=current_text,
                            delta_text=delta_text,
                            previous_token_ids=previous_token_ids,
                            current_token_ids=current_token_ids,
                            delta_token_ids=output.token_ids,
                            request=request,
                        )

                    # when only reasoning
                    elif reasoning_enabled:
                        delta_message = reasoning_parser.extract_reasoning_content_streaming(
                            previous_text,
                            current_text,
                            delta_text,
                            previous_token_ids,
                            current_token_ids,
                            output.token_ids,
                        )
                        if delta_message is not None and delta_message.reasoning_content:
                            reasoning_full_text[i] += delta_message.reasoning_content

                    # handle streaming just a content delta
                    else:
                        delta_message = DeltaMessage(content=delta_text)

                    # update the previous values for the next iteration
                    if should_stream_with_auto_tool_parsing or reasoning_enabled:
                        assert previous_texts is not None
                        assert all_previous_token_ids is not None
                        previous_texts[i] = current_text
                        all_previous_token_ids[i] = current_token_ids
                    else:
                        # Update for comprehensive logging even in simple case
                        assert previous_texts is not None
                        previous_texts[i] += delta_text

                    # set the previous values for the next iteration
                    previous_num_tokens[i] += len(output.token_ids)

                    if delta_message is None:
                        # Handle streaming of content-only delta messages
                        # Following OpenAI's convention: when the delta contains no content and only includes
                        # a finish reason, return an empty delta object that serializes to {"delta": {}}
                        if output.finish_reason is not None:
                            delta_message = DeltaMessage()
                        # if the message delta is None (e.g. because it was a
                        # "control token" for tool calls or the parser otherwise
                        # wasn't ready to send a token, then
                        #   get the next token without streaming a chunk
                        else:
                            continue

                    if output.finish_reason is None:
                        # Send token-by-token response for each request.n
                        choice_data = ChatCompletionResponseStreamChoice(
                            index=i, delta=delta_message, logprobs=logprobs, finish_reason=None
                        )

                    # if the model is finished generating
                    else:
                        # check to make sure we haven't "forgotten" to stream
                        #   any tokens that were generated but previously
                        #   matched by partial json parsing
                        # only happens if we are NOT using guided decoding
                        auto_tools_called = False
                        if tool_parser:
                            auto_tools_called = len(tool_parser.prev_tool_call_arr) > 0
                            index = (
                                len(tool_parser.prev_tool_call_arr) - 1 if auto_tools_called else 0
                            )
                        else:
                            index = 0

                        if (
                            self._should_check_for_unstreamed_tool_arg_tokens(delta_message, output)
                            and tool_parser
                        ):
                            latest_delta_len = 0
                            if (
                                isinstance(delta_message.tool_calls[0].function, DeltaFunctionCall)
                            ) and isinstance(delta_message.tool_calls[0].function.arguments, str):
                                latest_delta_len = len(
                                    delta_message.tool_calls[0].function.arguments
                                )

                            # get the expected call based on partial JSON
                            # parsing which "autocompletes" the JSON
                            expected_call = json.dumps(
                                tool_parser.prev_tool_call_arr[index].get("arguments", {}),
                                ensure_ascii=False,
                            )

                            # get what we've streamed so far for arguments
                            # for the current tool
                            actual_call = tool_parser.streamed_args_for_tool[index]
                            if latest_delta_len > 0:
                                actual_call = actual_call[:-latest_delta_len]

                            # check to see if there's anything left to stream
                            remaining_call = expected_call.replace(actual_call, "", 1)
                            # set that as a delta message
                            delta_message = DeltaMessage(
                                tool_calls=[
                                    DeltaToolCall(
                                        index=index,
                                        function=DeltaFunctionCall(arguments=remaining_call),
                                    )
                                ]
                            )

                        is_finish_reason_tool_calls = auto_tools_called or (
                            is_tool_choice_required and output.finish_reason == "stop"
                        )

                        # Send the finish response for each request.n only once
                        choice_data = ChatCompletionResponseStreamChoice(
                            index=i,
                            delta=delta_message,
                            logprobs=logprobs,
                            finish_reason=(
                                "tool_calls"
                                if is_finish_reason_tool_calls
                                else output.finish_reason
                            ),
                        )

                        finish_reason_sent[i] = True
                        if reasoning_full_text[i]:
                            len_completion_tokens_reasoning = len(
                                self.tokenizer.encode(
                                    reasoning_full_text[i], add_special_tokens=False
                                )
                            )
                            usage_completion_tokens_reasoning += len_completion_tokens_reasoning
                            metrics.increment_generation_tokens(len_completion_tokens_reasoning)

                    chunk = ChatCompletionStreamResponse(
                        id=request_id,
                        object=chunk_object_type,
                        created=created_time,
                        choices=[choice_data],
                        model=self.model_name,
                    )

                    data = chunk.model_dump_json(exclude_unset=True)
                    # TODO(elpis): Consider abort.
                    if choice_data.finish_reason not in ["length"]:
                        metrics.token_generation_time.append(time.monotonic())
                    yield f"data: {data}\n\n"

        except ValueError as e:
            # TODO(vllm): Use a vllm-specific Validation Error
            data = self.create_streaming_error_response(str(e))
            metrics.request_success = False
            yield f"data: {data}\n\n"
        except Exception as e:
            logger.error("Error in chat completion stream: %s", e, exc_info=True)
            data = self.create_streaming_error_response(
                "internal server error",
                err_type="InternalServerError",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            metrics.request_success = False
            yield f"data: {data}\n\n"

        if request.stream_options and request.stream_options.include_usage:
            # Send the final usage message after all response.n are finished
            usage = UsageInfo(
                prompt_tokens=usage_prompt_tokens,
                completion_tokens=usage_completion_tokens,
                total_tokens=usage_prompt_tokens + usage_completion_tokens,
                completion_tokens_details=CompletionTokenUsageInfo(
                    accepted_prediction_tokens=0,
                    audio_tokens=0,
                    reasoning_tokens=usage_completion_tokens_reasoning,
                    rejected_prediction_tokens=0,
                ),
            )
            chunk = ChatCompletionStreamResponse(
                id=request_id,
                object="chat.completion.chunk",
                created=created_time,
                choices=[],
                model=self.model_name,
                usage=usage,
            )
            data = chunk.model_dump_json(exclude_unset=True)
            yield f"data: {data}\n\n"

        metrics.request_completed = time.monotonic()

        # Send the final done message after all response.n are finished
        yield "data: [DONE]\n\n"

    def extract_tool_call_required_streaming(
        self,
        previous_text: str,
        current_text: Optional[str],
        delta_text: str,
        function_name_returned: bool,
    ) -> tuple[Optional[DeltaMessage], bool]:
        if current_text is None or current_text == "":
            # if the current text is empty, we cannot parse it
            return None, function_name_returned
        try:
            obj = partial_json_parser.loads(current_text)
        except partial_json_parser.core.exceptions.MalformedJSON:
            logger.debug('not enough tokens to parse into JSON yet')
            obj = None

        # check if the current text is a valid array
        # containing a partial tool calling object
        # if not repeat
        if obj is None or not isinstance(obj, list) or not len(obj) > 0:
            function_name_returned = False
            delta_message = None
        else:
            _, finishes_previous_tool = OpenAIServingChat._filter_delta_text(
                delta_text, previous_text
            )
            # take the last tool call from the generated list
            current_tool_call = obj[-1]

            # once parameters have been generated the name is complete as well
            if not finishes_previous_tool and (
                "name" not in current_tool_call or "parameters" not in current_tool_call
            ):
                function_name_returned = False
                delta_message = None
            else:
                if not function_name_returned:
                    # get partly generated arguments from the latest tool call
                    param_match = re.search(r'.*"parameters":\s*(.*)', current_text)
                    arguments = param_match.group(1) if param_match else ""
                    arguments, _ = OpenAIServingChat._filter_delta_text(arguments, previous_text)

                    # if this iteration finishes a previous tool call but a
                    # new incomplete tool is already generated, take the
                    # previous from the list
                    if finishes_previous_tool and "parameters" not in current_tool_call:
                        current_tool_call = obj[-2]

                    function_name_returned = True
                    delta_message = DeltaMessage(
                        tool_calls=[
                            DeltaToolCall(
                                id=random_tool_call_id(),
                                function=DeltaFunctionCall(
                                    name=current_tool_call["name"], arguments=arguments
                                ),
                                index=len(obj) - 1,
                                type="function",
                            )
                        ]
                    )

                else:
                    delta_text, _ = OpenAIServingChat._filter_delta_text(delta_text, previous_text)

                    if delta_text != "":
                        delta_message = DeltaMessage(
                            tool_calls=[
                                DeltaToolCall(
                                    function=DeltaFunctionCall(
                                        # OpenAI API returns None
                                        # instead of name every time
                                        name=None,
                                        arguments=delta_text,
                                    ),
                                    index=len(obj) - 1,
                                )
                            ]
                        )
                    else:
                        delta_message = None

        return delta_message, function_name_returned

    @staticmethod
    def _filter_delta_text(delta_text: str, previous_text: str) -> tuple[str, bool]:
        # remove last '},' of the tool definition stemming from the
        # "name"/"parameters" outer object or closing ']' of the tool list
        # count occurrences of opening and closing curly braces and
        # once level 0 is reached stop outputting text
        # if 0 is reached while parsing the delta_text we know the current
        # tool will finish in this current iteration
        bracket_level = OpenAIServingChat._bracket_level(previous_text)
        updated_delta, passed_zero = "", False
        for c in delta_text:
            if c == '{':
                bracket_level += 1
                passed_zero = bracket_level == 0
            elif c == '}':
                bracket_level -= 1
                passed_zero = bracket_level == 0

            if bracket_level != 0:
                updated_delta += c
            else:
                # if a comma is reached at level 0 we can stop
                if c == ',':
                    break
        return updated_delta, passed_zero

    @staticmethod
    def _bracket_level(s: str, opening='{', closing='}') -> int:
        """
        Calculate the current level of nested brackets in a given string.
        """
        level = 0
        for char in s:
            if char == opening:
                level += 1
            elif char == closing:
                level -= 1
        return level

    async def chat_completion_full_generator(
        self,
        request: ChatCompletionRequest,
        result_generator: AsyncIterator[RequestOutput],
        request_id: str,
        metrics: RequestMetrics,
    ) -> Union[ErrorResponse, ChatCompletionResponse]:
        metrics.set_running()
        previous_token_generation_time = time.monotonic()
        created_time = int(previous_token_generation_time)
        role = self.get_chat_request_role(request)

        choices: List[ChatCompletionResponseChoice] = []

        result = None
        async for result in result_generator:
            # only get the last `result`
            continue
        if result is None:
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response("No result from model")

        len_prompt_tokens = len(result.prompt_token_ids)
        usage_prompt_tokens = len_prompt_tokens
        metrics.increment_prompt_tokens(len_prompt_tokens)
        usage_completion_tokens = 0
        usage_completion_tokens_reasoning = 0

        reasoning_enabled = self.reasoning_parser is not None
        auto_tools_enabled = bool(self.enable_auto_tools and self.tool_parser)
        is_named_tool_call = isinstance(request.tool_choice, ChatCompletionNamedToolChoiceParam)
        is_tool_choice_required = request.tool_choice == "required"
        is_tool_choice_auto = request.tool_choice in ["auto", None]

        for output in result.outputs:
            if request.logprobs and request.top_logprobs is not None:
                assert output.logprobs is not None, "Did not output logprobs"
                return_as_token_id = (
                    request.return_tokens_as_token_ids is not None
                    and request.return_tokens_as_token_ids
                )
                for token_id_to_logprob in output.logprobs:
                    for token_id, logprob in token_id_to_logprob.items():
                        logprob.decoded_token = self._get_decoded_token(
                            logprob, token_id, self.tokenizer, return_as_token_id=return_as_token_id
                        )
                logprobs = self._create_chat_logprobs(
                    token_ids=output.token_ids,
                    top_logprobs=output.logprobs,
                    tokenizer=self.tokenizer,
                    num_output_top_logprobs=request.top_logprobs,
                    return_as_token_id=request.return_tokens_as_token_ids,
                )
            else:
                logprobs = None

            len_completion_tokens = len(output.token_ids)
            usage_completion_tokens += len_completion_tokens
            metrics.increment_generation_tokens(len_completion_tokens)

            if reasoning_enabled:
                try:
                    reasoning_parser = self.reasoning_parser(self.tokenizer)  # type: ignore
                except RuntimeError as e:
                    logger.exception("Error in reasoning parser creation.")
                    return self.create_error_response(str(e))

                reasoning_content, content = reasoning_parser.extract_reasoning_content(
                    output.text, request=request
                )
                if reasoning_content:
                    len_completion_tokens_reasoning = len(
                        self.tokenizer.encode(reasoning_content, add_special_tokens=False)
                    )
                    usage_completion_tokens_reasoning += len_completion_tokens_reasoning
                    metrics.increment_generation_tokens(len_completion_tokens_reasoning)
                    message = ChatMessage(
                        role=role, content=content, reasoning_content=reasoning_content
                    )
                else:
                    message = ChatMessage(role=role, content=output.text)
            else:
                reasoning_content, content = None, output.text

            auto_tools_called = False
            # if auto tools are not enabled, and a named tool choice using
            #   outlines is not being used
            if not auto_tools_enabled and not is_named_tool_call and not is_tool_choice_required:
                message = ChatMessage(
                    role=role, reasoning_content=reasoning_content, content=content
                )

            # if the request uses tools and specified a tool choice
            elif is_named_tool_call:
                message = ChatMessage(
                    role=role,
                    reasoning_content=reasoning_content,
                    content="",
                    tool_calls=[
                        ToolCall(
                            function=FunctionCall(
                                name=request.tool_choice.function.name,  # type: ignore
                                arguments=content or "",
                            )
                        )
                    ],
                )

            # if the request requires tool choice
            elif is_tool_choice_required:
                # TODO: handle metrics for request failure
                assert content is not None
                tool_calls = TypeAdapter(list[FunctionDefinition]).validate_json(content)

                message = ChatMessage(
                    role=role,
                    content="",
                    reasoning_content=reasoning_content,
                    tool_calls=[
                        ToolCall(
                            function=FunctionCall(
                                name=tool_call.name,
                                arguments=json.dumps(tool_call.parameters, ensure_ascii=False),
                            )
                        )
                        for tool_call in tool_calls
                    ],
                )

            # if the request doesn't use tool choice
            # OR specifies to not use a tool
            elif not request.tool_choice or request.tool_choice == "none":
                message = ChatMessage(
                    role=role, reasoning_content=reasoning_content, content=content
                )

            # handle when there are tools and tool choice is auto
            elif is_tool_choice_auto and auto_tools_enabled and request.tools:
                try:
                    tool_parser = self.tool_parser(self.tokenizer)
                except RuntimeError as e:
                    logger.exception("Error in tool parser creation.")
                    metrics.request_success = False
                    metrics.request_completed = time.monotonic()
                    return self.create_error_response(str(e))

                tool_call_info = tool_parser.extract_tool_calls(content or "", request=request)
                # In the OpenAI API the finish_reason is "tools_called"
                # if the tool choice is auto and the model produced a tool
                # call. The same is not true for named function calls
                auto_tools_called = tool_call_info.tools_called
                if auto_tools_called:
                    message = ChatMessage(
                        role=role,
                        reasoning_content=reasoning_content,
                        content=tool_call_info.content,
                        tool_calls=tool_call_info.tool_calls,
                    )
                else:
                    # FOR NOW make it a chat message; we will have to detect
                    # the type to make it later.
                    ret_content = content

                    # try to use content return from tool parser first,
                    # tool parser may do some modify for the content.
                    if tool_call_info.content and len(tool_call_info.content) > 0:
                        ret_content = tool_call_info.content

                    message = ChatMessage(
                        role=role, reasoning_content=reasoning_content, content=ret_content
                    )

            else:
                logger.error(
                    "Error in chat_completion_full_generator - cannot determine "
                    "if tools should be extracted. Returning a standard chat "
                    "completion. Perhaps --enable-auto-tool-choice is not set?"
                )
                message = ChatMessage(
                    role=role, reasoning_content=reasoning_content, content=content
                )

            is_finish_reason_tool_calls = auto_tools_called or (
                is_tool_choice_required and output.finish_reason == "stop"
            )
            choice_data = ChatCompletionResponseChoice(
                index=output.index,
                message=message,
                logprobs=logprobs,
                finish_reason=(
                    "tool_calls"
                    if is_finish_reason_tool_calls
                    else (output.finish_reason or "stop")
                ),
            )
            choices.append(choice_data)

        usage = UsageInfo(
            prompt_tokens=usage_prompt_tokens,
            completion_tokens=usage_completion_tokens,
            total_tokens=usage_prompt_tokens + usage_completion_tokens,
            completion_tokens_details=CompletionTokenUsageInfo(
                accepted_prediction_tokens=0,
                audio_tokens=0,
                reasoning_tokens=usage_completion_tokens_reasoning,
                rejected_prediction_tokens=0,
            ),
        )
        response = ChatCompletionResponse(
            id=request_id,
            created=created_time,
            model=self.model_name,
            choices=choices,
            usage=usage,
            # https://community.openai.com/t/logprob-of-the-prompt/2795/3
            # https://github.com/vllm-project/vllm/pull/7453
            prompt_logprobs=None,
        )

        metrics.request_completed = time.monotonic()

        return response

    def get_chat_request_role(self, request: ChatCompletionRequest) -> str:
        if request.add_generation_prompt:
            return self.response_role
        else:
            return request.messages[-1]["role"]

    # Based on https://github.com/vllm-project/vllm/blob/v0.8.3/vllm/entrypoints/openai/serving_chat.py#L1100-L1115.
    def _get_top_logprobs(
        self,
        logprobs: dict[int, Logprob],
        top_logprobs: Optional[int],
        tokenizer: AnyTokenizer,
        should_return_as_token_id: bool,
    ) -> list[ChatCompletionLogProb]:
        return [
            ChatCompletionLogProb(
                token=(
                    token := self._get_decoded_token(
                        p[1], p[0], tokenizer, return_as_token_id=should_return_as_token_id
                    )
                ),
                logprob=max(p[1].logprob, -9999.0),
                bytes=list(token.encode("utf-8", errors="replace")),
            )
            for i, p in enumerate(logprobs.items())
            if top_logprobs and i < top_logprobs
        ]

    # Based on https://github.com/vllm-project/vllm/blob/v0.8.3/vllm/entrypoints/openai/serving_chat.py#L1117-L1162.
    def _create_chat_logprobs(
        self,
        token_ids: Sequence[int],
        top_logprobs: Sequence[Optional[dict[int, Logprob]]],
        tokenizer: AnyTokenizer,
        num_output_top_logprobs: Optional[int] = None,
        return_as_token_id: Optional[bool] = None,
    ) -> ChatCompletionLogProbs:
        """Create OpenAI-style logprobs."""
        logprobs_content: list[ChatCompletionLogProbsContent] = []

        if return_as_token_id is None:
            return_as_token_id = self.return_tokens_as_token_ids
        for i, token_id in enumerate(token_ids):
            step_top_logprobs = top_logprobs[i]
            if step_top_logprobs is None:
                token = f"token_id:{token_id}" if return_as_token_id else tokenizer.decode(token_id)

                logprobs_content.append(
                    ChatCompletionLogProbsContent(
                        token=token,
                        bytes=list(token.encode("utf-8", errors="replace")),
                    )
                )
            else:
                step_token = step_top_logprobs[token_id]
                step_decoded = step_token.decoded_token

                logprobs_content.append(
                    ChatCompletionLogProbsContent(
                        token=self._get_decoded_token(
                            step_token, token_id, tokenizer, return_as_token_id
                        ),
                        logprob=max(step_token.logprob, -9999.0),
                        bytes=(
                            None
                            if step_decoded is None
                            else list(step_decoded.encode("utf-8", errors="replace"))
                        ),
                        top_logprobs=self._get_top_logprobs(
                            step_top_logprobs,
                            num_output_top_logprobs,
                            tokenizer,
                            return_as_token_id,
                        ),
                    )
                )
        return ChatCompletionLogProbs(content=logprobs_content)

    def _should_check_for_unstreamed_tool_arg_tokens(
        self,
        delta_message: Optional[DeltaMessage],
        output: CompletionOutput,
    ) -> bool:
        """
        Check to see if we should check for unstreamed tool arguments tokens.
        This is only applicable when auto tool parsing is enabled, the delta
        is a tool call with arguments.
        """

        # yapf: disable
        return bool(
            # if there is a delta message that includes tool calls which
            # include a function that has arguments
            output.finish_reason is not None
            and self.enable_auto_tools
            and self.tool_parser
            and delta_message
            and delta_message.tool_calls
            and delta_message.tool_calls[0]
            and delta_message.tool_calls[0].function
            and delta_message.tool_calls[0].function.arguments is not None
        )

    async def _abort_request(self, request_id: str) -> None:
        await self.async_llm_engine.abort(request_id)
