# Copyright (c) 2023, The vLLM team.
# Copyright (c) 2023, FuriosaAI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from dataclasses import dataclass
from enum import IntEnum
from functools import cached_property
from typing import Optional, Union

from pydantic import BaseModel

from furiosa_llm.outputs import RequestOutputKind

_SAMPLING_EPS = 1e-5


class SamplingType(IntEnum):
    GREEDY = 0
    RANDOM = 1
    BEAM = 2


# https://github.com/vllm-project/vllm/blob/6d8d0a24c02bfd84d46b3016b865a44f048ae84b/vllm/sampling_params.py#L30-L84
@dataclass
class GuidedDecodingParams:
    """One of these fields will be used to build a logit processor."""

    json: Optional[Union[str, dict]] = None
    regex: Optional[str] = None
    choice: Optional[list[str]] = None
    grammar: Optional[str] = None
    json_object: Optional[bool] = None
    """These are other options that can be set"""
    backend: Optional[str] = None
    backend_was_auto: bool = False
    disable_fallback: bool = False
    disable_any_whitespace: bool = False
    disable_additional_properties: bool = False
    whitespace_pattern: Optional[str] = None
    structural_tag: Optional[str] = None

    @staticmethod
    def from_optional(
        json: Optional[Union[dict, BaseModel, str]] = None,
        regex: Optional[str] = None,
        choice: Optional[list[str]] = None,
        grammar: Optional[str] = None,
        json_object: Optional[bool] = None,
        backend: Optional[str] = None,
        whitespace_pattern: Optional[str] = None,
        structural_tag: Optional[str] = None,
    ) -> Optional["GuidedDecodingParams"]:
        if all(arg is None for arg in (json, regex, choice, grammar, json_object, structural_tag)):
            return None
        # Extract json schemas from pydantic models
        if isinstance(json, (BaseModel, type(BaseModel))):
            json = json.model_json_schema()
        return GuidedDecodingParams(
            json=json,
            regex=regex,
            choice=choice,
            grammar=grammar,
            json_object=json_object,
            backend=backend,
            whitespace_pattern=whitespace_pattern,
            structural_tag=structural_tag,
        )

    def __post_init__(self):
        """Validate that some fields are mutually exclusive."""
        guide_count = sum(
            [
                self.json is not None,
                self.regex is not None,
                self.choice is not None,
                self.grammar is not None,
                self.json_object is not None,
            ]
        )
        if guide_count > 1:
            raise ValueError(
                "You can only use one kind of guided decoding but multiple are "
                f"specified: {self.__dict__}"
            )


