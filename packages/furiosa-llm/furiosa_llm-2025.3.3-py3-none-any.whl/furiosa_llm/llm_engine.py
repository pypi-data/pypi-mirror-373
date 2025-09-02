import argparse
from argparse import ArgumentParser
import asyncio
from dataclasses import dataclass, fields
import os
from pathlib import Path
from typing import AsyncGenerator, Callable, Iterable, List, Optional, Set, Tuple, Union

from transformers import PreTrainedTokenizerBase
from typing_extensions import TypedDict

from furiosa.native_runtime.llm import NativeLLMEngine  # type: ignore
from furiosa_llm.api import (
    CACHE_DIR,
    LLM,
    RequestOutput,
    SamplingParams,
    SchedulerConfig,
    TokenizerModeType,
)
from furiosa_llm.outputs import NativeOutputConverter
from furiosa_llm.server.utils import AnyTokenizer


# adopted from https://github.com/vllm-project/vllm/blob/main/vllm/inputs/data.py
class TextPrompt(TypedDict):
    """Schema for a text prompt."""

    prompt: str
    """The input text to be tokenized before passing to the model."""


class TokensPrompt(TypedDict):
    """Schema for a tokenized prompt."""

    prompt_token_ids: List[int]
    """A list of token IDs to pass to the model."""


SingletonPrompt = Union[str, TextPrompt, TokensPrompt]

# TODO: support ExplicitEncoderDecoderPrompt later
PromptType = Union[SingletonPrompt]


# A shallow version of transformers.tokenization_utils_base.BatchEncoding
@dataclass
class BatchEncoding:
    input_ids: List[int]
    attention_mask: List[int]


@dataclass
class EngineArgs:
    # Currently only artifact path is supported
    model: str
    revision: Optional[str] = None
    pipeline_parallel_size: Optional[int] = None
    data_parallel_size: Optional[int] = None
    tokenizer: Optional[str] = None
    tokenizer_mode: TokenizerModeType = "auto"
    seed: Optional[int] = None
    devices: Optional[str] = None
    cache_dir: os.PathLike = CACHE_DIR

    # scheduler_config
    npu_queue_limit: Optional[int] = None
    max_processing_samples: Optional[int] = None
    spare_blocks_ratio: Optional[float] = None

    @staticmethod
    def add_cli_args(parser: ArgumentParser) -> ArgumentParser:
        """Shared CLI arguments for vLLM engine."""

        # Model arguments
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            help='The Hugging Face model id, or path to Furiosa model artifact. Currently only one model is supported per server.',
        )
        parser.add_argument(
            "--revision",
            type=str,
            default=EngineArgs.revision,
            help="The specific model revision on Hugging Face Hub if the model is given as a Hugging Face model id. It can be a branch name, a tag name, or a commit id."
            " Its default value is main. However, if a given model belongs to the furiosa-ai organization, the model will use the release model tag by default.",
        )
        parser.add_argument(
            '--tokenizer',
            type=str,
            default=EngineArgs.tokenizer,
            help='The name or path of a HuggingFace Transformers tokenizer.',
        )
        parser.add_argument(
            '--tokenizer-mode',
            type=str,
            default=EngineArgs.tokenizer_mode,
            help='The tokenizer mode. "auto" will use the fast tokenizer '
            'if available, and "slow" will always use the slow tokenizer.',
        )
        parser.add_argument(
            '--seed',
            type=int,
            default=EngineArgs.seed,
            help='The seed to initialize the random number generator for sampling.',
        )

        # Furiosa LLM specific arguments
        parser.add_argument(
            '--devices',
            type=str,
            default=EngineArgs.devices,
            help='The devices to run the model. It can be a single device or a comma-separated list of devices. '
            'Each device can be either "npu:X" or "npu:X:Y", where X is a device index and Y is a NPU core range notation '
            '(e.g. "npu:0" for whole npu 0, "npu:0:0" for core 0 of NPU 0, and "npu:0:0-3" for fused core 0-3 of npu 0). '
            'If not given, all available unoccupied devices will be used.',
        )
        parser.add_argument(
            '--pipeline-parallel-size',
            type=int,
            default=EngineArgs.pipeline_parallel_size,
            help='The size of the pipeline parallelism group. '
            'If not given, it will use the default pp value of the artifact.',
        )
        parser.add_argument(
            '--data-parallel-size',
            type=int,
            default=EngineArgs.data_parallel_size,
            help='The size of the data parallelism group. '
            'If not given, it will be inferred from total available PEs and other parallelism degrees.',
        )
        parser.add_argument(
            '--cache-dir',
            type=Path,
            default=EngineArgs.cache_dir,
            help='The cache directory for temporarily generated files for this LLM instance. '
            'When its value is ``None``, caching is disabled. The default is "$HOME/.cache/furiosa/llm".',
        )
        parser.add_argument(
            '--npu-queue-limit',
            type=int,
            default=EngineArgs.npu_queue_limit,
            help='The NPU queue limit of the scheduler config.',
        )
        parser.add_argument(
            '--max-processing-samples',
            type=int,
            default=EngineArgs.max_processing_samples,
            help='The maximum processing samples. Used as an hint for the scheduler.',
        )
        parser.add_argument(
            '--spare-blocks-ratio',
            type=float,
            default=EngineArgs.spare_blocks_ratio,
            help='The spare blocks ratio. Used as an hint for the scheduler.',
        )
        return parser

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace):
        attrs = [attr.name for attr in fields(cls)]
        engine_args = cls(**{attr: getattr(args, attr) for attr in attrs})
        return engine_args


