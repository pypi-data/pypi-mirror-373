# Code obtained from
# https://github.com/vllm-project/vllm/blob/40253bab443ad0cdd22ff33bd8f777d2f289cfc4/vllm/engine/metrics.py

from dataclasses import dataclass, field
from enum import Enum, auto
import logging
import re
import sys
import threading
import time
from typing import Callable, List, Optional

from starlette.routing import Mount

from furiosa.native_runtime import metrics

if sys.version_info >= (3, 10):
    from itertools import pairwise  # noqa
else:

    def pairwise(iterable):  # fmt: skip
        iterator = iter(iterable)
        a = next(iterator, None)

        for b in iterator:
            yield a, b
            a = b


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_BYTES_TO_GIBIBYTES = 1024 * 1024 * 1024


# Code obtained and modified from Prometheus Python client.
# https://github.com/prometheus/client_python/blob/73680284ce63f0bc0f23cfc42af06e74fd7e3ccf/prometheus_client/asgi.py#L8
# TODO(elpis): Add gzip compression.
def _make_prometheus_endpoint() -> Callable:
    async def prometheus_app(scope, receive, send):
        assert scope.get("type") == "http"
        # Bake output
        status = "200 OK"
        headers = [("Content-Type", "text/plain; version=0.0.4; charset=utf-8")]
        output = metrics.get_metrics().to_prometheus().encode("utf8")
        formatted_headers = []
        for header in headers:
            formatted_headers.append(tuple(x.encode("utf8") for x in header))
        # Return output
        payload = await receive()
        if payload.get("type") == "http.request":
            await send(
                {
                    "type": "http.response.start",
                    "status": int(status.split(" ")[0]),
                    "headers": formatted_headers,
                }
            )
            await send({"type": "http.response.body", "body": output})

    return prometheus_app


class _Metrics:
    def __init__(self):
        # First sets of metrics to support.
        metrics.register_up_down_counter(
            name="furiosa_llm_num_requests_running",
            description="Number of requests currently running on RNGD.",
        )
        metrics.register_up_down_counter(
            name="furiosa_llm_num_requests_waiting",
            description="Number of requests waiting to be processed.",
        )
        metrics.register_counter(
            name="furiosa_llm_request_received_total",
            description="Count of requests.",
        )
        metrics.register_counter(
            name="furiosa_llm_request_success_total",
            description="Count of successfully processed requests.",
        )
        metrics.register_counter(
            name="furiosa_llm_request_failure_total",
            description="Count of request process failures.",
        )

        metrics.register_counter(
            name="furiosa_llm_prompt_tokens_total",
            description="Number of prefill tokens processed.",
        )
        metrics.register_counter(
            name="furiosa_llm_generation_tokens_total",
            description="Number of generation tokens processed.",
        )

        metrics.register_histogram(
            name="furiosa_llm_time_to_first_token",
            unit="s",
            description="Histogram of time to first token in seconds.",
            boundaries=[
                0.001,
                0.005,
                0.01,
                0.02,
                0.04,
                0.06,
                0.08,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ],
        )
        metrics.register_histogram(
            name="furiosa_llm_time_per_output_token",
            unit="s",
            description="Histogram of time per output token in seconds.",
            boundaries=[0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 2.5],
        )

        # Request stats
        #   Latency
        request_latency_buckets = [
            0.3,
            0.5,
            0.8,
            1.0,
            1.5,
            2.0,
            2.5,
            5.0,
            10.0,
            15.0,
            20.0,
            30.0,
            40.0,
            50.0,
            60.0,
        ]
        metrics.register_histogram(
            name="furiosa_llm_e2e_request_latency",
            unit="s",
            description="Histogram of end to end request latency in seconds.",
            boundaries=request_latency_buckets,
        )
        #   Metadata
        metrics.register_histogram(
            name="furiosa_llm_request_prompt_tokens",
            description="Number of prefill tokens processed.",
            boundaries=_build_buckets([1, 2, 5], _MAX_MODEL_LEN),
        )
        metrics.register_histogram(
            name="furiosa_llm_request_generation_tokens",
            description="Number of generation tokens processed.",
            boundaries=_build_buckets([1, 2, 5], _MAX_MODEL_LEN),
        )
        metrics.register_histogram(
            name="furiosa_llm_request_params_max_tokens",
            description="Histogram of the max_tokens request parameter.",
            boundaries=_build_buckets([1, 2, 5], _MAX_MODEL_LEN),
        )


