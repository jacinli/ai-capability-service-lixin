"""能力注册中心。"""

from app.capabilities.base import CapabilityHandler


class CapabilityRegistry:
    """维护能力名称到处理器实例的映射。"""

    def __init__(self) -> None:
        self._handlers: dict[str, CapabilityHandler] = {}

    def register(self, handler: CapabilityHandler) -> None:
        """注册一个能力处理器。"""

        self._handlers[handler.name] = handler

    def get(self, name: str) -> CapabilityHandler | None:
        """按名称获取处理器。"""

        return self._handlers.get(name)

    def available(self) -> list[str]:
        """返回当前可用能力列表。"""

        return list(self._handlers.keys())


registry = CapabilityRegistry()
