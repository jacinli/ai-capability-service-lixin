# Agent Skills

## 推荐技能清单

### 1. FastAPI Service Design

- 设计统一响应结构
- 使用 APIRouter 管理版本化接口
- 通过异常分类控制状态码

### 2. OpenAI Compatible Integration

- 通过 `.env` 注入 `OPENAI_API_KEY`
- 通过 `.env` 注入 `OPENAI_API_BASE`
- 通过 `MODEL_PROVIDER` 切换 OpenAI、豆包、DeepSeek、智谱、千问
- 为不可用场景提供 deterministic mock

### 3. Testing First

- 用 `httpx.AsyncClient + ASGITransport` 直接测 ASGI
- 使用 `monkeypatch` 固定 mock 路径
- 重点覆盖成功、输入错误、未知能力、meta 字段

### 4. Docker Delivery

- 使用轻量 Python 基础镜像
- 显式暴露 `37612`
- 通过 compose 拉取 GHCR 镜像并注入 `.env`

### 5. GitHub CI/CD

- Push / PR 自动执行测试
- 构建 Docker 镜像
- 非 PR 场景推送到 GHCR
