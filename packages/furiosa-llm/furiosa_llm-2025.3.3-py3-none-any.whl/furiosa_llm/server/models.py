from argparse import Namespace
from dataclasses import fields
import logging
import os
from typing import List, Optional, Tuple

from furiosa_llm.api import LLM, LLMBackend, SchedulerConfig
from furiosa_llm.utils import get_logger_with_tz

logger = get_logger_with_tz(logging.getLogger(__name__))


def parse_device_mesh(device_mesh: str) -> List[List[List[str]]]:
    pp_groups = [piece.strip() for piece in device_mesh.split("||") if piece.strip()]
    return [
        list(list(tp_group.strip().split(",")) for tp_group in pp_group.split("|"))
        for pp_group in pp_groups
    ]


def load_llm_from_args(args: Namespace) -> LLM:
    """
    Returns LLM object and an identifier for representing the model.
    The identifier will be:
      - pretrained_id if args.model is a pretrained model id.
      - artifact_id if args.model is an artifact path.
    """
    model: str = args.model
    tp: Optional[int] = args.tensor_parallel_size
    pp: Optional[int] = args.pipeline_parallel_size
    dp: Optional[int] = args.data_parallel_size
    devices = args.devices

    if args.device_mesh:
        device_mesh = parse_device_mesh(args.device_mesh)
    else:
        device_mesh = None

    speculative_model = args.speculative_model
    num_speculative_tokens = args.num_speculative_tokens
    draft_tp: Optional[int] = args.speculative_draft_tensor_parallel_size
    draft_pp: Optional[int] = args.speculative_draft_pipeline_parallel_size
    draft_dp: Optional[int] = args.speculative_draft_data_parallel_size

    prefill_buckets = parse_bucket_args(args.prefill_buckets) if args.prefill_buckets else None
    decode_buckets = parse_bucket_args(args.decode_buckets) if args.decode_buckets else None

    if tp or draft_tp:
        logging.warning(
            "Currently, loading artifacts is only supported. "
            "--tensor-parallel-size or --speculative-draft-tensor-parallel-size will be ignored when loading artifacts."
        )

    if (num_speculative_tokens or speculative_model) and not (
        num_speculative_tokens and speculative_model
    ):
        raise ValueError(
            "To use speculative decoding, both --num-speculative-tokens and --speculative-model should be given."
        )

    # Create LLM for speculative model if given.
    if speculative_model:
        assert num_speculative_tokens

        # FIXME(ssh): Remove this constraint after adjusting the LLM to provide a model parallelization interface for the original and speculative model separately.
        if draft_dp != dp:
            raise ValueError(
                "Different value for --data-parallel-size and --speculative-draft-pipeline-parallel-size is not allowed now."
            )

        use_speculative_model_artifact_load_path = os.path.isdir(
            speculative_model
        ) and os.path.exists(os.path.join(speculative_model, "artifact.json"))

        # TODO: Support artifact loading both from path and from HF hub.
        # Then, support bucket filters (e.g. prefill_buckets, max_model_len).
        if use_speculative_model_artifact_load_path:
            logger.info(f"Loading Speculative model LLM from artifact: {speculative_model}")
            if args.speculative_draft_tensor_parallel_size:
                logger.warning(
                    "When loading Speculative model LLM from artifact, given -tp value will be ignored."
                )
            speculative_model = LLM.load_artifact(
                speculative_model,
                data_parallel_size=draft_dp,
                pipeline_parallel_size=draft_pp,
                devices=devices,
            )
        else:
            speculative_model = LLM(
                speculative_model,
                tensor_parallel_size=draft_tp or 4,
                pipeline_parallel_size=draft_pp or 1,
                data_parallel_size=draft_dp,
                devices=devices,
            )

    if model == "furiosa-ai/fake-llm":
        from transformers import AutoTokenizer

        from tests.utils import FakeLLM

        return FakeLLM(AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer"))

    logger.info(f"Loading LLM from artifact: {model}")
    if args.tensor_parallel_size:
        logger.warning("When loading LLM from artifact, given -tp value will be ignored.")

    scheduler_config = SchedulerConfig()
    for scheduler_config_attr in fields(SchedulerConfig):
        if (v := getattr(args, scheduler_config_attr.name, None)) is not None:
            setattr(scheduler_config, scheduler_config_attr.name, v)

    if args.use_mock_backend:
        backend = LLMBackend.MOCK_BACKEND_V2
    else:
        backend = LLMBackend.FURIOSA_RT_V2

    return LLM.load_artifact(
        model,
        revision=args.revision,
        devices=devices,
        data_parallel_size=dp,
        pipeline_parallel_size=pp,
        device_mesh=device_mesh,
        scheduler_config=scheduler_config,
        prefill_buckets=prefill_buckets,
        decode_buckets=decode_buckets,
        max_prompt_len=args.max_prompt_len,
        max_model_len=args.max_model_len,
        max_batch_size=args.max_batch_size,
        min_batch_size=args.min_batch_size,
        backend=backend,
        # TODO: support speculative_model, num_speculative_tokens
    )


def parse_bucket_args(bucket_args: List[str]) -> List[Tuple[int, int]]:
    try:
        return [tuple(map(int, b.split(",", 1))) for b in bucket_args]  # type: ignore
    except ValueError:
        raise ValueError(
            "Invalid bucket format. Buckets should be in the format of 'batch_size,sequence_length', space-separated."
        )
