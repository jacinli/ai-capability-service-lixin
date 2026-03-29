"""能力调用路由。"""

import json
import logging
import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.capabilities.registry import registry
from app.capabilities.text_summary import ModelError
from app.models.schemas import (
    CapabilityRequest,
    ErrorDetail,
    ErrorResponse,
    MetaBlock,
    SuccessResponse,
)

router = APIRouter(prefix="/v1/capabilities", tags=["capabilities"])
logger = logging.getLogger(__name__)


def _meta(request_id: str, capability: str, start: float) -> MetaBlock:
    """构建统一 meta 信息。"""

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return MetaBlock(request_id=request_id, capability=capability, elapsed_ms=elapsed_ms)


def _log(meta: MetaBlock, ok: bool, code: str | None = None) -> None:
    """输出结构化请求日志。"""

    payload = {
        "request_id": meta.request_id,
        "capability": meta.capability,
        "elapsed_ms": meta.elapsed_ms,
        "ok": ok,
    }
    if code:
        payload["code"] = code
    logger.info(json.dumps(payload, ensure_ascii=False))


@router.post("/run", response_model=SuccessResponse | ErrorResponse)
async def run_capability(req: CapabilityRequest) -> JSONResponse:
    """统一调度能力处理器。"""

    start = time.monotonic()
    handler = registry.get(req.capability)
    if handler is None:
        meta = _meta(req.request_id, req.capability, start)
        error = ErrorDetail(
            code="CAPABILITY_NOT_FOUND",
            message=f"未找到能力 `{req.capability}`。",
            details={"available": registry.available()},
        )
        _log(meta, ok=False, code=error.code)
        body = ErrorResponse(error=error, meta=meta).model_dump()
        return JSONResponse(status_code=404, content=body)
    try:
        result = await handler.run(req.input)
    except ValueError as exc:
        meta = _meta(req.request_id, req.capability, start)
        error = ErrorDetail(code="INPUT_ERROR", message=str(exc))
        _log(meta, ok=False, code=error.code)
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error=error, meta=meta).model_dump(),
        )
    except ModelError as exc:
        meta = _meta(req.request_id, req.capability, start)
        error = ErrorDetail(code="MODEL_ERROR", message=str(exc))
        _log(meta, ok=False, code=error.code)
        return JSONResponse(
            status_code=502,
            content=ErrorResponse(error=error, meta=meta).model_dump(),
        )
    except Exception as exc:
        meta = _meta(req.request_id, req.capability, start)
        logger.exception("未处理异常: %s", exc)
        error = ErrorDetail(code="INTERNAL_ERROR", message="服务器内部错误。")
        _log(meta, ok=False, code=error.code)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error=error, meta=meta).model_dump(),
        )
    meta = _meta(req.request_id, req.capability, start)
    _log(meta, ok=True)
    body = SuccessResponse(data={"result": result}, meta=meta).model_dump()
    return JSONResponse(status_code=200, content=body)
