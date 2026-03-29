"""情感分析能力。"""

import json
import re
from typing import Any

from openai import APIError

from app.capabilities.base import CapabilityHandler
from app.capabilities.registry import registry
from app.llm import build_openai_client, get_active_provider
from app.capabilities.text_summary import ModelError

POSITIVE_WORDS = (
    "good",
    "great",
    "love",
    "excellent",
    "happy",
    "best",
    "amazing",
    "fantastic",
    "wonderful",
)
NEGATIVE_WORDS = (
    "bad",
    "terrible",
    "hate",
    "awful",
    "worst",
    "horrible",
    "poor",
    "disappointing",
)


class SentimentAnalysisHandler(CapabilityHandler):
    """执行 sentiment_analysis 能力。"""

    name = "sentiment_analysis"

    async def run(self, input: dict[str, Any], model: str) -> str:
        """分析输入文本情感并返回 JSON 字符串。"""

        text = self._validate_text(input.get("text"))
        provider = get_active_provider()
        if provider is None:
            return self._mock_sentiment(text)
        try:
            client = build_openai_client()
            response = await client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only a JSON object with fields label, score, "
                            "reasoning. label must be positive, neutral, or negative. "
                            "score must be a float from 0 to 1. reasoning must be one sentence."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )
        except APIError as exc:
            raise ModelError(f"模型调用失败: {exc}") from exc
        content = (response.choices[0].message.content or "").strip()
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ModelError("模型未返回合法 JSON。") from exc
        return json.dumps(payload, ensure_ascii=False)

    def _validate_text(self, text: Any) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("`text` 字段必须是非空字符串。")
        return text.strip()

    def _mock_sentiment(self, text: str) -> str:
        lowered = text.lower()
        positive_count = self._count_keywords(lowered, POSITIVE_WORDS)
        negative_count = self._count_keywords(lowered, NEGATIVE_WORDS)
        if positive_count > negative_count:
            label, score = "positive", min(0.5 + 0.1 * positive_count, 0.99)
        elif negative_count > positive_count:
            label, score = "negative", min(0.5 + 0.1 * negative_count, 0.99)
        else:
            label, score = "neutral", 0.5
        payload = {
            "label": label,
            "score": score,
            "reasoning": "Mock sentiment analysis based on keyword matching.",
        }
        return json.dumps(payload, ensure_ascii=False)

    def _count_keywords(self, text: str, keywords: tuple[str, ...]) -> int:
        return sum(len(re.findall(rf"\b{re.escape(word)}\b", text)) for word in keywords)


registry.register(SentimentAnalysisHandler())
