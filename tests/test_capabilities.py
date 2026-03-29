"""接口测试。"""

import json


async def test_health(client) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_text_summary_success(client) -> None:
    response = await client.post("/v1/capabilities/run", json=_summary_payload())
    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is True
    assert isinstance(body["data"]["result"], str) and body["data"]["result"]


async def test_text_summary_empty_text(client) -> None:
    payload = _summary_payload(text="")
    response = await client.post("/v1/capabilities/run", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INPUT_ERROR"


async def test_text_summary_truncates(client) -> None:
    payload = _summary_payload(max_length=20)
    response = await client.post("/v1/capabilities/run", json=payload)
    result = response.json()["data"]["result"]
    assert len(result) < len(payload["input"]["text"])


async def test_sentiment_analysis_positive(client) -> None:
    response = await client.post("/v1/capabilities/run", json=_sentiment_payload("good great amazing best"))
    result = json.loads(response.json()["data"]["result"])
    assert result["label"] == "positive"


async def test_sentiment_analysis_negative(client) -> None:
    response = await client.post("/v1/capabilities/run", json=_sentiment_payload("bad awful worst horrible"))
    result = json.loads(response.json()["data"]["result"])
    assert result["label"] == "negative"


async def test_sentiment_analysis_neutral(client) -> None:
    response = await client.post("/v1/capabilities/run", json=_sentiment_payload("good but also bad"))
    result = json.loads(response.json()["data"]["result"])
    assert result["label"] == "neutral"


async def test_unknown_capability(client) -> None:
    response = await client.post("/v1/capabilities/run", json={"capability": "unknown", "input": {}})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CAPABILITY_NOT_FOUND"


async def test_response_has_meta(client) -> None:
    success = await client.post("/v1/capabilities/run", json=_summary_payload())
    error = await client.post("/v1/capabilities/run", json={"capability": "unknown", "input": {}})
    for body in (success.json(), error.json()):
        assert body["meta"]["request_id"]
        assert body["meta"]["capability"]
        assert isinstance(body["meta"]["elapsed_ms"], int)


async def test_custom_request_id(client) -> None:
    response = await client.post("/v1/capabilities/run", json=_summary_payload(request_id="req-123"))
    assert response.json()["meta"]["request_id"] == "req-123"


async def test_missing_bearer_token_rejected(client) -> None:
    client.headers.pop("Authorization")
    response = await client.get("/health")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def _summary_payload(text: str | None = None, max_length: int = 120, request_id: str = "summary-1") -> dict:
    source = text if text is not None else (
        "人工智能系统可以通过统一的能力接口完成摘要、分类和情感分析，"
        "从而降低上层应用的接入复杂度。"
    )
    return {
        "capability": "text_summary",
        "input": {"text": source, "max_length": max_length},
        "request_id": request_id,
    }


def _sentiment_payload(text: str) -> dict:
    return {"capability": "sentiment_analysis", "input": {"text": text}}
