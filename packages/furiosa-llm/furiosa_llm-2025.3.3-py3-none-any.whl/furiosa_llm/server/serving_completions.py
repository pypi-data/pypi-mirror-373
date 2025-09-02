import asyncio
from http import HTTPStatus
from logging import Logger
import time
from typing import AsyncGenerator, AsyncIterator, Dict, List, Optional, Sequence, Tuple, Union

from fastapi import Request

from furiosa_llm.api import LLM, RequestOutput, SamplingParams
from furiosa_llm.llm_engine import AsyncLLMEngine, TokensPrompt
from furiosa_llm.outputs import Logprob, RequestOutputKind
from furiosa_llm.server.metrics import RequestMetrics
from furiosa_llm.server.parse import parse_and_batch_prompt  # type: ignore
from furiosa_llm.server.protocol import (
    CompletionLogProbs,
    CompletionRequest,
    CompletionResponse,
    CompletionResponseChoice,
    CompletionResponseStreamChoice,
    CompletionStreamResponse,
    ErrorResponse,
    UsageInfo,
)
from furiosa_llm.server.serving_base import OpenAIServing
from furiosa_llm.server.utils import (
    AnyTokenizer,
    handle_disconnect,
    merge_async_iterators,
    random_uuid,
)

logger = Logger(__name__)


