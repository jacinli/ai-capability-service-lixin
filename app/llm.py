"""模型供应商配置与客户端构建。"""

from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import settings


@dataclass(frozen=True)
class LLMProvider:
    """统一描述一个 OpenAI 兼容供应商。"""

    name: str
    api_key: str
    api_base: str
    model: str


def get_active_provider() -> LLMProvider | None:
    """根据环境变量解析当前启用的模型供应商。"""

    provider_name = settings.model_provider.lower()
    providers = {
        "openai": LLMProvider(
            name="openai",
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            model=settings.openai_model,
        ),
        "doubao": LLMProvider(
            name="doubao",
            api_key=settings.doubao_api_key,
            api_base=settings.doubao_api_base,
            model=settings.doubao_model,
        ),
        "deepseek": LLMProvider(
            name="deepseek",
            api_key=settings.deepseek_api_key,
            api_base=settings.deepseek_api_base,
            model=settings.deepseek_model,
        ),
        "zhipu": LLMProvider(
            name="zhipu",
            api_key=settings.zhipu_api_key,
            api_base=settings.zhipu_api_base,
            model=settings.zhipu_model,
        ),
        "qwen": LLMProvider(
            name="qwen",
            api_key=settings.qwen_api_key,
            api_base=settings.qwen_api_base,
            model=settings.qwen_model,
        ),
    }
    provider = providers.get(provider_name)
    if provider is None or not provider.api_key or not provider.model:
        return None
    return provider


def build_openai_client() -> AsyncOpenAI:
    """构建当前激活供应商对应的客户端。"""

    provider = get_active_provider()
    if provider is None:
        raise ValueError("未配置可用模型供应商。")
    return AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_base)
