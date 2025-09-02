from dataclasses import dataclass
from enum import Enum
import logging
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from transformers import PreTrainedTokenizerBase


@dataclass
class Logprob:
    """Infos for supporting OpenAI compatible logprobs and token ranks.

    Attributes:
        logprob: The logprob of chosen token
        rank: The vocab rank of chosen token (>=1)
        decoded_token: The decoded chosen token index
    """

    logprob: float
    rank: Optional[int] = None
    decoded_token: Optional[str] = None


SampleLogprobs = List[Dict[int, Logprob]]


class CompletionOutput:
    """The output data of one completion output of a request.

    Args:
        index: The index of the output in the request.
        text: The generated output text.
        token_ids: The token IDs of the generated output text.
            Note that it is expected to have EOS token included in the token_ids.
        logprobs: The log probabilities of the top probability words at each
            position if the logprobs are requested.
        finish_reason: The reason why the sequence is finished.
    """

    def __init__(
        self,
        index: int,
        text: str,
        token_ids: List[int],
        logprobs: Optional[SampleLogprobs],
        finish_reason: Optional[str] = None,
    ) -> None:
        self.index = index
        self.text = text
        self.token_ids = token_ids
        self.logprobs = logprobs
        self.finish_reason = finish_reason

    def __repr__(self) -> str:
        return (
            f"CompletionOutput(index={self.index}, "
            f"text={self.text!r}, "
            f"token_ids={self.token_ids}, "
            f"logprobs={self.logprobs}, "
            f"finish_reason={self.finish_reason})"
        )


class RequestOutput:
    def __init__(
        self,
        request_id: str,
        prompt: str,
        prompt_token_ids: List[int],
        outputs: List[CompletionOutput],
        finished: bool,
    ) -> None:
        self.request_id = request_id
        self.prompt = prompt
        self.prompt_token_ids = prompt_token_ids
        self.outputs = outputs
        self.finished = finished

    def __repr__(self) -> str:
        return (
            f"RequestOutput(request_id={self.request_id}, "
            f"prompt={self.prompt!r}, "
            f"prompt_token_ids={self.prompt_token_ids}, "
            f"outputs={self.outputs}, "
            f"finished={self.finished})"
        )


class RequestOutputKind(Enum):
    # Return entire output so far in every RequestOutput
    CUMULATIVE = 0
    # Return only deltas in each RequestOutput
    DELTA = 1
    # Return only final output
    FINAL = 2