@dataclass
class AsyncEngineArgs(EngineArgs):
    # TODO: add async-specific arguments

    @staticmethod
    def add_cli_args(parser: ArgumentParser) -> ArgumentParser:
        # TODO: add async-specific arguments
        parser = EngineArgs.add_cli_args(parser)
        return parser


# XXX: Since SamplingParams.max_tokens in Rust is not an Option type,
# we must ensure max_tokens is not None when SamplingParams is converted from Python to Rust.
# That's why the validation logic is duplicated here and in `LLM._verify_token_len_and_finalize_max_tokens`.
# Unfortunately there is no way to avoid this duplication while minimizing unnecessary encode/decode operations
# and keeping the Python API compatible with vLLM at the same time.
# The best solution would be to change SamplingParams.max_tokens in Rust to an Option type in the future.
# related PR: https://github.com/furiosa-ai/furiosa-runtime/pull/1260
class LLMEngineBase:
    prompt_max_seq_len: int
    max_seq_len_to_capture: int

    request_ids: Set[str]

    # TODO: Also do __verify_sampling_params_with_generator_config

    def try_add_request_id(self, request_id: str) -> None:
        if request_id in self.request_ids:
            raise ValueError(f"Request ID {request_id} already exist in the engine.")
        if not isinstance(request_id, str):
            raise ValueError(f"Request ID {request_id} must be a string.")
        self.request_ids.add(request_id)

    def try_remove_request_id(self, request_id: str) -> None:
        try:
            self.request_ids.remove(request_id)
        except KeyError:
            pass


