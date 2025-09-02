from http import HTTPStatus
import json

from furiosa_llm.server.protocol import ErrorResponse, Logprob
from furiosa_llm.server.utils import AnyTokenizer


class OpenAIServing:
    def create_error_response(
        self,
        message: str,
        err_type: str = "BadRequestError",
        status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
    ) -> ErrorResponse:
        return ErrorResponse(message=message, type=err_type, code=status_code.value)

    def create_streaming_error_response(
        self,
        message: str,
        err_type: str = "BadRequestError",
        status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
    ) -> str:
        json_str = json.dumps(
            {
                "error": self.create_error_response(
                    message=message, err_type=err_type, status_code=status_code
                ).model_dump()
            }
        )
        return json_str

    # Based on https://github.com/vllm-project/vllm/blob/v0.8.3/vllm/entrypoints/openai/serving_engine.py#L518-L528.
    @staticmethod
    def _get_decoded_token(
        logprob: Logprob, token_id: int, tokenizer: AnyTokenizer, return_as_token_id: bool = False
    ) -> str:
        if return_as_token_id:
            return f"token_id:{token_id}"

        if logprob.decoded_token is not None:
            return logprob.decoded_token
        return tokenizer.decode(token_id)