class OpenAIServingCompletion(OpenAIServing):
    def __init__(
        self,
        llm: LLM,
        *,
        return_tokens_as_token_ids: bool = False,
    ):
        self.async_llm_engine: AsyncLLMEngine = AsyncLLMEngine.from_llm(llm)
        self.tokenizer: AnyTokenizer = llm.tokenizer
        self.model_name = llm.model_metadata.pretrained_id
        self.return_tokens_as_token_ids = return_tokens_as_token_ids

    async def create_completion(
        self,
        request: CompletionRequest,
        raw_request: Request,
        metrics: RequestMetrics,
    ) -> Union[AsyncGenerator[str, None], CompletionResponse, ErrorResponse]:
        """Completion API similar to OpenAI's API.

        See https://platform.openai.com/docs/api-reference/completions/create
        for the API specification. This API mimics the OpenAI Completion API.

        NOTE: Currently we do not support the following feature:
            - suffix (the language models we currently support do not support
            suffix)
        """
        request_id = f"cmpl-{random_uuid()}"
        created_time = int(time.time())

        try:
            assert request.max_tokens is not None
            sampling_params = request.to_sampling_params()
            metrics.max_tokens_request = sampling_params.max_tokens
        except ValueError as e:
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))

        stream = (
            request.stream
            and (request.best_of is None or request.n == request.best_of)
            and not request.use_beam_search
        )

        parsed_prompts = parse_and_batch_prompt(request.prompt)
        tokens_prompts: List[TokensPrompt] = []
        # When we pass text as an input to AsyncLLMEngine, it encodes it with fixed `add_special_tokens=False`.
        # This is because the chat API, which handles the majority of use cases, passes text with the bos token already prepended due to chat templates.
        # So we need to encode the prompt text here with `add_special_tokens=True` before passing it to the AsyncLLMEngine.
        try:
            for prompt in parsed_prompts:
                if prompt["is_tokens"]:
                    tokens_prompts.append(TokensPrompt(prompt_token_ids=prompt["content"]))
                else:
                    encoded = self.tokenizer.encode(
                        prompt["content"], padding=False, add_special_tokens=True
                    )
                    tokens_prompts.append(TokensPrompt(prompt_token_ids=encoded))

            sampling_params.output_kind = (
                RequestOutputKind.DELTA if stream else RequestOutputKind.FINAL
            )
            # XXX: AsyncLLMEngine does not accept multiple prompts at once,
            # and at the same time does not accept duplicate request ids.
            # So we need to generate multiple requests with -i suffix.
            request_ids = [f"{request_id}-{i}" for i in range(len(tokens_prompts))]
            result_generator: List[AsyncGenerator[RequestOutput, None]] = []
            for i, prompt in enumerate(tokens_prompts):
                sampling_params_cloned = sampling_params.clone()
                sampling_params_cloned.verify_and_finalize_max_tokens(
                    input_prompt_len=len(prompt["prompt_token_ids"]),
                    model_max_prompt_len=self.async_llm_engine.prompt_max_seq_len,
                    model_max_context_len=self.async_llm_engine.max_seq_len_to_capture,
                )
                result_generator.append(
                    self.async_llm_engine.generate(prompt, sampling_params_cloned, request_ids[i])
                )

            merged_generator = merge_async_iterators(*result_generator)
        except ValueError as e:
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))
        except Exception as e:
            logger.error("Error in chat completion: %s", e, exc_info=True)
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response("internal server error")

        asyncio.create_task(
            handle_disconnect(raw_request, lambda: self._abort_request(request_ids))
        )

        if stream:
            return self.completion_stream_generator(
                request,
                merged_generator,
                request_id,
                created_time,
                sampling_params,
                metrics,
            )

        try:
            response = await self.completion_full_generator(
                request,
                merged_generator,
                request_id,
                created_time,
                metrics,
            )
            return response
        except ValueError as e:
            metrics.request_completed = time.monotonic()
            metrics.request_success = False
            return self.create_error_response(str(e))

    async def completion_stream_generator(
        self,
        request: CompletionRequest,
        result_generator: AsyncIterator[Tuple[int, RequestOutput]],
        request_id: str,
        created_time: int,
        sampling_params: SamplingParams,
        metrics: RequestMetrics,
    ) -> AsyncGenerator[str, None]:
        prompt_tokens_idx_set = set()
        usage_prompt_tokens = 0
        usage_completion_tokens = 0
        try:
            async for prompt_idx, output in result_generator:
                if not metrics.is_running():
                    metrics.set_running()
                if prompt_idx not in prompt_tokens_idx_set:
                    prompt_tokens_idx_set.add(prompt_idx)
                    len_prompt_tokens = len(output.prompt_token_ids)
                    usage_prompt_tokens += len_prompt_tokens
                    metrics.increment_prompt_tokens(len_prompt_tokens)
                for o in output.outputs:
                    len_completion_tokens = len(o.token_ids)
                    usage_completion_tokens += len_completion_tokens
                    metrics.increment_generation_tokens(len_completion_tokens)
                    if o.text == "" and o.finish_reason is None:
                        # EOS case, don't return empty text
                        continue
                    if request.logprobs is not None:
                        assert o.logprobs is not None, "Did not output logprobs"
                        logprobs = self._create_completion_logprobs(
                            token_ids=o.token_ids,
                            top_logprobs=o.logprobs,
                            num_output_top_logprobs=request.logprobs,
                            tokenizer=self.tokenizer,
                            return_as_token_id=request.return_tokens_as_token_ids,
                        )
                    else:
                        logprobs = None
                    chunk = CompletionStreamResponse(
                        id=request_id,
                        created=created_time,
                        model=self.model_name,
                        choices=[
                            CompletionResponseStreamChoice(
                                index=prompt_idx * sampling_params.n + o.index,
                                text=o.text,
                                logprobs=logprobs,
                                finish_reason=o.finish_reason,
                            )
                        ],
                    )
                    response_json = chunk.model_dump_json(exclude_unset=False)
                    # TODO(elpis): Consider abort.
                    if o.finish_reason not in ["length"]:
                        metrics.token_generation_time.append(time.monotonic())
                    yield f"data: {response_json}\n\n"

            # TODO: support echo

        except ValueError as e:
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
            usage = UsageInfo(
                prompt_tokens=usage_prompt_tokens,
                completion_tokens=usage_completion_tokens,
                total_tokens=usage_prompt_tokens + usage_completion_tokens,
            )
            chunk = CompletionStreamResponse(
                id=request_id,
                created=created_time,
                model=self.model_name,
                choices=[],
                usage=usage,
            )
            data = chunk.model_dump_json(exclude_unset=True)
            yield f"data: {data}\n\n"

        metrics.request_completed = time.monotonic()
        yield "data: [DONE]\n\n"

    async def completion_full_generator(
        self,
        request: CompletionRequest,
        result_generator: AsyncIterator[Tuple[int, RequestOutput]],
        request_id: str,
        created_time: int,
        metrics: RequestMetrics,
    ) -> CompletionResponse:
        metrics.set_running()
        last_outputs_only: Dict[int, RequestOutput] = {}
        async for prompt_idx, output in result_generator:
            last_outputs_only[prompt_idx] = output

        request_outputs = [last_outputs_only[i] for i in sorted(last_outputs_only.keys())]
        return self.request_outputs_to_completion_response(
            request_outputs, request, request_id, created_time, metrics
        )

    def request_outputs_to_completion_response(
        self,
        request_outputs: List[RequestOutput],
        request: CompletionRequest,
        request_id: str,
        created_time: int,
        metrics: RequestMetrics,
    ) -> CompletionResponse:
        choices: List[CompletionResponseChoice] = []
        usage_prompt_tokens = 0
        usage_completion_tokens = 0

        for request_output in request_outputs:
            prompt_token_ids = request_output.prompt_token_ids

            for output in request_output.outputs:
                # TODO: support echo
                token_ids = output.token_ids
                out_logprobs = output.logprobs
                output_text = output.text
                if request.logprobs is not None:
                    assert out_logprobs is not None, "Did not output logprobs"
                    logprobs = self._create_completion_logprobs(
                        token_ids=token_ids,
                        top_logprobs=out_logprobs,
                        tokenizer=self.tokenizer,
                        num_output_top_logprobs=request.logprobs,
                        return_as_token_id=request.return_tokens_as_token_ids,
                    )
                else:
                    logprobs = None
                choice_data = CompletionResponseChoice(
                    index=len(choices),
                    text=output_text,
                    logprobs=logprobs,
                    finish_reason=output.finish_reason,
                )
                choices.append(choice_data)

            len_prompt_tokens = len(prompt_token_ids)
            usage_prompt_tokens += len_prompt_tokens
            metrics.increment_prompt_tokens(len_prompt_tokens)
            len_completion_tokens = sum(len(output.token_ids) for output in request_output.outputs)
            usage_completion_tokens += len_completion_tokens
            metrics.increment_generation_tokens(len_completion_tokens)

        usage = UsageInfo(
            prompt_tokens=usage_prompt_tokens,
            completion_tokens=usage_completion_tokens,
            total_tokens=usage_prompt_tokens + usage_completion_tokens,
        )

        metrics.request_completed = time.monotonic()

        return CompletionResponse(
            id=request_id,
            created=created_time,
            model=self.model_name,
            choices=choices,
            usage=usage,
        )

    # Based on https://github.com/vllm-project/vllm/blob/v0.8.3/vllm/entrypoints/openai/serving_completion.py#L487-L557.
    def _create_completion_logprobs(
        self,
        token_ids: Sequence[int],
        top_logprobs: Sequence[Optional[dict[int, Logprob]]],
        num_output_top_logprobs: int,
        tokenizer: AnyTokenizer,
        initial_text_offset: int = 0,
        return_as_token_id: Optional[bool] = None,
    ) -> CompletionLogProbs:
        """Create logprobs for OpenAI Completion API."""
        out_text_offset: list[int] = []
        out_token_logprobs: list[Optional[float]] = []
        out_tokens: list[str] = []
        out_top_logprobs: list[Optional[dict[str, float]]] = []

        last_token_len = 0

        if return_as_token_id is None:
            return_as_token_id = self.return_tokens_as_token_ids
        for i, token_id in enumerate(token_ids):
            step_top_logprobs = top_logprobs[i]
            if step_top_logprobs is None:
                token = f"token_id:{token_id}" if return_as_token_id else tokenizer.decode(token_id)

                out_tokens.append(token)
                out_token_logprobs.append(None)
                out_top_logprobs.append(None)
            else:
                step_token = step_top_logprobs[token_id]

                token = self._get_decoded_token(
                    step_token, token_id, tokenizer, return_as_token_id=return_as_token_id
                )
                token_logprob = max(step_token.logprob, -9999.0)

                out_tokens.append(token)
                out_token_logprobs.append(token_logprob)

                out_top_logprobs.append(
                    {
                        self._get_decoded_token(
                            top_lp[1],
                            top_lp[0],
                            tokenizer,
                            return_as_token_id=return_as_token_id,
                        ): max(top_lp[1].logprob, -9999.0)
                        for i, top_lp in enumerate(step_top_logprobs.items())
                        if num_output_top_logprobs >= i
                    }
                )

            if len(out_text_offset) == 0:
                out_text_offset.append(initial_text_offset)
            else:
                out_text_offset.append(out_text_offset[-1] + last_token_len)
            last_token_len = len(token)

        return CompletionLogProbs(
            text_offset=out_text_offset,
            token_logprobs=out_token_logprobs,
            tokens=out_tokens,
            top_logprobs=out_top_logprobs,
        )

    async def _abort_request(self, request_ids: List[str]) -> None:
        for request_id in request_ids:
            await self.async_llm_engine.abort(request_id)
