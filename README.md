# AI Capability Service

## Project Overview

这是一个最小但可交付的模型能力统一调用后端服务，基于 FastAPI 提供 `POST /v1/capabilities/run` 和 `POST /v1/capabilities/chat/stream`。当前内置 `text_summary`、`sentiment_analysis`，并额外提供流式对话能力；服务使用 `uv` 管理依赖与虚拟环境，支持 OpenAI、豆包、DeepSeek、智谱、通义千问等 OpenAI 兼容供应商，并为全部 API 增加 Bearer Token 鉴权。`request_id` 仅用于链路追踪，不表示模型；模型通过独立的 `model` 字段指定。

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
docker compose pull
docker compose up -d
```

Nginx 反代示例：

项目已提供可直接参考的 Nginx 配置文件：

- [ai-capability-service-lixin.conf](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/deploy/nginx/ai-capability-service-lixin.conf)

这份配置已经包含：

- HTTPS 终止
- 反向代理到 `127.0.0.1:37612`
- SSE 所需的 `proxy_buffering off`
- 适用于 `chat/stream` 的长连接超时设置

服务地址：`http://localhost:37612`  
接口文档：`http://localhost:37612/docs`

## API Overview

当前对外接口如下：

- `GET /health`
  - 健康检查
- `POST /v1/capabilities/run`
  - 同步能力调用
- `POST /v1/capabilities/chat/stream`
  - 流式对话，返回 `text/event-stream`

除 `/docs`、`/openapi.json`、`/redoc` 外，所有请求都需要：

```http
Authorization: Bearer <API_BEARER_TOKEN>
```

统一响应包说明：

- 同步成功：`{ ok, data, meta }`
- 同步失败：`{ ok, error, meta }`
- `meta` 固定包含：`request_id`、`capability`、`model`、`elapsed_ms`

更详细的字段定义、错误码和 SSE 事件说明见 [docs/api.md](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/docs/api.md)。

Swagger 调试说明：

- `/docs` 已声明 Bearer Token 安全方案
- 打开文档后，右上角会出现 `Authorize` 按钮
- 点击后填入：

- Swagger UI 会自动带上 `Authorization: Bearer ...`

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

`chat_stream`：

```bash
curl -N -X POST http://localhost:37612/v1/capabilities/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的 API_BEARER_TOKEN>" \
  -d '{
    "model": "qwen-plus-latest",
    "messages": [
      {"role": "system", "content": "你是一个简洁的中文助手。"},
      {"role": "user", "content": "请用三句话介绍这个服务。"}
    ]
  }'
```

流式接口返回 `text/event-stream`，事件类型包括：

- `meta`：请求元信息
- `chunk`：逐段返回的文本内容
- `done`：流结束与耗时
- `error`：流式处理中的错误

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
│   │   ├── chat_stream.py
│   │   ├── registry.py
│   │   ├── text_summary.py
│   │   └── sentiment_analysis.py
│   └── routers/
│       ├── __init__.py
│       ├── capabilities.py
│       └── chat_stream.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_capabilities.py
├── docs/
│   ├── architecture.md
│   └── api.md
├── agents/
├── deploy/
│   └── nginx/
│       └── ai-capability-service-lixin.conf
├── .env.example
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
└── README.md
```

目录说明：

- `app/`：服务主代码，包含配置、能力处理器、路由和鉴权
- `tests/`：最小测试集，覆盖同步能力、鉴权和流式接口
- `docs/`：架构说明与详细接口文档
- `agents/`：给 AI Coding Agent 的规则和技能说明
- `.github/workflows/`：CI/CD 和 Docker 镜像构建流程

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