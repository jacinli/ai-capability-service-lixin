"""Bearer Token 鉴权。"""

import uuid

from fastapi import Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.llm import resolve_model_name
from app.models.schemas import ErrorDetail, ErrorResponse, MetaBlock

PUBLIC_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}
http_bearer = HTTPBearer(auto_error=False)


def is_public_path(path: str) -> bool:
    """判断路径是否跳过鉴权。"""

    return path in PUBLIC_PATHS or path.startswith("/docs/")


def is_authorized(request: Request) -> bool:
    """校验 Bearer Token。"""

    auth_header = request.headers.get("Authorization", "")
    expected = settings.api_bearer_token.strip()
    if not expected:
        return True
    return auth_header == f"Bearer {expected}"


def unauthorized_response(path: str) -> JSONResponse:
    """返回统一未授权响应。"""

    meta = MetaBlock(
        request_id=str(uuid.uuid4()),
        capability=path,
        model=resolve_model_name(),
        elapsed_ms=0,
    )
    body = ErrorResponse(
        error=ErrorDetail(code="UNAUTHORIZED", message="缺少有效的 Bearer Token。"),
        meta=meta,
    )
    return JSONResponse(status_code=401, content=body.model_dump())


async def document_bearer_scheme(
    _: HTTPAuthorizationCredentials | None = Security(http_bearer),
) -> None:
    """仅用于在 OpenAPI 中声明 Bearer 认证。"""
