# 架构说明

## 服务概览

`ai-capability-service-lixin` 是一个统一模型能力分发后端。客户端通过单一接口提交能力名与结构化输入，服务完成能力查找、输入校验、模型调用或 mock 回退，并返回统一响应包。

## 技术选型

| 层 | 选型 | 说明 |
|---|---|---|
| 语言 | Python 3.11+ | 生态成熟，适合快速实现 AI 服务 |
| Web 框架 | FastAPI | 原生异步，类型标注友好 |
| 配置 | pydantic-settings | 统一读取 `.env` 与环境变量 |
| 依赖管理 | uv | 统一开发环境、锁定依赖 |
| 模型 SDK | openai | 支持 OpenAI 兼容 API Base |
| 日志 | logging + JSON formatter | 标准输出结构化日志 |
| 测试 | pytest + httpx | 不依赖真实网络调用 |
| 部署 | Docker + docker-compose | 便于本地和面试环境复现 |
| CI/CD | GitHub Actions + GHCR | 自动测试、构建并推送镜像 |

## 目录结构

```text
ai-capability-service-lixin/
├── app/
├── tests/
├── docs/
├── agents/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## 请求流程

```text
客户端
  -> POST /v1/capabilities/run
  -> Pydantic 校验请求体
  -> Registry 查找 capability
  -> Handler.run(input)
  -> OpenAI 或 mock
  -> 返回统一 envelope
```

## 能力扩展模式

每个能力都是一个独立处理器，实现 `CapabilityHandler.run()` 并在模块加载时注册到 `registry`。新增能力时不需要改 router，只需增加处理器并在启动文件中导入。

## 模型调用策略

- 当前支持 OpenAI、豆包、DeepSeek、智谱、通义千问。
- 通过 `MODEL_PROVIDER` 指定当前供应商。
- 各供应商对应的 `*_API_KEY`、`*_API_BASE`、`*_MODEL` 都从 `.env` 读取。
- 默认模型示例为 `qwen-plus-latest`、`deepseek-chat`、`doubao-seed-1-8-251228`。
- 未配置 key 时自动回退为 deterministic mock，确保无网络也可演示与测试。

## 错误码

| 错误码 | HTTP 状态码 | 含义 |
|---|---|---|
| `VALIDATION_ERROR` | 422 | 请求体结构校验失败 |
| `CAPABILITY_NOT_FOUND` | 404 | 未注册的能力名称 |
| `INPUT_ERROR` | 400 | 能力内部输入校验失败 |
| `MODEL_ERROR` | 502 | 模型调用异常 |
| `INTERNAL_ERROR` | 500 | 未处理的服务端异常 |

## 日志与配置

- 所有请求按 JSON 输出日志，包含 `request_id`、`capability`、`elapsed_ms`、`ok`。
- 默认端口为 `37612`。
- 所有 API 路径要求 Bearer Token，防止被刷。
- 必须使用 `.env.example` 作为配置模板，真实 `.env` 不应提交到仓库。