_MAX_MODEL_LEN: int
_METRICS: _Metrics
_MODEL: str


def initialize_metrics(model: str, max_model_len: int) -> None:
    global _MAX_MODEL_LEN, _METRICS, _MODEL

    _MAX_MODEL_LEN = max_model_len
    _MODEL = model
    _METRICS = _Metrics()


def get_metrics_mount() -> Mount:
    metrics_route = Mount("/metrics", _make_prometheus_endpoint())
    # Workaround for 307 Redirect for /metrics
    metrics_route.path_regex = re.compile("^/metrics(?P<path>.*)$")
    return metrics_route


# NOTE(elpis): Example vLLM Log format:
# INFO 06-22 08:13:23 [loggers.py:118] Engine 000: Avg prompt throughput: 3155.9 tokens/s, Avg generation throughput: 2673.9 tokens/s, Running: 12 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.8%, Prefix cache hit rate: 60.4%


def _get_counter_data(counter: metrics.Counter) -> float:
    for data in counter.data:
        if data.labels.get("model_name") == _MODEL:
            return data.value
    return 0


@dataclass
class LogMetrics:
    time: float = field(default_factory=time.monotonic)
    prompt_tokens_total: int = 0
    generation_tokens_total: int = 0
    num_requests_running: int = 0
    num_requests_waiting: int = 0
    kv_cache_used: dict[str, float] = field(default_factory=dict)
    kv_cache_total: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        metrics_container = metrics.get_metrics()
        for counter in metrics_container.counters:
            if counter.name == "furiosa_llm_prompt_tokens_total":
                self.prompt_tokens_total = int(_get_counter_data(counter))
            elif counter.name == "furiosa_llm_generation_tokens_total":
                self.generation_tokens_total = int(_get_counter_data(counter))
        for counter in metrics_container.up_down_counters:
            if counter.name == "furiosa_llm_num_requests_running":
                self.num_requests_running = int(_get_counter_data(counter))
            elif counter.name == "furiosa_llm_num_requests_waiting":
                self.num_requests_waiting = int(_get_counter_data(counter))
        for gauge in metrics_container.gauges:
            if gauge.name == "furiosa_llm_kv_cache_used_bytes":
                for data in gauge.data:
                    if (
                        data.labels.get("model_name") == _MODEL
                        and (device_index := data.labels.get("device_index")) is not None
                    ):
                        self.kv_cache_used[device_index] = data.value / _BYTES_TO_GIBIBYTES
            elif gauge.name == "furiosa_llm_kv_cache_total_bytes":
                for data in gauge.data:
                    if (
                        data.labels.get("model_name") == _MODEL
                        and (device_index := data.labels.get("device_index")) is not None
                    ):
                        self.kv_cache_total[device_index] = data.value / _BYTES_TO_GIBIBYTES

    def print_diff_log(self, prev: "LogMetrics"):
        requests_exist: bool = (self.num_requests_waiting + self.num_requests_running) > 0
        tokens_processed: bool = (self.prompt_tokens_total > prev.prompt_tokens_total) or (
            self.generation_tokens_total > prev.generation_tokens_total
        )
        if not (requests_exist or tokens_processed):
            return
        time_diff = self.time - prev.time
        if time_diff > 0:
            prompt_throughput = (self.prompt_tokens_total - prev.prompt_tokens_total) / time_diff
            generation_throughput = (
                self.generation_tokens_total - prev.generation_tokens_total
            ) / time_diff
            requests_running = self.num_requests_running
            requests_waiting = self.num_requests_waiting
            log_string = (
                f"Avg prompt throughput: {prompt_throughput:.1f} tokens/s"
                f", Avg generation throughput: {generation_throughput:.1f} tokens/s"
                f", Running: {requests_running} reqs"
                f", Waiting: {requests_waiting} reqs"
            )
            for device_index in self.kv_cache_used.keys():
                if (kv_cache_used := self.kv_cache_used.get(device_index)) is not None and (
                    kv_cache_total := self.kv_cache_total.get(device_index)
                ) is not None:
                    kv_cache_usage = kv_cache_used * 100.0 / kv_cache_total
                    log_string += f", RNGD KV cache usage (device {device_index}): {kv_cache_usage:.1f}% ({kv_cache_used:.2f} GiB / {kv_cache_total:.2f} GiB)"
            logger.info(log_string)


