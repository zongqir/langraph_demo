# 🏗️ 系统架构文档

本文档详细介绍智能客服系统的技术架构、设计思路和核心实现。

---

## 📐 整体架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    表现层 (API Layer)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   FastAPI    │  │  WebSocket   │  │   CLI App    │  │
│  │  REST API    │  │  Real-time   │  │  Interactive │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   业务层 (Service Layer)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │          CustomerServiceAgent (LangGraph)        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐   │  │
│  │  │ Intent     │→ │ Knowledge  │→ │ Response │   │  │
│  │  │ Classifier │  │ Retrieval  │  │ Generator│   │  │
│  │  └────────────┘  └────────────┘  └──────────┘   │  │
│  │         ↓                                         │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │         Tool Calling Layer                 │  │
│  │  │  [订单][退款][库存][物流][更多工具...]     │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   数据层 (Data Layer)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    FAISS     │  │     Redis    │  │   Database   │  │
│  │  向量知识库   │  │   会话缓存    │  │  业务数据库   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 LangGraph状态图设计

### 核心状态机

```
                    [用户输入]
                        ↓
              ┌──────────────────┐
              │  意图分类节点      │
              │ classify_intent  │
              └────────┬─────────┘
                       ↓
         ┌─────────────┴─────────────┐
         ↓             ↓             ↓
    [需要工具]    [需要知识]    [一般对话]
         ↓             ↓             ↓
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │工具调用  │ │知识检索  │ │          │
   │call_tools│ │retrieve  │ │          │
   └────┬─────┘ └────┬─────┘ │          │
        └────────────┴────────┴──────────┘
                     ↓
            ┌─────────────────┐
            │  生成回复节点     │
            │generate_response│
            └────────┬────────┘
                     ↓
            ┌─────────────────┐
            │  满意度检查节点   │
            │check_satisfaction│
            └────────┬────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
    [继续对话]                [转人工]
        ↓                         ↓
      [END]                     [END]
```

### 节点功能说明

| 节点名称 | 功能描述 | 输入 | 输出 |
|---------|---------|------|------|
| **classify_intent** | 意图识别与实体提取 | 用户消息 | intent, entities |
| **retrieve_knowledge** | 向量检索相关知识 | 用户问题 | retrieved_docs |
| **call_tools** | 调用业务工具 | intent + entities | tool_results |
| **generate_response** | 生成自然语言回复 | context + history | response |
| **check_satisfaction** | 判断是否需要人工 | user_message | requires_human |

---

## 🧠 核心组件详解

### 1. 状态管理（State Management）

#### ConversationState模型

```python
class ConversationState:
    # 对话数据
    messages: List[Message]           # 完整对话历史
    session_id: str                   # 会话唯一标识
    user_id: Optional[str]            # 用户标识
    
    # AI理解
    intent: str                       # 当前意图
    entities: Dict[str, Any]          # 提取的实体
    
    # 上下文
    context: Dict[str, Any]           # 临时上下文
    retrieved_docs: List[str]         # 检索结果
    tool_calls: List[Dict]            # 工具调用历史
    
    # 流程控制
    current_response: str             # 当前回复
    requires_human: bool              # 是否转人工
    status: Literal["active", "waiting", "completed", "escalated"]
```

**设计思路**：
- 完整记录对话上下文，支持多轮对话
- 状态可序列化，便于持久化和恢复
- 包含业务流程控制字段

### 2. 意图识别（Intent Classification）

#### 实现方式

使用LLM进行零样本意图分类：

```python
# 1. 定义意图类型
INTENT_TYPES = [
    "order_query",      # 订单查询
    "refund_request",   # 退款申请
    "inventory_check",  # 库存查询
    "logistics_query",  # 物流查询
    "product_info",     # 产品咨询
    "general_chat"      # 一般聊天
]

# 2. 构造结构化prompt
prompt = f"""
请识别用户意图并提取实体信息。
返回JSON格式：
{{
    "intent": "意图类型",
    "entities": {{"order_id": "...", ...}},
    "confidence": 0.95,
    "needs_tool": true/false,
    "needs_knowledge": true/false
}}
"""

# 3. LLM推理
response = llm.invoke(prompt)
result = json.loads(response)
```

**优势**：
- 无需训练分类模型
- 易于扩展新意图
- 自动提取实体信息

