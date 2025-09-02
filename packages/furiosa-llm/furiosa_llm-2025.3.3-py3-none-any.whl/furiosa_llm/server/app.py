from argparse import Namespace
from contextlib import asynccontextmanager
import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, Response, StreamingResponse
import uvicorn

import furiosa.native_runtime
from furiosa_llm.api import LLM
from furiosa_llm.server.metrics import (
    RequestMetrics,
    get_metrics_mount,
    initialize_metrics,
    install_metrics_logging_thread,
)
from furiosa_llm.server.middleware import RequestLoggerMiddleware
from furiosa_llm.server.models import load_llm_from_args
from furiosa_llm.server.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    ErrorResponse,
    ModelsResponse,
)
from furiosa_llm.server.serving_chat import OpenAIServingChat
from furiosa_llm.server.serving_completions import OpenAIServingCompletion
from furiosa_llm.server.utils import parse_request
from furiosa_llm.version import FURIOSA_LLM_VERSION

router = APIRouter()

llm: LLM
openai_serving_completion: OpenAIServingCompletion
openai_serving_chat: OpenAIServingChat
openai_serving_models_response: ModelsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    install_metrics_logging_thread()
    yield


@router.get("/health")
async def health() -> Response:
    """Health check."""
    if llm.engine.is_alive():
        return Response(status_code=200)
    else:
        return Response(status_code=503)


@router.get("/version")
async def show_version():
    return ORJSONResponse(
        content={
            "version": FURIOSA_LLM_VERSION.version,
            "furiosa-llm": {
                "stage": FURIOSA_LLM_VERSION.stage,
                "version": FURIOSA_LLM_VERSION.version,
                "git_hash": FURIOSA_LLM_VERSION.hash,
            },
            "furiosa-runtime": {
                "version": furiosa.native_runtime.__version__,
                "git_hash": furiosa.native_runtime.__git_short_hash__,
                "build_time": furiosa.native_runtime.__build_timestamp__,
            },
            "npu-ir": {
                "version": furiosa.native_runtime.__ir_version__,
                "git_hash": furiosa.native_runtime.__ir_git_short_hash__,
                "build_time": furiosa.native_runtime.__ir_build_timestamp__,
            },
        }
    )


@router.get("/v1/models")
async def show_available_models(raw_request: Request):
    return ORJSONResponse(content=openai_serving_models_response.model_dump())


@router.get("/v1/models/{model_id:path}")
async def show_model(raw_request: Request, model_id: str):
    for model in openai_serving_models_response.data:
        if model.id == model_id:
            return ORJSONResponse(content=model.model_dump())
    return ORJSONResponse(
        content={
            "error": {
                "message": f"The model '{model_id}' does not exist",
                "type": "invalid_request_error",
                "param": "model",
                "code": "model_not_found",
            }
        },
        status_code=404,
    )


@router.post("/v1/completions")
async def create_completion(raw_request: Request):
    metrics = RequestMetrics()
    request = await parse_request(raw_request, CompletionRequest)
    generator = await openai_serving_completion.create_completion(request, raw_request, metrics)
    if isinstance(generator, ErrorResponse):
        return ORJSONResponse(content=generator.model_dump(), status_code=generator.code)
    elif isinstance(generator, CompletionResponse):
        return ORJSONResponse(content=generator.model_dump())

    return StreamingResponse(content=generator, media_type="text/event-stream")


@router.post("/v1/chat/completions")
async def create_chat_completion(raw_request: Request):
    metrics = RequestMetrics()
    request = await parse_request(raw_request, ChatCompletionRequest)
    generator = await openai_serving_chat.create_chat_completion(request, raw_request, metrics)
    if isinstance(generator, ErrorResponse):
        return ORJSONResponse(content=generator.model_dump(), status_code=generator.code)
    elif isinstance(generator, ChatCompletionResponse):
        return ORJSONResponse(content=generator.model_dump())

    return StreamingResponse(content=generator, media_type="text/event-stream")


def init_app(
    args: Namespace,
) -> FastAPI:
    global llm
    global openai_serving_completion
    global openai_serving_chat
    global openai_serving_models_response

    # NOTE(elpis): Lifespan is usage is not constrained to metrics logging purpose
    # and can be expanded to other use cases in the future.
    metrics_logging_task = None
    if not args.disable_log_stats:
        metrics_logging_task = lifespan
    app = FastAPI(lifespan=metrics_logging_task)
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    llm = load_llm_from_args(args)
    assert llm.is_generative_model

    override_chat_template = None
    if args.chat_template is not None:
        try:
            override_chat_template = open(args.chat_template).read()
        except Exception as e:
            raise ValueError(f"Error in reading chat template file: {e}")
    else:
        try:
            llm.tokenizer.get_chat_template()
        except Exception as e:
            raise ValueError(
                f"Failed to load chat template from tokenizer: {e}. Please specify a chat template using the --chat-template option."
            )
    openai_serving_completion = OpenAIServingCompletion(llm)
    openai_serving_chat = OpenAIServingChat(
        llm,
        args.response_role,
        chat_template=override_chat_template,
        reasoning_parser=args.reasoning_parser,
        enable_auto_tools=args.enable_auto_tool_choice,
        tool_parser=args.tool_call_parser,
    )
    openai_serving_models_response = ModelsResponse.from_llm(llm)

    initialize_metrics(llm.model_metadata.pretrained_id, llm.model_max_seq_len)

    if args.enable_metrics:
        app.routes.append(get_metrics_mount())

    return app


def run_server(args, **uvicorn_kwargs) -> None:
    app = init_app(args)

    if args.enable_payload_logging:
        app.add_middleware(RequestLoggerMiddleware)
        logging.warning(
            "Payload logging is enabled. This might expose sensitive data. If you do not fully understand the risks associated with this option, do not enable it."
        )
        # Disable uvicorn's access log
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["loggers"]["uvicorn.access"]["level"] = logging.CRITICAL + 1
        log_config["loggers"]["uvicorn.access"]["handlers"] = []
        log_config["loggers"]["uvicorn.access"]["propagate"] = False
        uvicorn_kwargs["log_config"] = log_config

    uvicorn.run(app, host=args.host, port=args.port, **uvicorn_kwargs)
