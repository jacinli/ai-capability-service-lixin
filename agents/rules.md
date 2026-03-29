# Agent Rules

## 基本规则

- 默认使用中文交流和文档
- 接口默认端口是 `37612`
- 使用 `uv` 管理依赖与虚拟环境
- 所有配置项从环境变量读取，优先读取 `.env`
- 仓库中只能保留 `.env.example`，禁止提交真实 `.env`
- 所有返回必须保持统一 envelope 结构
- 所有 API 必须做 Bearer Token 鉴权

## 代码规则

- 新能力放在 `app/capabilities/`
- 所有能力必须注册到 `registry`
- 路由层只负责调度、计时、包装响应和日志
- 模型依赖必须可通过 mock 替代
- 测试中禁止真实网络请求

## 部署规则

- 使用 `Dockerfile` 构建镜像
- 使用 `docker-compose.yml` 从 GHCR 镜像部署
- GitHub Actions 负责测试和 Docker 镜像构建
- 镜像推送目标默认使用 GHCR
