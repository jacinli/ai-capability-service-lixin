"""能力处理器抽象基类。"""

from abc import ABC, abstractmethod
from typing import Any


class CapabilityHandler(ABC):
    """所有能力处理器的统一接口。"""

    name: str

    @abstractmethod
    async def run(self, input: dict[str, Any], model: str) -> str:
        """执行能力处理逻辑并返回字符串结果。"""
