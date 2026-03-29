# API 说明

本地基础地址：`http://localhost:37612`  
FastAPI 文档：`http://localhost:37612/docs`

## POST /v1/capabilities/run

统一能力调用接口。

除 `/docs`、`/openapi.json`、`/redoc` 外，请求都需要携带：

```http
Authorization: Bearer <API_BEARER_TOKEN>
```

### 请求体

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `capability` | string | 是 | 要调用的能力名称 |
| `input` | object | 是 | 能力输入参数 |
| `model` | string | 否 | 指定本次调用使用的模型；不传时默认 `qwen-plus-latest` |
| `request_id` | string | 否 | 调用链跟踪 ID，不传则自动生成 |

### 成功响应

```json
{
  "ok": true,
  "data": {
    "result": "..."
  },
  "meta": {
    "request_id": "demo-001",
    "capability": "text_summary",
    "model": "qwen-plus-latest",
    "elapsed_ms": 8
  }
}
```

### 失败响应

```json
{
  "ok": false,
  "error": {
    "code": "INPUT_ERROR",
    "message": "错误信息",
    "details": {}
  },
  "meta": {
    "request_id": "demo-001",
    "capability": "text_summary",
    "model": "qwen-plus-latest",
    "elapsed_ms": 2
  }
}
```

## text_summary

输入字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `text` | string | 是 | - | 待摘要文本 |
| `max_length` | int | 否 | `120` | 摘要最大字符数，范围 20-2000 |

调用示例：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_BEARER_TOKEN>" \
  -d '{
    "capability": "text_summary",
    "input": {
      "text": "统一能力接口可以让上层业务只面对一个 API，而把底层模型切换和兼容逻辑收敛到服务端。",
      "max_length": 50
    },
    "request_id": "summary-demo"
  }'
```

## sentiment_analysis

输入字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 待分析文本 |

调用示例：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_BEARER_TOKEN>" \
  -d '{
    "capability": "sentiment_analysis",
    "input": {
      "text": "This product is great, amazing and wonderful."
    }
  }'
```

返回的 `data.result` 是 JSON 字符串，包含 `label`、`score`、`reasoning`。

## 错误示例

未知能力：

```bash
curl -X POST http://localhost:37612/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_BEARER_TOKEN>" \
  -d '{"capability":"unknown_cap","input":{}}'
```

健康检查：

```bash
curl -H "Authorization: Bearer <API_BEARER_TOKEN>" http://localhost:37612/health
```

## POST /v1/capabilities/chat/stream

流式对话接口，返回 `text/event-stream`。

请求体：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `messages` | array | 是 | 对话消息列表，元素包含 `role` 与 `content` |
| `model` | string | 否 | 本次流式对话使用的模型；不传时默认 `qwen-plus-latest` |
| `request_id` | string | 否 | 调用链跟踪 ID，不传则自动生成 |

示例：

```bash
curl -N -X POST http://localhost:37612/v1/capabilities/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_BEARER_TOKEN>" \
  -d '{
    "messages": [
      {"role": "system", "content": "你是一个简洁的中文助手。"},
      {"role": "user", "content": "请介绍这个服务。"}
    ]
  }'
```

SSE 事件：

- `meta`
- `chunk`
- `done`
- `error`
