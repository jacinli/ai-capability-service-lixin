# AGENTS.md

## 目标

实现一个可运行、可测试、可容器化部署的 FastAPI 后端服务，对外提供统一 AI 能力调用接口。

## 必做范围

- 实现 `POST /v1/capabilities/run`
- 至少包含 `text_summary` 和 `sentiment_analysis`
- 有真实模型调用与 mock 回退
- 所有响应统一为 `{ok, data|error, meta}`
- 包含结构化日志与 `elapsed_ms`
- 包含 pytest 测试
- 使用 `Dockerfile` 与 `docker-compose.yml`
- 包含 GitHub Actions Docker 构建流程

## 项目约束

- 默认端口固定为 `37612`
- 所有用户可见文案优先中文
- 依赖环境使用 `uv`
- Bearer Token 通过 `.env` 中的 `API_BEARER_TOKEN` 提供
- 模型供应商配置通过 `.env` 中的 `MODEL_PROVIDER` 与 `*_API_KEY` / `*_API_BASE` / `*_MODEL` 提供
- 仓库中只能提交 `.env.example`，不能提交真实 `.env`
- 代码需支持无 API Key 的离线 mock 模式
- 不要在代码中硬编码任何密钥

## 实现顺序

1. 先阅读 [docs/architecture.md](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/docs/architecture.md) 与 [docs/api.md](/Users/jacinlee/selfwork/job/self-proj/ai-capability-service-lixin/docs/api.md)
2. 完成 `app/` 下的配置、模型、能力处理器、路由与入口
3. 完成 `tests/` 下的最小测试集
4. 增加 `.env.example`、`.gitignore`、`pyproject.toml`
5. 增加 Docker 与 docker-compose
6. 增加 GitHub Actions 镜像构建流程
7. 更新 README、docs 与 `agents/` 目录

## 编码规范

- 所有异步逻辑使用 `async def`
- 公共函数和类保留一行 docstring
- 使用 Pydantic v2 风格
- 统一通过 `logging` 输出日志，不使用 `print`
- 处理器输入校验失败抛 `ValueError`
- 模型调用失败抛 `ModelError`

## 验收清单

- `python -m app.main` 可以启动
- `curl http://localhost:37612/health` 返回正常
- `pytest` 全部通过
- `docker compose up --build` 可以拉起服务
- 未知能力返回 404
- 空文本返回 400
- 所有响应都带 `meta.elapsed_ms`