### 3. 知识检索（RAG）

#### 向量检索流程

```
用户问题
    ↓
[1] 文本→向量
    ↓ (Embedding Model)
查询向量
    ↓
[2] 向量相似度搜索
    ↓ (FAISS Index)
Top-K相似文档
    ↓
[3] 重排序（可选）
    ↓
相关知识片段
    ↓
[4] 注入到Prompt
    ↓
生成回复
```

#### 技术细节

```python
# 1. 文档向量化
embeddings = embedding_model.encode(documents)
faiss_index.add(embeddings)

# 2. 查询检索
query_vector = embedding_model.encode(query)
distances, indices = faiss_index.search(query_vector, k=3)

# 3. 构建上下文
context = "\n".join([documents[i] for i in indices[0]])

# 4. 生成回复
prompt = f"""
参考资料：
{context}

用户问题：{query}

请基于参考资料回答：
"""
```

**优化策略**：
- 使用中文优化的嵌入模型（BGE）
- 合理设置检索数量（top-k）
- 实现结果缓存减少计算

### 4. 工具调用（Tool Calling）

#### 工具注册机制

```python
class CustomerServiceAgent:
    def __init__(self):
        # 工具映射表
        self.tools = {
            "query_order": query_order,
            "process_refund": process_refund,
            "check_inventory": check_inventory,
            "get_logistics_info": get_logistics_info
        }
    
    def _call_tools(self, state: ConversationState):
        # 根据意图选择工具
        tool_name = self._intent_to_tool(state.intent)
        if tool_name in self.tools:
            # 提取参数
            params = self._extract_params(state.entities)
            # 调用工具
            result = self.tools[tool_name](**params)
            # 记录结果
            state.tool_calls.append(result)
        return state
```

#### 工具函数规范

所有工具函数遵循统一规范：

```python
def tool_function(param: str) -> Dict[str, Any]:
    """
    工具函数说明
    
    Args:
        param: 参数说明
    
    Returns:
        {
            "success": bool,       # 是否成功
            "data": {...},         # 返回数据
            "message": str         # 消息说明
        }
    """
    # 实现逻辑
    return {"success": True, "data": {}, "message": ""}
```

**优势**：
- 统一的接口规范
- 易于添加新工具
- 支持异步调用

### 5. 回复生成（Response Generation）

#### Prompt工程

```python
system_prompt = f"""
你是{settings.customer_service_name}，代表{settings.company_name}。

服务准则：
1. 保持礼貌、专业、耐心
2. 基于提供的上下文回答
3. 信息不足时主动询问
4. 复杂问题建议转人工

当前意图：{state.intent}
"""

user_prompt = f"""
对话历史：
{format_history(state.messages)}

上下文信息：
{format_context(state)}

用户问题：{user_message}

请生成回复：
"""
```

**设计原则**：
- 清晰的角色定位
- 结构化的上下文
- 明确的输出要求

---

## 🔌 集成接口

### 1. REST API

```python
# POST /chat
{
    "message": "用户消息",
    "session_id": "会话ID（可选）",
    "user_id": "用户ID（可选）"
}

# Response
{
    "response": "客服回复",
    "session_id": "会话ID",
    "intent": "识别的意图",
    "requires_human": false,
    "timestamp": "2024-01-01T00:00:00"
}
```

### 2. Python SDK

```python
from src.agents import CustomerServiceAgent

# 初始化
agent = CustomerServiceAgent()

# 单轮对话
response, state = agent.chat("用户消息")

# 多轮对话
state = None
for user_input in conversation:
    response, state = agent.chat(user_input, state)
```

### 3. 命令行界面

```bash
# 交互式对话
python examples/simple_chat.py

# 批量测试
python examples/advanced_demo.py
```

---

## 📊 数据流转

### 完整请求流程

```
1. 用户输入
   ↓
2. API层接收请求
   ↓
3. 检查/创建会话状态
   ↓
4. 进入LangGraph状态图
   ├─ 意图分类
   ├─ 条件路由
   │  ├─ 知识检索
   │  ├─ 工具调用
   │  └─ 直接回复
   ├─ 生成回复
   └─ 满意度检查
   ↓
5. 更新会话状态
   ↓
6. 返回响应
   ↓
7. 用户收到回复
```

### 状态流转示例

