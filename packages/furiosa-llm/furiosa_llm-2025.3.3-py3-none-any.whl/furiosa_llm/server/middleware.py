import datetime
import json
import logging
from logging import Formatter
import sys

from starlette.middleware.base import BaseHTTPMiddleware


class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        json_record = {}
        json_record["timestamp"] = (
            datetime.datetime.fromtimestamp(record.created)
            .astimezone()
            .isoformat("T", "milliseconds")
        )
        json_record["message"] = record.getMessage()
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json.dumps(json_record)


json_logger = logging.getLogger("serve")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(JsonFormatter())
json_logger.handlers = [handler]
json_logger.setLevel(logging.DEBUG)
json_logger.propagate = False


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        remote_addr = f"{request.client.host}:{request.client.port}" if request.client else ""
        body = await request.body()
        req_time = datetime.datetime.now().astimezone()
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            body_json = json.dumps(body.decode("utf-8"))

        response = await call_next(request)
        resp_time = datetime.datetime.now().astimezone()
        json_logger.info(
            "request",
            extra={
                "req": {
                    "timestamp": req_time.isoformat("T", "milliseconds"),
                    "method": request.method,
                    "url": str(request.url),
                    "remote_addr": remote_addr,
                    "payload": body_json,
                },
                "res": {
                    "timestamp": resp_time.isoformat("T", "milliseconds"),
                    "status_code": response.status_code,
                },
            },
        )
        return response