# https://github.com/vllm-project/vllm/blob/v0.6.2/vllm/sampling_params.py#L46-L127
class SamplingParams:
    """Sampling parameters for text generation.

    Args:
        n: Number of output sequences to return for the given prompt.
        best_of: Number of output sequences that are generated from the prompt.
            From these `best_of` sequences, the top `n` sequences are returned.
            `best_of` must be greater than or equal to `n`. This is treated as
            the beam width when `use_beam_search` is True. By default, `best_of`
            is set to `n`.
        repetition_penalty: Float that penalizes new tokens based on whether
            they appear in the prompt and the generated text so far. Values > 1
            encourage the model to use new tokens, while values < 1 encourage
            the model to repeat tokens.
        temperature: Float that controls the randomness of the sampling. Lower
            values make the model more deterministic, while higher values make
            the model more random. Zero means greedy sampling.
        top_p: Float that controls the cumulative probability of the top tokens
            to consider. Must be in (0, 1]. Set to 1 to consider all tokens.
        top_k: Integer that controls the number of top tokens to consider. Set
            to -1 to consider all tokens.
        min_p: Float that represents the minimum probability for a token to be
            considered, relative to the probability of the most likely token.
            Must be in [0, 1]. Set to 0 to disable this.
        use_beam_search: Whether to use beam search instead of sampling.
        length_penalty: Float that penalizes sequences based on their length.
            Used in beam search.
        early_stopping: Controls the stopping condition for beam search. It
            accepts the following values: `True`, where the generation stops as
            soon as there are `best_of` complete candidates; `False`, where an
            heuristic is applied and the generation stops when is it very
            unlikely to find better candidates; `"never"`, where the beam search
            procedure only stops when there cannot be better candidates
            (canonical beam search algorithm).
        max_tokens: Maximum number of tokens to generate per output sequence.
            If the value is None, it is capped to the maximum sequence length.
        min_tokens: Minimum number of tokens to generate per output sequence
            before EOS or stop_token_ids can be generated
        logprobs: Number of log probabilities to return per output token.
            When set to None, no probability is returned. If set to a non-None
            value, the result includes the log probabilities of the specified
            number of most likely tokens, as well as the chosen tokens.
            Note that the implementation follows the OpenAI API: The API will
            always return the log probability of the sampled token, so there
            may be up to `logprobs+1` elements in the response.
    """

    def __init__(
        self,
        *,
        n: int = 1,
        best_of: Optional[int] = None,
        repetition_penalty: float = 1.0,
        temperature: float = 1.0,
        top_p: float = 1.0,
        top_k: int = -1,
        min_p: float = 0.0,
        use_beam_search: bool = False,
        length_penalty: float = 1.0,
        early_stopping: Union[bool, str] = False,
        max_tokens: Optional[int] = 16,
        min_tokens: int = 0,
        logprobs: Optional[int] = None,
        output_kind: RequestOutputKind = RequestOutputKind.CUMULATIVE,
        guided_decoding: Optional[GuidedDecodingParams] = None,
    ) -> None:
        self.n = n
        self.best_of = best_of if best_of is not None else n
        self.repetition_penalty = repetition_penalty
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.min_p = min_p
        self.use_beam_search = use_beam_search
        self.length_penalty = length_penalty
        self.early_stopping = early_stopping
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        # https://github.com/vllm-project/vllm/blob/v0.6.2/vllm/sampling_params.py#L253
        self.logprobs = 1 if logprobs is True else logprobs
        self.output_kind = output_kind
        self.guided_decoding = guided_decoding

        self._verify_args()
        if self.use_beam_search:
            self._verify_beam_search()
        else:
            self._verify_non_beam_search()
            if self.temperature < _SAMPLING_EPS:
                self._verify_greedy_sampling()

    @classmethod
    def from_optional(
        cls,
        *,
        n: Optional[int] = None,
        best_of: Optional[int] = None,
        repetition_penalty: Optional[float] = 1.0,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        min_p: float = 0.0,
        use_beam_search: Optional[bool] = None,
        length_penalty: Optional[float] = None,
        early_stopping: Optional[Union[bool, str]] = None,
        max_tokens: Optional[int] = None,
        min_tokens: Optional[int] = None,
        logprobs: Optional[int] = None,
        output_kind: Optional[RequestOutputKind] = None,
        guided_decoding: Optional[GuidedDecodingParams] = None,
    ) -> "SamplingParams":
        return cls(
            n=1 if n is None else n,
            best_of=best_of,
            repetition_penalty=1.0 if repetition_penalty is None else repetition_penalty,
            temperature=1.0 if temperature is None else temperature,
            top_p=1.0 if top_p is None else top_p,
            top_k=-1 if top_k is None else top_k,
            min_p=min_p,
            use_beam_search=False if use_beam_search is None else use_beam_search,
            length_penalty=1.0 if length_penalty is None else length_penalty,
            early_stopping=False if early_stopping is None else early_stopping,
            max_tokens=max_tokens,
            min_tokens=0 if min_tokens is None else min_tokens,
            logprobs=logprobs,
            output_kind=RequestOutputKind.CUMULATIVE if output_kind is None else output_kind,
            guided_decoding=guided_decoding,
        )

    def clone(self) -> "SamplingParams":
        return copy.deepcopy(self)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SamplingParams)
            and self.n == other.n
            and self.best_of == other.best_of
            and self.repetition_penalty == other.repetition_penalty
            and self.temperature == other.temperature
            and self.top_p == other.top_p
            and self.top_k == other.top_k
            and self.min_p == other.min_p
            and self.use_beam_search == other.use_beam_search
            and self.length_penalty == other.length_penalty
            and self.early_stopping == other.early_stopping
            and self.max_tokens == other.max_tokens
            and self.min_tokens == other.min_tokens
            and self.logprobs == other.logprobs
            and self.output_kind == other.output_kind
        )

    def _verify_args(self) -> None:
        if self.n < 1:
            raise ValueError(f"n must be at least 1, got {self.n}.")
        if self.n > 1:
            raise ValueError(f"furiosa-llm currently does not support n > 1, got {self.n}.")
        if self.best_of < self.n:
            raise ValueError(
                f"best_of must be greater than or equal to n, "
                f"got n={self.n} and best_of={self.best_of}."
            )
        if not 0.0 < self.repetition_penalty <= 2.0:
            raise ValueError(
                f"repetition_penalty must be in (0, 2], got {self.repetition_penalty}."
            )
        if self.temperature < 0.0:
            raise ValueError(f"temperature must be non-negative, got {self.temperature}.")
        if not 0.0 < self.top_p <= 1.0:
            raise ValueError(f"top_p must be in (0, 1], got {self.top_p}.")
        if self.top_k < -1 or self.top_k == 0:
            raise ValueError(f"top_k must be -1 (disable), or at least 1, " f"got {self.top_k}.")
        if not 0.0 <= self.min_p <= 1.0:
            raise ValueError(f"min_p must be in [0, 1], got {self.min_p}.")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError(f"max_tokens must be at least 1, got {self.max_tokens}.")
        if self.min_tokens < 0:
            raise ValueError(
                f"min_tokens must be greater than or equal to 0, " f"got {self.min_tokens}."
            )
        if self.max_tokens is not None and self.min_tokens > self.max_tokens:
            raise ValueError(
                f"min_tokens must be less than or equal to "
                f"max_tokens={self.max_tokens}, got {self.min_tokens}."
            )
        if self.logprobs is not None and self.logprobs < 0:
            raise ValueError(f"logprobs must be non-negative, got {self.logprobs}.")

    def _verify_beam_search(self) -> None:
        if self.best_of == 1:
            raise ValueError(
                "best_of must be greater than 1 when using beam " f"search. Got {self.best_of}."
            )
        if self.early_stopping not in [True, False, "never"]:
            raise ValueError(
                f"early_stopping must be True, False, or 'never', " f"got {self.early_stopping}."
            )

    def _verify_non_beam_search(self) -> None:
        if self.early_stopping is not False:
            raise ValueError(
                "early_stopping is not effective and must be " "False when not using beam search."
            )
        if self.length_penalty < 1.0 - _SAMPLING_EPS or self.length_penalty > 1.0 + _SAMPLING_EPS:
            raise ValueError(
                "length_penalty is not effective and must be the "
                "default value of 1.0 when not using beam search."
            )

    def _verify_greedy_sampling(self) -> None:
        if self.best_of > 1:
            raise ValueError("best_of must be 1 when using greedy sampling." f"Got {self.best_of}.")

    def verify_and_finalize_max_tokens(
        self, input_prompt_len, model_max_prompt_len, model_max_context_len
    ):
        if input_prompt_len > model_max_prompt_len:
            raise ValueError(
                f"This model's maximum input context length is {model_max_prompt_len} tokens."
                f" However, your messages resulted in {input_prompt_len} tokens."
                " Please reduce the length of the messages."
            )

        if self.max_tokens is None:
            self.max_tokens = model_max_context_len - input_prompt_len
        else:
            requested_context_len = input_prompt_len + self.max_tokens
            if requested_context_len > model_max_context_len:
                raise ValueError(
                    f"This model's maximum context length is {model_max_context_len} tokens."
                    f" However, you requested {requested_context_len} tokens ({input_prompt_len} in the messages, {self.max_tokens} in the completion)."
                    " Please reduce the length of the messages or completion."
                )

    @cached_property
    def sampling_type(self) -> SamplingType:
        if self.use_beam_search:
            return SamplingType.BEAM
        if self.temperature < _SAMPLING_EPS:
            return SamplingType.GREEDY
        return SamplingType.RANDOM

    def __repr__(self) -> str:
        return (
            f"SamplingParams(n={self.n}, "
            f"best_of={self.best_of}, "
            f"repetition_penalty={self.repetition_penalty}, "
            f"temperature={self.temperature}, "
            f"top_p={self.top_p}, "
            f"top_k={self.top_k}, "
            f"min_p={self.min_p}, "
            f"use_beam_search={self.use_beam_search}, "
            f"length_penalty={self.length_penalty}, "
            f"early_stopping={self.early_stopping}, "
            f"max_tokens={self.max_tokens}, "
            f"min_tokens={self.min_tokens}, "
            f"logprobs={self.logprobs}, "
            f"guided_decoding={self.guided_decoding}, "
            f"output_kind={self.output_kind})"
        )