class NativeOutputConverter:
    """
    This class has two main functions:
    1. Convert the NativeRequestOutput to RequestOutput, respecting the RequestOutputKind.
    2. For streaming RequestOutput, detokenize incrementally so that
       incomplete tokens (which are represented as replacement character "�") is not returned to the user.
    This class must be initialized per prompt, not per request.

    Args:
        tokenizer: The tokenizer used to tokenize the prompt.
        n: The number of expected outputs. Usually equals to `SamplingParams.n` if not beam search.
        output_kind: Determines how to handle the output. See `RequestOutputKind`.
        request_id: The request ID.
        prompt: The prompt text.
        prompt_token_ids: The prompt token IDs.
    """

    def __init__(
        self,
        tokenizer: PreTrainedTokenizerBase,
        n: int,
        output_kind: RequestOutputKind,
        request_id: str,
        prompt: str,
        prompt_token_ids: List[int],
    ):
        self.n = n
        self.tokenizer = tokenizer
        self.output_kind = output_kind
        self.request_id = request_id
        self.prompt = prompt
        self.prompt_token_ids = prompt_token_ids

    async def convert_stream(
        self, native_output_generator: AsyncGenerator["NativeRequestOutput", None]  # type: ignore # noqa: F821
    ) -> AsyncGenerator[RequestOutput, None]:
        decoders: List[StreamDecoder] = [StreamDecoder(self.tokenizer, True) for _ in range(self.n)]
        completion_outputs: List[CompletionOutput] = [
            CompletionOutput(i, "", [], None, None) for i in range(self.n)
        ]
        logprobs: List[List[Dict[int, Logprob]]] = [[] for _ in range(self.n)]

        if self.output_kind == RequestOutputKind.FINAL:
            async for native_output in native_output_generator:
                for o in native_output.outputs:
                    if o.finish_reason is not None:
                        completion_outputs[o.index].finish_reason = o.finish_reason
                    if o.logprobs is not None:
                        logprobs[o.index].extend(
                            {
                                token_id: Logprob(
                                    logprob.logprob, logprob.rank, logprob.decoded_token
                                )
                                for token_id, logprob in token_id_to_logprob
                            }
                            for token_id_to_logprob in o.logprobs
                        )
                    decoders[o.index].push(o.token_ids)
            for idx, decoder in enumerate(decoders):
                text, token_ids = decoder.flush()
                completion_outputs[idx].text = text
                completion_outputs[idx].token_ids = token_ids
                if logprobs[idx]:
                    completion_outputs[idx].logprobs = logprobs[idx]
            yield RequestOutput(
                request_id=self.request_id,
                prompt=self.prompt,
                prompt_token_ids=self.prompt_token_ids,
                outputs=completion_outputs,
                finished=all(co.finish_reason is not None for co in completion_outputs),
            )

        elif self.output_kind == RequestOutputKind.CUMULATIVE:
            async for native_output in native_output_generator:
                for o in native_output.outputs:
                    if o.finish_reason is not None:
                        completion_outputs[o.index].finish_reason = o.finish_reason
                    if o.logprobs is not None:
                        logprobs[o.index].extend(
                            {
                                token_id: Logprob(
                                    logprob.logprob, logprob.rank, logprob.decoded_token
                                )
                                for token_id, logprob in token_id_to_logprob
                            }
                            for token_id_to_logprob in o.logprobs
                        )
                    maybe_decoded = decoders[o.index].push_decode(o.token_ids)
                    if maybe_decoded is None:
                        continue
                    text, token_ids = maybe_decoded
                    completion_outputs[o.index].text += text
                    completion_outputs[o.index].token_ids.extend(token_ids)
                    if logprobs[o.index]:
                        # fmt: off
                        completion_outputs[o.index].logprobs = \
                            logprobs[o.index][: len(completion_outputs[o.index].token_ids)]
                        # fmt: on
                finished = all(co.finish_reason is not None for co in completion_outputs)
                if not finished:
                    yield RequestOutput(
                        request_id=self.request_id,
                        prompt=self.prompt,
                        prompt_token_ids=self.prompt_token_ids,
                        outputs=completion_outputs,
                        finished=False,
                    )
                else:
                    break
            for idx, decoder in enumerate(decoders):
                if not decoder.has_remaining_tokens():
                    continue
                text, token_ids = decoder.flush()
                completion_outputs[idx].text += text
                completion_outputs[idx].token_ids.extend(token_ids)
                if logprobs[idx]:
                    # fmt: off
                    completion_outputs[idx].logprobs = \
                        logprobs[idx][: len(completion_outputs[idx].token_ids)]
                    # fmt: on
            yield RequestOutput(
                request_id=self.request_id,
                prompt=self.prompt,
                prompt_token_ids=self.prompt_token_ids,
                outputs=completion_outputs,
                finished=True,
            )

        else:
            # RequestOutputKind.DELTA
            # Unlike the above two, we set finished=True per CompletionOutput, not per RequestOutput.
            async for native_output in native_output_generator:
                for o in native_output.outputs:
                    if o.finish_reason is not None:
                        completion_outputs[o.index].finish_reason = o.finish_reason
                    if o.logprobs is not None:
                        logprobs[o.index].extend(
                            {
                                token_id: Logprob(
                                    logprob.logprob, logprob.rank, logprob.decoded_token
                                )
                                for token_id, logprob in token_id_to_logprob
                            }
                            for token_id_to_logprob in o.logprobs
                        )
                    maybe_decoded = decoders[o.index].push_decode(o.token_ids)

                    finished = o.finish_reason is not None
                    new_content_added = maybe_decoded is not None

                    if new_content_added:
                        text, token_ids = maybe_decoded
                        completion_outputs[o.index].text = text
                        completion_outputs[o.index].token_ids = token_ids
                        # fmt: off
                        completion_outputs[o.index].logprobs = \
                            logprobs[o.index][: len(completion_outputs[o.index].token_ids)]
                        logprobs[o.index] = \
                            logprobs[o.index][len(completion_outputs[o.index].token_ids) :]
                        # fmt: on
                        yield RequestOutput(
                            request_id=self.request_id,
                            prompt=self.prompt,
                            prompt_token_ids=self.prompt_token_ids,
                            outputs=[completion_outputs[o.index]],
                            finished=finished,
                        )
                    elif finished:
                        completion_outputs[o.index].text = ""
                        completion_outputs[o.index].token_ids = []
                        completion_outputs[o.index].logprobs = None
                        yield RequestOutput(
                            request_id=self.request_id,
                            prompt=self.prompt,
                            prompt_token_ids=self.prompt_token_ids,
                            outputs=[completion_outputs[o.index]],
                            finished=True,
                        )


