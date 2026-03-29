"""请求与响应模型。"""

from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field


class CapabilityRequest(BaseModel):
    """能力调用请求。"""

    model_config = ConfigDict(extra="forbid")

    capability: str
    input: dict[str, Any]
    model: str | None = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ChatMessage(BaseModel):
    """对话消息。"""

    model_config = ConfigDict(extra="forbid")

    role: str
    content: str


class ChatStreamRequest(BaseModel):
    """流式对话请求。"""

    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage]
    model: str | None = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class MetaBlock(BaseModel):
    """统一元信息。"""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    capability: str
    model: str
    elapsed_ms: int


class SuccessResponse(BaseModel):
    """成功响应。"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = True
    data: dict[str, Any]
    meta: MetaBlock


class ErrorDetail(BaseModel):
    """错误详情。"""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """失败响应。"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = False
    error: ErrorDetail
    meta: MetaBlock
