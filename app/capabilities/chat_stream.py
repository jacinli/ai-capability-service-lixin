"""流式对话能力。"""

import asyncio
from collections.abc import AsyncIterator

from openai import APIError

from app.capabilities.text_summary import ModelError
from app.llm import build_openai_client, get_active_provider
from app.models.schemas import ChatMessage


class ChatStreamService:
    """按流式方式输出对话回复。"""

    capability = "chat_stream"

    async def stream(self, messages: list[ChatMessage], model: str) -> AsyncIterator[str]:
        """根据消息列表逐段返回回复内容。"""

        user_message = self._last_user_message(messages)
        provider = get_active_provider()
        if provider is None:
            async for chunk in self._mock_stream(user_message):
                yield chunk
            return
        try:
            client = build_openai_client()
            stream = await client.chat.completions.create(
                model=model,
                messages=[message.model_dump() for message in messages],
                stream=True,
            )
            async for event in stream:
                delta = event.choices[0].delta.content or ""
                if delta:
                    yield delta
        except APIError as exc:
            raise ModelError(f"模型流式调用失败: {exc}") from exc

    def _last_user_message(self, messages: list[ChatMessage]) -> str:
        for message in reversed(messages):
            if message.role == "user" and message.content.strip():
                return message.content.strip()
        raise ValueError("`messages` 中至少需要一条 role=user 的非空消息。")

    async def _mock_stream(self, user_message: str) -> AsyncIterator[str]:
        reply = (
            "这是一个流式 mock 回复。"
            f"我已经收到你的问题：{user_message[:80]}。"
            "当前服务会按片段持续输出内容，便于前端逐步渲染。"
        )
        for index in range(0, len(reply), 10):
            await asyncio.sleep(0)
            yield reply[index : index + 10]


chat_stream_service = ChatStreamService()
