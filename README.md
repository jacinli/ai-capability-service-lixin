# AI Capability Service

## Project Overview

这是一个最小但可交付的模型能力统一调用后端服务，基于 FastAPI 提供 `POST /v1/capabilities/run`，当前内置 `text_summary` 与 `sentiment_analysis` 两个能力；服务使用 `uv` 管理依赖与虚拟环境，支持 OpenAI、豆包、DeepSeek、智谱、通义千问等 OpenAI 兼容供应商，并为全部 API 增加 Bearer Token 鉴权。`request_id` 仅用于链路追踪，不表示模型；模型通过独立的 `model` 字段指定。

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic v2 + pydantic-settings
- OpenAI Python SDK
- Uvicorn
- pytest + pytest-asyncio
- Docker / docker-compose
- GitHub Actions + GHCR
- uv

## Quick Start

先决条件：Python 3.11+

安装依赖：

```bash
uv sync
```

复制环境变量：

```bash
cp .env.example .env
```

说明：

- `API_BEARER_TOKEN` 用于所有 API 的 Bearer 鉴权
- `MODEL_PROVIDER` 选择当前供应商：`openai`、`doubao`、`deepseek`、`zhipu`、`qwen`
- 对应的 `*_API_KEY`、`*_API_BASE`、`*_MODEL` 都从 `.env` 读取
- 不要提交真实 `.env` 文件
- 未配置可用 key 时，服务自动回退为 mock 模式
- 如果请求里不传 `model`，后端默认使用 `qwen-plus-latest`
- 当前默认模板使用：`qwen-plus-latest`、`deepseek-chat`、`doubao-seed-1-8-251228`

本地运行：

```bash
uv run python -m app.main
```

或：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 37612
```

使用 Docker Compose：

```bash
docker compose up --build -d
```

服务地址：`http://localhost:37612`  
接口文档：`http://localhost:37612/docs`

## curl Examples

`text_summary`：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的 API_BEARER_TOKEN>" \
  -d '{
    "capability": "text_summary",
    "input": {
      "text": "人工智能能力服务可以通过统一入口封装多种模型能力，降低上层业务的接入成本，同时保留后续扩展空间。",
      "max_length": 60
    },
    "request_id": "demo-summary-001"
  }'
```

`sentiment_analysis`：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的 API_BEARER_TOKEN>" \
  -d '{
    "capability": "sentiment_analysis",
    "input": {
      "text": "I love this service, it is amazing and wonderful."
    }
  }'
```

错误示例：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的 API_BEARER_TOKEN>" \
  -d '{"capability": "unknown_capability", "input": {}}'
```

## Running Tests

```bash
uv run pytest
```

测试不需要 API Key，默认强制走 mock 分支。

## Project Structure

```text
ai-capability-service-lixin/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── capabilities/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── text_summary.py
│   │   └── sentiment_analysis.py
│   └── routers/
│       ├── __init__.py
│       └── capabilities.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_capabilities.py
├── docs/
│   ├── architecture.md
│   └── api.md
├── agents/
├── .env.example
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Adding a New Capability

1. 在 [app/capabilities](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/app/capabilities) 新建处理器文件，并继承 `CapabilityHandler`。
2. 在文件末尾调用 `registry.register(YourHandler())` 完成注册。
3. 在 [app/main.py](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/app/main.py) 导入该模块，让注册逻辑在启动时生效。

## 支持的模型供应商

- OpenAI：`https://api.openai.com/v1`
- 豆包 / 火山方舟：`https://ark.cn-beijing.volces.com/api/v3`
- DeepSeek：`https://api.deepseek.com`
- 智谱：`https://open.bigmodel.cn/api/paas/v4/`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`

说明：这些供应商都通过 `.env` 配置，仓库只保留模板，不保留真实 key。
