"""流式对话路由。"""

import json
import logging
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.capabilities.chat_stream import chat_stream_service
from app.capabilities.text_summary import ModelError
from app.llm import resolve_model_name
from app.models.schemas import ChatStreamRequest
from app.security import document_bearer_scheme

router = APIRouter(
    prefix="/v1/capabilities",
    tags=["capabilities"],
    dependencies=[Depends(document_bearer_scheme)],
)
logger = logging.getLogger(__name__)


def _sse(event: str, data: dict) -> str:
    """将字典格式化为 SSE 文本。"""

    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def stream_chat(req: ChatStreamRequest) -> StreamingResponse:
    """以 SSE 方式返回流式对话结果。"""

    start = time.monotonic()
    model = resolve_model_name(req.model)

    async def event_stream() -> AsyncIterator[str]:
        base_meta = {
            "request_id": req.request_id,
            "capability": chat_stream_service.capability,
            "model": model,
        }
        yield _sse("meta", base_meta)
        try:
            async for delta in chat_stream_service.stream(req.messages, model):
                yield _sse("chunk", {"delta": delta})
        except ValueError as exc:
            logger.info(json.dumps({**base_meta, "ok": False, "code": "INPUT_ERROR"}, ensure_ascii=False))
            yield _sse("error", {"code": "INPUT_ERROR", "message": str(exc), **base_meta})
            return
        except ModelError as exc:
            logger.info(json.dumps({**base_meta, "ok": False, "code": "MODEL_ERROR"}, ensure_ascii=False))
            yield _sse("error", {"code": "MODEL_ERROR", "message": str(exc), **base_meta})
            return
        except Exception as exc:
            logger.exception("流式对话未处理异常: %s", exc)
            logger.info(json.dumps({**base_meta, "ok": False, "code": "INTERNAL_ERROR"}, ensure_ascii=False))
            yield _sse("error", {"code": "INTERNAL_ERROR", "message": "服务器内部错误。", **base_meta})
            return
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info(json.dumps({**base_meta, "elapsed_ms": elapsed_ms, "ok": True}, ensure_ascii=False))
        yield _sse("done", {**base_meta, "elapsed_ms": elapsed_ms})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
