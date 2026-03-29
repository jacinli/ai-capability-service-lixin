"""文本摘要能力。"""

from typing import Any

from openai import APIError

from app.capabilities.base import CapabilityHandler
from app.capabilities.registry import registry
from app.llm import build_openai_client, get_active_provider


class ModelError(Exception):
    """模型调用失败时抛出的异常。"""


class TextSummaryHandler(CapabilityHandler):
    """执行 text_summary 能力。"""

    name = "text_summary"

    async def run(self, input: dict[str, Any], model: str) -> str:
        """摘要输入文本并返回结果。"""

        text = self._validate_text(input.get("text"))
        max_length = self._validate_max_length(input.get("max_length", 120))
        provider = get_active_provider()
        if provider is None:
            return self._mock_summary(text, max_length)
        try:
            client = build_openai_client()
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Summarise the following "
                            f"text in no more than {max_length} characters. "
                            "Return only the summary, no preamble."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )
        except APIError as exc:
            raise ModelError(f"模型调用失败: {exc}") from exc
        result = (response.choices[0].message.content or "").strip()
        if not result:
            raise ModelError("模型未返回有效摘要。")
        return result

    def _validate_text(self, text: Any) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("`text` 字段必须是非空字符串。")
        return text.strip()

    def _validate_max_length(self, max_length: Any) -> int:
        if not isinstance(max_length, int) or not 20 <= max_length <= 2000:
            raise ValueError("`max_length` 必须是 20 到 2000 之间的整数。")
        return max_length

    def _mock_summary(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return f"{text[:max_length]}..."


registry.register(TextSummaryHandler())
