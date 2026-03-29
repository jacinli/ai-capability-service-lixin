"""测试公共夹具。"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def mock_openai_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """强制测试走 mock 分支。"""

    monkeypatch.setattr(settings, "api_bearer_token", "test-token")
    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "openai_api_base", "https://api.openai.com/v1")


@pytest.fixture
async def client():
    """提供异步测试客户端。"""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        c.headers.update({"Authorization": "Bearer test-token"})
        yield c