```python
# 初始状态
state = ConversationState(
    session_id="xxx",
    messages=[],
    intent=None
)

# 添加用户消息
state.add_message("user", "帮我查订单ORD001")

# 意图分类
state.intent = "order_query"
state.entities = {"order_id": "ORD001"}

# 工具调用
tool_result = query_order("ORD001")
state.tool_calls.append(tool_result)

# 生成回复
state.current_response = "您的订单ORD001状态为：已发货..."
state.add_message("assistant", state.current_response)

# 返回状态
return state
```

---

## ⚙️ 配置管理

### 分层配置

```
1. 代码默认值
   ↓
2. 配置文件 (.env)
   ↓
3. 环境变量
   ↓
4. 运行时参数
```

### 配置加载

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API配置
    siliconflow_api_key: str
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    
    # 模型配置
    default_model: str = "Qwen/Qwen2.5-7B-Instruct"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局实例
settings = Settings()
```

---

## 🔍 日志与监控

### 日志层级

```python
# DEBUG - 详细调试信息
log.debug("查询向量: shape={}", vector.shape)

# INFO - 一般信息
log.info("处理用户消息: session={}", session_id)

# WARNING - 警告信息
log.warning("知识库未找到，使用无知识库模式")

# ERROR - 错误信息
log.error("API调用失败: {}", error)
```

### 监控指标

```python
# 请求量
requests_total = Counter('requests_total')

# 响应时间
response_time = Histogram('response_time_seconds')

# 活跃会话
active_sessions = Gauge('active_sessions')

# 错误率
error_rate = Counter('errors_total')
```

---

## 🚀 性能优化

### 1. 缓存策略

```python
# 响应缓存
@cache(expire=3600)
def get_product_info(product_id):
    pass

# 向量缓存
@lru_cache(maxsize=1000)
def get_embedding(text):
    pass
```

### 2. 批处理

```python
# 批量嵌入
embeddings = model.encode(texts, batch_size=32)

# 批量推理
responses = llm.batch_generate(prompts)
```

### 3. 异步处理

```python
async def async_chat(message: str):
    # 异步LLM调用
    response = await llm.ainvoke(message)
    return response
```

---

## 🔐 安全设计

### 1. 输入验证

```python
# 长度限制
assert len(message) <= 1000

# 内容过滤
message = sanitize_input(message)

# 频率限制
@rate_limit("10/minute")
def chat(message):
    pass
```

### 2. 敏感信息保护

```python
# 脱敏处理
def mask_sensitive(text):
    text = re.sub(r'\d{11}', '***', text)  # 手机号
    text = re.sub(r'\d{15,18}', '***', text)  # 身份证
    return text
```

### 3. 访问控制

```python
# 认证中间件
@require_auth
def protected_endpoint():
    pass

# 权限检查
if not user.has_permission("chat"):
    raise PermissionError()
```

---

## 📈 扩展性设计

### 1. 插件化架构

```python
# 工具插件
class ToolPlugin:
    def register(self, agent):
        agent.tools[self.name] = self.execute

# 注册插件
plugin = CustomToolPlugin()
plugin.register(agent)
```

### 2. 多租户支持

```python
# 租户隔离
class TenantAgent:
    def __init__(self, tenant_id):
        self.kb = load_knowledge_base(tenant_id)
        self.tools = load_tools(tenant_id)
```

### 3. 多语言支持

```python
# 国际化
from i18n import translate

response = translate(
    text=raw_response,
    source="zh",
    target=user.language
)
```

---

## 🧪 测试策略

### 1. 单元测试

```python
def test_intent_classification():
    state = ConversationState(...)
    agent._classify_intent(state)
    assert state.intent == "order_query"
```

### 2. 集成测试

```python
def test_full_conversation():
    agent = CustomerServiceAgent()
    response, state = agent.chat("查订单ORD001")
    assert "已发货" in response
```

### 3. 性能测试

```python
def test_response_time():
    start = time.time()
    agent.chat(message)
    duration = time.time() - start
    assert duration < 5.0  # 5秒内响应
```

---

## 📚 参考资料

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain文档](https://python.langchain.com/)
- [FAISS文档](https://github.com/facebookresearch/faiss)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Pydantic文档](https://docs.pydantic.dev/)

---

**本架构文档将随项目演进持续更新。**

