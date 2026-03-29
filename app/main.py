"""FastAPI 应用入口。"""

import json
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import app.capabilities.sentiment_analysis  # noqa: F401
import app.capabilities.text_summary  # noqa: F401
from app.config import settings
from app.llm import resolve_model_name
from app.models.schemas import ErrorDetail, ErrorResponse, MetaBlock
from app.routers.chat_stream import router as chat_stream_router
from app.routers.capabilities import router as capabilities_router
from app.security import is_authorized, is_public_path, unauthorized_response


class JsonFormatter(logging.Formatter):
    """输出统一 JSON 日志。"""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        try:
            parsed_message = json.loads(message)
        except json.JSONDecodeError:
            parsed_message = message
        payload = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": parsed_message,
        }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """初始化日志格式与级别。"""

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


configure_logging()
app = FastAPI(title="AI 能力统一调用服务", version="1.0.0")
app.include_router(capabilities_router)
app.include_router(chat_stream_router)
logger = logging.getLogger(__name__)


def _error_response(request_id: str, capability: str, code: str, message: str) -> JSONResponse:
    """构建统一错误响应。"""

    meta = MetaBlock(
        request_id=request_id,
        capability=capability,
        model=resolve_model_name(),
        elapsed_ms=0,
    )
    body = ErrorResponse(error=ErrorDetail(code=code, message=message), meta=meta)
    return JSONResponse(status_code=500 if code == "INTERNAL_ERROR" else 422, content=body.model_dump())


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """对公开路径之外的请求执行 Bearer Token 鉴权。"""

    if is_public_path(request.url.path) or is_authorized(request):
        return await call_next(request)
    return unauthorized_response(request.url.path)


@app.get("/health")
async def health() -> dict[str, str]:
    """健康检查接口。"""

    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """将 422 校验错误包装成统一响应。"""

    request_id = str(uuid.uuid4())
    message = "请求体校验失败。"
    details = {"errors": exc.errors()}
    meta = MetaBlock(
        request_id=request_id,
        capability="unknown",
        model=resolve_model_name(),
        elapsed_ms=0,
    )
    body = ErrorResponse(
        error=ErrorDetail(code="VALIDATION_ERROR", message=message, details=details),
        meta=meta,
    )
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获异常并返回统一响应。"""

    logger.exception("全局异常: %s", exc)
    request_id = str(uuid.uuid4())
    capability = request.url.path
    return _error_response(request_id, capability, "INTERNAL_ERROR", "服务器内部错误。")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