class LLMEngine(LLMEngineBase):
    """
    LLMEngine receives requests and generates texts.
    Implements the API interface compatible with vLLM's `LLMEngine`, but this class is based on furiosa-runtime and FuriosaAI NPU.

    The request scheduling approach of this engine is different from that of vLLM's . While vLLM provides
    fine-grained control over decoding via the `step` method, this engine immediately begins
    text generation in the background as soon as a request is submitted via :meth:`add_request`,
    continuing asynchronously until completion. The generated results are placed in a queue that
    clients can retrieve by calling :meth:`step`.

    The Furiosa native engine handles scheduling and batching internally,
    allowing clients to retrieve results via :meth:`step` calls without needing to manage the decoding schedule.
    """

    def __init__(
        self,
        native_engine: NativeLLMEngine,
        tokenizer: AnyTokenizer,
        prompt_max_seq_len: int,
        max_seq_len_to_capture: int,
    ):
        self.native_engine = native_engine
        self.tokenizer = tokenizer
        self.prompt_max_seq_len = prompt_max_seq_len
        self.max_seq_len_to_capture = max_seq_len_to_capture

        self.queue: asyncio.Queue[RequestOutput] = asyncio.Queue()
        self.request_ids = set()

        self.aio_loop = asyncio.new_event_loop()

    @classmethod
    def from_llm(
        cls,
        llm: LLM,
    ) -> "LLMEngine":
        assert (
            llm.max_seq_len_to_capture is not None
        ), "Generative models must have max_seq_len_to_capture set."
        return cls(
            llm.engine,
            llm.tokenizer,
            llm.prompt_max_seq_len,
            llm.max_seq_len_to_capture,
        )

    @classmethod
    def from_engine_args(cls, args: EngineArgs) -> "LLMEngine":
        """
        Creates an LLMEngine from EngineArgs.
        """
        scheduler_config = SchedulerConfig()
        for scheduler_config_attr in fields(SchedulerConfig):
            if (v := getattr(args, scheduler_config_attr.name, None)) is not None:
                setattr(scheduler_config, scheduler_config_attr.name, v)

        llm = LLM.load_artifact(
            model_id_or_path=args.model,
            revision=args.revision,
            pipeline_parallel_size=args.pipeline_parallel_size,
            data_parallel_size=args.data_parallel_size,
            tokenizer=args.tokenizer,
            tokenizer_mode=args.tokenizer_mode,
            seed=args.seed,
            devices=args.devices,
            cache_dir=args.cache_dir,
            scheduler_config=scheduler_config,
        )

        return cls.from_llm(llm)

    def add_request(
        self,
        request_id: str,
        prompt: PromptType,
        sampling_params: SamplingParams,
    ) -> None:
        """
        Adds a new request to the engine.
        The decoding iteration starts immediately after adding the request.

        Args:
            request_id: The unique id of the request.
            prompt: The prompt to the LLM.
            sampling_params: The sampling parameters of the request.
        """
        self.try_add_request_id(request_id)

        batch_encoding, prompt_getter = preprocess_prompt(prompt, self.tokenizer)
        prompt_token_ids = batch_encoding.input_ids
        sampling_params.verify_and_finalize_max_tokens(
            len(prompt_token_ids), self.prompt_max_seq_len, self.max_seq_len_to_capture
        )

        n = sampling_params.n if sampling_params is not None else 1

        # TODO: call prompt_getter after calling `self.native_engine.stream_generate` to reduce latency
        prompt_str = prompt_getter()
        converter = NativeOutputConverter(
            self.tokenizer, n, sampling_params.output_kind, request_id, prompt_str, prompt_token_ids
        )
        self.aio_loop.create_task(
            self._process_request(request_id, converter, batch_encoding, sampling_params)
        )

    def abort_request(self, request_id: Union[str, Iterable[str]]):
        """
        Aborts request(s) with the given ID.
        """
        if isinstance(request_id, str):
            request_id = [request_id]
        for rid in request_id:
            self.native_engine.abort_request(rid)
            self.try_remove_request_id(rid)

    async def _process_request(
        self,
        request_id: str,
        converter: NativeOutputConverter,
        batch_encoding: BatchEncoding,
        sampling_params: Optional[SamplingParams] = None,
    ) -> None:
        native_output_generator = self.native_engine.stream_generate(
            batch_encoding, sampling_params, request_id
        )
        async for request_output in converter.convert_stream(native_output_generator):
            await self.queue.put(request_output)

    def has_unfinished_requests(self) -> bool:
        """
        Returns True if there are unfinished requests.
        """
        return len(self.request_ids) > 0

    def step(self) -> List[RequestOutput]:
        """
        Returns newly generated results of one decoding iteration from the queue.
        """
        # ensure at least one output is returned
        req_output = self.aio_loop.run_until_complete(self.queue.get())

        # get as many outputs as possible
        req_outputs = [req_output]
        while True:
            try:
                req_outputs.append(self.queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        # ignore aborted request
        req_outputs = [r for r in req_outputs if r.request_id in self.request_ids]

        # remove finished requests
        for req_output in req_outputs:
            if req_output.finished:
                self.try_remove_request_id(req_output.request_id)

        return req_outputs


class AsyncLLMEngine(LLMEngineBase):
    """
    AsyncLLMEngine receives requests and generates texts asynchronously.
    Implements the API interface compatible with vLLM's `AsyncLLMEngine`, but this class is based on furiosa-runtime and FuriosaAI NPU.
    """

    def __init__(
        self,
        native_engine: NativeLLMEngine,
        tokenizer: AnyTokenizer,
        prompt_max_seq_len: int,
        max_seq_len_to_capture: int,
    ):
        self.native_engine = native_engine
        self.tokenizer = tokenizer
        self.prompt_max_seq_len = prompt_max_seq_len
        self.max_seq_len_to_capture = max_seq_len_to_capture

        self.request_ids = set()

    @classmethod
    def from_llm(
        cls,
        llm: LLM,
    ) -> "AsyncLLMEngine":
        assert (
            llm.max_seq_len_to_capture is not None
        ), "Generative models must have max_seq_len_to_capture set."
        return cls(
            llm.engine,
            llm.tokenizer,
            llm.prompt_max_seq_len,
            llm.max_seq_len_to_capture,
        )

    @classmethod
    def from_engine_args(cls, args: AsyncEngineArgs) -> "AsyncLLMEngine":
        """
        Creates an AsyncLLMEngine from AsyncEngineArgs.
        """
        scheduler_config = SchedulerConfig()
        for scheduler_config_attr in fields(SchedulerConfig):
            if (v := getattr(args, scheduler_config_attr.name, None)) is not None:
                setattr(scheduler_config, scheduler_config_attr.name, v)

        llm = LLM.load_artifact(
            model_id_or_path=args.model,
            pipeline_parallel_size=args.pipeline_parallel_size,
            data_parallel_size=args.data_parallel_size,
            tokenizer=args.tokenizer,
            tokenizer_mode=args.tokenizer_mode,
            seed=args.seed,
            devices=args.devices,
            cache_dir=args.cache_dir,
            scheduler_config=scheduler_config,
        )

        return cls.from_llm(llm)

    async def generate(
        self,
        prompt: PromptType,
        sampling_params: SamplingParams,
        request_id: str,
    ) -> AsyncGenerator[RequestOutput, None]:
        """
        Generates text completions for a given prompt.

        Args:
            prompt: The prompt to the LLM. See :class:`~PromptType`
                for more details about the format of each input.
            sampling_params: The sampling parameters of the request.
            request_id: The unique id of the request.
        """
        self.try_add_request_id(request_id)

        # TODO: add a path to send add_special_tokens to preprocess_prompt
        batch_encoding, prompt_getter = preprocess_prompt(prompt, self.tokenizer)
        prompt_token_ids = batch_encoding.input_ids
        sampling_params.verify_and_finalize_max_tokens(
            len(prompt_token_ids), self.prompt_max_seq_len, self.max_seq_len_to_capture
        )

        native_output_generator = self.native_engine.stream_generate(
            batch_encoding, sampling_params, request_id
        )

        prompt_str = prompt_getter()
        converter = NativeOutputConverter(
            self.tokenizer,
            sampling_params.n,
            sampling_params.output_kind,
            request_id,
            prompt_str,
            prompt_token_ids,
        )

        async for request_output in converter.convert_stream(native_output_generator):
            yield request_output

        self.try_remove_request_id(request_id)

    async def abort(self, request_id: str) -> None:
        """
        Aborts a request with the given ID.
        """
        self.native_engine.abort_request(request_id)
        self.try_remove_request_id(request_id)

    # TODO
    # async def engine_step(self): ...


def preprocess_prompt(
    prompt: PromptType,
    tokenizer: PreTrainedTokenizerBase,
) -> Tuple[BatchEncoding, Callable[[], str]]:
    """
    Returns a tuple containing `(BatchEncoding, prompt string getter)`.

    The reason we want prompt as string is for `RequestOutput`, not as an input to the model.
    Therefore to reduce latency it is recommended to call `prompt_getter` after calling `self.native_engine.stream_generate`.

    **Note:** `add_special_tokens` is currently set to `False` by default.

    This is because the majority of use cases rely on chat templates, which already include special tokens.
    If special tokens need to be added manually, the caller must handle encoding themselves.

    While this approach may seem unconventional, it is necessary for compatibility with vLLM,
    as there is no straightforward way to pass `add_special_tokens` in this context.
    """
    if isinstance(prompt, str):
        prompt_str = prompt
        input_ids = tokenizer.encode(prompt_str, padding=False, add_special_tokens=False)
        return (
            BatchEncoding(input_ids=input_ids, attention_mask=[1] * len(input_ids)),
            lambda: prompt_str,
        )
    if isinstance(prompt, dict):
        if "prompt" in prompt:
            prompt_str = prompt["prompt"]  # type: ignore
            input_ids = tokenizer.encode(prompt_str, padding=False, add_special_tokens=False)
            return (
                BatchEncoding(input_ids=input_ids, attention_mask=[1] * len(input_ids)),
                lambda: prompt_str,
            )
        elif "prompt_token_ids" in prompt:
            input_ids = prompt["prompt_token_ids"]
            return BatchEncoding(
                input_ids=input_ids, attention_mask=[1] * len(input_ids)
            ), lambda: tokenizer.decode(input_ids, skip_special_tokens=True)

    raise ValueError(f"Unsupported prompt type: {type(prompt)}")