class StreamDecoder:
    # Maximum number of tokenizer.decode() calls allowed per completion output.
    # Set to 4 since BPE-based tokenizers typically split natural language words into at most 4 tokens.
    MAX_DECODE_TRAIL = 4

    def __init__(
        self,
        tokenizer: PreTrainedTokenizerBase,
        skip_special_tokens: bool = True,
    ):
        self.tokenizer = tokenizer
        self.skip_special_tokens = skip_special_tokens
        self.token_buffer: List[int] = []

    def push(self, token_ids: List[int]) -> None:
        """
        Push tokens in the buffer without decoding it.
        """
        self.token_buffer.extend(token_ids)

    def push_decode(self, token_ids: List[int]) -> Optional[Tuple[str, List[int]]]:
        """
        Push tokens in the buffer and decode them.
        This function returns the first human-readable text as output while pushing tokens one by one,
        and the leftovers are pushed to the buffer.
        You must decode the leftovers by calling `flush()` at the end in a separate function call.
        """
        if len(token_ids) > self.MAX_DECODE_TRAIL:
            # This scenario is unlikely since for streaming requests because
            # the Generator normally emits single token per CompletionOutput.
            # Multiple tokens returned in a CompletionOutput could negatively impact
            # TPOT and user experience, so logging a warning.
            logging.warning(
                f"Received {len(token_ids)} tokens at once in streaming mode. "
                f"This may degrade TPOT and user experience. "
                f"Keeping only last {self.MAX_DECODE_TRAIL} tokens."
            )
            self.token_buffer.extend(token_ids[: -self.MAX_DECODE_TRAIL])
            token_ids = token_ids[-self.MAX_DECODE_TRAIL :]

        for i, token_id in enumerate(token_ids):
            self.token_buffer.append(token_id)
            decoded_text = self._decode(self.token_buffer)
            if not decoded_text.endswith("�"):
                break
        else:
            # failed to retrieve a human-readable text
            return None

        decoded_token_ids = self.token_buffer[:]
        if i == len(token_ids) - 1:
            self.token_buffer.clear()
        else:
            self.token_buffer = token_ids[i + 1 :]

        return decoded_text, decoded_token_ids

    def flush(self) -> Tuple[str, List[int]]:
        """
        Decode all remaining tokens in the buffer.
        """
        decoded_text = self._decode(self.token_buffer)
        decoded_token_ids = self.token_buffer[:]
        self.token_buffer.clear()
        return decoded_text, decoded_token_ids

    def has_remaining_tokens(self) -> bool:
        return bool(self.token_buffer)

    def _decode(self, token_ids: List[int]) -> str:
        return self.tokenizer.decode(
            token_ids,
            skip_special_tokens=self.skip_special_tokens,
            cleanup_tokenization_spaces=True,
        )