def install_metrics_logging_thread():
    def log_time_periodically():
        prev = LogMetrics()
        while True:
            cur = LogMetrics()
            cur.print_diff_log(prev)
            prev = cur
            time.sleep(10)

    thread = threading.Thread(target=log_time_periodically, daemon=True)
    thread.start()


def _build_buckets(mantissa_lst: List[int], max_value: int) -> List[int]:
    """
    Builds a list of buckets with increasing powers of 10 multiplied by
    mantissa values until the value exceeds the specified maximum.
    """
    exponent = 0
    buckets: List[int] = []
    mantissa_lst = sorted(mantissa_lst)
    while True:
        for m in mantissa_lst:
            value = m * 10**exponent
            if value <= max_value:
                buckets.append(value)
            else:
                return buckets
        exponent += 1


class RequestStatus(Enum):
    WAITING = auto()
    RUNNING = auto()


@dataclass
class RequestMetrics:
    request_created: float = field(default_factory=time.monotonic)
    token_generation_time: List[float] = field(default_factory=list)
    request_status: RequestStatus = RequestStatus.WAITING
    request_completed: Optional[float] = None
    max_tokens_request: Optional[int] = None
    request_success: bool = True
    prompt_tokens: int = 0
    generation_tokens: int = 0

    def __post_init__(self) -> None:
        metrics.increment_counter("furiosa_llm_request_received_total", 1, model_name=_MODEL)
        metrics.increment_up_down_counter("furiosa_llm_num_requests_waiting", 1, model_name=_MODEL)

    def increment_prompt_tokens(self, num_tokens: int) -> None:
        if num_tokens > 0:
            self.prompt_tokens += num_tokens
            metrics.increment_counter(
                "furiosa_llm_prompt_tokens_total", num_tokens, model_name=_MODEL
            )

    def increment_generation_tokens(self, num_tokens: int) -> None:
        if num_tokens > 0:
            self.generation_tokens += num_tokens
            metrics.increment_counter(
                "furiosa_llm_generation_tokens_total", num_tokens, model_name=_MODEL
            )

    def is_running(self) -> bool:
        return self.request_status == RequestStatus.RUNNING

    def set_running(self) -> None:
        if self.is_running():
            logger.warning("Trying to set status of request that is already running.")
        else:
            self.request_status = RequestStatus.RUNNING
            metrics.decrement_up_down_counter(
                "furiosa_llm_num_requests_waiting", 1, model_name=_MODEL
            )
            metrics.increment_up_down_counter(
                "furiosa_llm_num_requests_running", 1, model_name=_MODEL
            )

    def __del__(self) -> None:
        if self.request_success:
            metrics.increment_counter("furiosa_llm_request_success_total", 1, model_name=_MODEL)
        else:
            metrics.increment_counter("furiosa_llm_request_failure_total", 1, model_name=_MODEL)

        if self.request_status == RequestStatus.WAITING:
            metrics.decrement_up_down_counter(
                "furiosa_llm_num_requests_waiting", 1, model_name=_MODEL
            )
        elif self.request_status == RequestStatus.RUNNING:
            metrics.decrement_up_down_counter(
                "furiosa_llm_num_requests_running", 1, model_name=_MODEL
            )

        if self.request_completed is not None:
            metrics.record_histogram(
                "furiosa_llm_e2e_request_latency",
                self.request_completed - self.request_created,
                model_name=_MODEL,
            )
        if self.max_tokens_request is None:
            metrics.record_histogram(
                "furiosa_llm_request_params_max_tokens",
                _MAX_MODEL_LEN - self.prompt_tokens,
                model_name=_MODEL,
            )
        else:
            metrics.record_histogram(
                "furiosa_llm_request_params_max_tokens",
                self.max_tokens_request,
                model_name=_MODEL,
            )

        if self.token_generation_time:
            metrics.record_histogram(
                "furiosa_llm_time_to_first_token",
                self.token_generation_time[0] - self.request_created,
                model_name=_MODEL,
            )
        for start, end in pairwise(self.token_generation_time):
            metrics.record_histogram(
                "furiosa_llm_time_per_output_token", end - start, model_name=_MODEL
            )

        metrics.record_histogram(
            "furiosa_llm_request_prompt_tokens", self.prompt_tokens, model_name=_MODEL
        )
        metrics.record_histogram(
            "furiosa_llm_request_generation_tokens",
            self.generation_tokens,
            model_name=_MODEL,
        )
