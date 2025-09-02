import argparse
import json

from furiosa_llm.server.app import run_server
from furiosa_llm.server.reasoning_parsers import ReasoningParserManager
from furiosa_llm.server.tool_parsers import ToolParserManager


def add_serve_args(serve_parser):
    serve_parser.add_argument(
        "model",
        type=str,
        help="The Hugging Face model id, or path to Furiosa model artifact. Currently only one model is supported per server.",
    )
    serve_parser.add_argument(
        "--revision",
        type=str,
        help="The specific model revision on Hugging Face Hub if the model is given as a Hugging Face model id. It can be a branch name, a tag name, or a commit id."
        " Its default value is main. However, if a given model belongs to the furiosa-ai organization, the model will use the release model tag by default.",
    )
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: %(default)s)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: %(default)s)",
    )
    serve_parser.add_argument(
        "--allowed-origins",
        type=json.loads,
        default=["*"],
        help='Allowed origins in json list (default: ["*"])',
    )
    serve_parser.add_argument(
        "--disable-log-stats", action="store_true", help="Disable logging statistics."
    )
    serve_parser.add_argument(
        "--enable-metrics",
        action="store_true",
        help="Enable Prometheus metrics.",
    )
    serve_parser.add_argument(
        "--enable-payload-logging",
        default=False,
        action="store_true",
        help="Enabling HTTP POST request payload logging. This logging can expose sensitive data,"
        " increasing the risk of data breaches and regulatory non-compliance (e.g., GDPR)."
        " It may also lead to excessive storage usage and potential security vulnerabilities if the logs are not properly protected."
        " If you do not fully understand the risks associated with this option, do not enable it.",
    )
    serve_parser.add_argument(
        "--chat-template",
        type=str,
        help="If given, the default chat template will be overridden with the given file. (Default: use chat template from tokenizer)",
    )
    serve_parser.add_argument(
        "--enable-auto-tool-choice",
        action="store_true",
        default=False,
        help="Enable auto tool choice for supported models. Use --tool-call-parser to specify which parser to use",
    )
    valid_tool_parsers = ToolParserManager.tool_parsers.keys()
    serve_parser.add_argument(
        "--tool-call-parser",
        type=str,
        metavar="{" + ",".join(valid_tool_parsers) + "}",
        default=None,
        help="Select the tool call parser depending on the model that you're using."
        " This is used to parse the model-generated tool call into OpenAI API "
        "format. Required for --enable-auto-tool-choice.",
    )
    valid_reasoning_parsers = ReasoningParserManager.reasoning_parsers.keys()
    serve_parser.add_argument(
        "--reasoning-parser",
        type=str,
        metavar="{" + ",".join(valid_reasoning_parsers) + "}",
        default=None,
        help="Select the reasoning parser depending on the model that you're "
        "using. This is used to parse the reasoning content into OpenAI "
        "API format. Required for reasoning models.",
    )
    serve_parser.add_argument(
        "--response-role",
        type=str,
        default="assistant",
        help="Response role for /v1/chat/completions API (default: %(default)s)",
    )
    serve_parser.add_argument(
        "-tp",
        "--tensor-parallel-size",
        type=int,
        help="Number of tensor parallel replicas. (default: 4)",
    )
    serve_parser.add_argument(
        "-pp",
        "--pipeline-parallel-size",
        type=int,
        help="Number of pipeline stages. (default: 1)",
    )
    serve_parser.add_argument(
        "-dp",
        "--data-parallel-size",
        type=int,
        help="Data parallelism size. If not given, it will be inferred from total available PEs and other parallelism degrees.",
    )
    serve_parser.add_argument(
        "-pb",
        "--prefill-buckets",
        type=str,
        nargs="+",
        help="List of prefill buckets to use. If not given, the prefill buckets specified in the artifact will be used by default.",
    )
    serve_parser.add_argument(
        "-db",
        "--decode-buckets",
        type=str,
        nargs="+",
        help="List of decode buckets to use. If not given, the decode buckets specified in the artifact will be used by default.",
    )
    serve_parser.add_argument(
        "--max-prompt-len",
        type=int,
        default=None,
        help="Maximum prompt length to capture for the model. If given, prefill buckets with longer attention size than this value will be ignored.",
    )
    serve_parser.add_argument(
        "--max-model-len",
        type=int,
        default=None,
        help="Maximum supported sequence length of the model. If given, decode buckets with longer attention size than this value will be ignored.",
    )
    serve_parser.add_argument(
        "--max-batch-size",
        type=int,
        default=None,
        help="Maximum batch size to process in a single npu request. If given, buckets with larger batch size than this value will be ignored.",
    )
    serve_parser.add_argument(
        "--min-batch-size",
        type=int,
        default=None,
        help="Minimum batch size to process in a single npu request. If given, buckets with smaller batch size than this value will be ignored.",
    )
    serve_parser.add_argument(
        "--devices",
        type=str,
        default=None,
        help="The devices to run the model. It can be a single device or a comma-separated list of devices. "
        'Each device can be either "npu:X" or "npu:X:Y", where X is a device index and Y is a NPU core range notation '
        '(e.g. "npu:0" for whole npu 0, "npu:0:0" for core 0 of NPU 0, and "npu:0:0-3" for fused core 0-3 of npu 0). '
        "If not given, all available unoccupied devices will be used.",
    )
    serve_parser.add_argument(
        "--device-mesh",
        type=str,
        default=None,
        help="3D Matrix of device IDs that defines the model parallelism strategy. In this matrix, three dimensions determine"
        "the grouping of devices for data, pipeline, and tensor parallelism respectively. Groups for each kind of parallelism"
        "(data, pipeline, tensor) are separated by double vertical bar(||), single vertical bar(|), and comma(,) respectively.\n\n"
        "Examples:\n"
        "- DP=3 x PP=2 x TP=4 : npu:0:0-3|npu:1:0-3||npu:0:4-7|npu:1:4-7||npu:2:0-3|npu3:4-7\n"
        "- DP=2 x PP=1 x TP=16 : npu:0,npu:1||npu:2,npu:3\n"
        "- DP=1 x PP=4 x TP=8 : npu:0 | npu:1 | npu:0 | npu:1\n",
    )
    serve_parser.add_argument(
        "--scheduler-kind",
        type=str,
        default=None,
        help="Select named scheduler implementation with specialized strategy when provided. "
        "(default: use default scheduler which handles generic cases well)",
    )
    serve_parser.add_argument(
        "--npu-queue-limit",
        type=int,
        default=None,
        help="If given, override the NPU queue limit of the scheduler config. (default: use value from artifact)",
    )
    serve_parser.add_argument(
        "--max-processing-samples",
        type=int,
        default=None,
        help="If given, override the maximum processing samples of the scheduler config. (default: use value from artifact)",
    )
    serve_parser.add_argument(
        "--spare-blocks-ratio",
        type=float,
        default=0.0,  # LLM-924
        help="The spare blocks ratio of the scheduler config (default: 0.0)."
        " Increasing this value might improve the performance but might lead to OOM.",
    )
    serve_parser.add_argument(
        "--estimation-time-limit-ms",
        type=int,
        default=None,
        help="The estimation time limit in milliseconds of the scheduler config (default: None)."
        " Increasing this value will allow scheduler to calculate better batching strategy at the expense of given computation time",
    )
    serve_parser.add_argument(
        "--enable-prefix-caching",
        dest="enable_prefix_caching",
        action="store_true",
        help="Enable prefix caching",
    )
    serve_parser.add_argument(
        "--no-enable-prefix-caching",
        dest="enable_prefix_caching",
        action="store_false",
        help="Disable prefix caching",
    )
    serve_parser.add_argument(
        "--speculative-model",
        type=str,
        default=None,
        help="The Hugging Face model id, or path to Furiosa model artifact for the speculative model.",
    )
    serve_parser.add_argument(
        "--num-speculative-tokens",
        type=int,
        default=None,
        help="The number of speculative tokens to sample from the draft model in speculative decoding.",
    )
    serve_parser.add_argument(
        "-draft-tp",
        "--speculative-draft-tensor-parallel-size",
        type=int,
        default=None,
        help="Number of tensor parallel replicas for the speculative model. (default: 4)",
    )
    serve_parser.add_argument(
        "-draft-pp",
        "--speculative-draft-pipeline-parallel-size",
        type=int,
        default=None,
        help="Number of pipeline stages for the speculative model. (default: 1)",
    )
    serve_parser.add_argument(
        "-draft-dp",
        "--speculative-draft-data-parallel-size",
        type=int,
        default=None,
        help="Data parallelism size for the speculative model. If not given, it will be inferred from total available PEs and other parallelism degrees.",
    )
    serve_parser.add_argument(
        "--use-mock-backend",
        type=bool,
        default=False,
        help=argparse.SUPPRESS,
    )

    serve_parser.set_defaults(dispatch_function=serve)
    serve_parser.set_defaults(enable_prefix_caching=False)


def serve(args):
    run_server(args)
