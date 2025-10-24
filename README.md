# 🤖 智能客服系统 - LangGraph实战项目

> 基于LangGraph和硅基流动API构建的生产级智能客服系统

## 📋 目录

- [项目简介](#项目简�?
- [核心功能](#核心功能)
- [技术架构](#技术架�?
- [快速开始](#快速开�?
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [生产部署](#生产部署)
- [实际应用场景](#实际应用场景)

---

## 🎯 项目简�?
这是一�?*真正生产可用**的智能客服系统，展示了如何使用LangGraph构建复杂的AI应用。项目涵盖了企业级AI应用的核心要素：

- �?**多轮对话管理** - 基于LangGraph的状态图设计
- �?**意图识别与实体提�?* - 智能理解用户需�?- �?**RAG知识库检�?* - 向量数据库支持的知识问答
- �?**工具调用（Function Calling�?* - 集成真实业务系统
- �?**智能转人�?* - 复杂问题自动升级
- �?**完整日志与监�?* - 生产级可观测�?
## 🌟 核心功能

### 1. 智能对话引擎

基于LangGraph构建的状态机，支持复杂的对话流程控制�?
```
用户输入 �?意图分类 �?知识检�?工具调用 �?生成回复 �?满意度检�?```

### 2. 知识库管理（RAG�?
- 使用FAISS向量数据库存储企业知�?- 支持产品信息、FAQ、技术文档等多类型知�?- 语义检索，自动找到最相关的答�?
### 3. 业务工具集成

模拟真实业务场景，支持：
- 📦 **订单查询** - 查询订单状态、物流信�?- 💰 **退款处�?* - 自动处理退款申�?- 📊 **库存查询** - 实时库存信息
- 🚚 **物流跟踪** - 快递追�?
### 4. 生产级特�?
- 🔐 **配置管理** - 基于Pydantic的类型安全配�?- 📝 **结构化日�?* - 使用Loguru的多级日志系�?- 🛡�?**异常处理** - 完善的错误捕获和恢复机制
- 📈 **性能优化** - 向量索引、缓存策�?
---

## 🏗�?技术架�?
### 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **LLM框架** | LangChain + LangGraph | 对话流程编排 |
| **大模�?* | 硅基流动 API | Qwen2.5-7B-Instruct |
| **向量数据�?* | FAISS | 本地高性能向量检�?|
| **嵌入模型** | BGE-large-zh | 中文语义理解 |
| **配置管理** | Pydantic Settings | 类型安全的配�?|
| **日志系统** | Loguru | 结构化日�?|

### 架构�?
```
┌─────────────�?�? 用户输入    �?└──────┬──────�?       �?┌──────────────────────────────────────�?�?       LangGraph状态图引擎            �?�? ┌────────────────────────────────�? �?�? �? 1. 意图分类 (Intent Classifier)�? �?�? └────────┬───────────────────────�? �?�?          �?                          �?�? ┌────────────────────┬──────────�?  �?�? �? 2a. 知识检�?     �?2b. 工具调用�? �?�? �? (RAG)            �?(Tools)    �? �?�? └────────┬───────────┴──────┬───�?  �?�?          �?                 �?       �?�? ┌────────────────────────────────�? �?�? �? 3. 回复生成 (Response Gen)    �? �?�? └────────┬───────────────────────�? �?�?          �?                          �?�? ┌────────────────────────────────�? �?�? �? 4. 满意度检�?(Satisfaction)  �? �?�? └────────────────────────────────�? �?└──────────────────────────────────────�?       �?┌──────────────�?�? 智能回复     �?└──────────────�?```

---

## 🚀 快速开�?
### 环境要求

- Python 3.9+
- 8GB+ RAM（用于加载嵌入模型）

### 安装步骤

1. **克隆项目**

```bash
cd langraph_demo
```

2. **创建虚拟环境**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置API密钥**

项目已配置硅基流动API密钥，可直接使用。如需修改配置，请创建`.env`文件�?
```env
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
DEFAULT_MODEL=Qwen/Qwen2.5-7B-Instruct
```

5. **初始化知识库**

```bash
python examples/init_knowledge_base.py
```

这将创建包含产品信息、FAQ、技术文档的向量知识库�?
---

## 📖 使用指南

### 1. 简单对话示�?
最基础的交互式对话�?
```bash
python examples/simple_chat.py
```

支持的对话示例：
```
用户: iPhone 15 Pro多少钱？
客服: iPhone 15 Pro的价格是7999元起...

用户: 帮我查订单ORD001
客服: 您的订单ORD001状态为：已发货...
```

### 2. 高级功能演示

运行完整的功能演示，包括所有场景：

```bash
python examples/advanced_demo.py
```

演示内容�?- �?产品咨询（知识库检索）
- �?订单查询（工具调用）
- �?物流跟踪（工具调用）
- �?退款申请（工具调用�?- �?库存查询（工具调用）
- �?多轮对话（上下文理解�?- �?常见问题（FAQ�?- �?复杂问题转人�?
### 3. 代码集成示例

在你的代码中使用智能客服�?
```python
from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase

# 初始�?kb = KnowledgeBase()
kb.load()  # 加载已有知识�?agent = CustomerServiceAgent(knowledge_base=kb)

# 单次对话
response, state = agent.chat("iPhone 15 Pro多少钱？")
print(response)

# 多轮对话（保持上下文�?state = None
response1, state = agent.chat("帮我查订单ORD001", state)
response2, state = agent.chat("物流单号是多少？", state)
```

---

## 📁 项目结构

```
langraph_demo/
├── config/                 # 配置模块
�?  ├── __init__.py
�?  └── settings.py        # 系统配置（API密钥、模型配置等�?�?├── src/                   # 核心源代�?�?  ├── agents/           # 智能代理
�?  �?  ├── __init__.py
�?  �?  └── customer_service.py  # 客服Agent（LangGraph核心�?�?  �?�?  ├── knowledge_base/   # 知识库模�?�?  �?  ├── __init__.py
�?  �?  └── vector_store.py      # FAISS向量存储
�?  �?�?  ├── tools/            # 业务工具
�?  �?  ├── __init__.py
�?  �?  └── business_tools.py    # 订单/退�?库存等工�?�?  �?�?  ├── state.py          # 对话状态定�?�?  ├── llm_client.py     # LLM客户端封�?�?  └── utils.py          # 工具函数（日志等�?�?├── examples/              # 示例程序
�?  ├── init_knowledge_base.py   # 初始化知识库
�?  ├── simple_chat.py           # 简单对话示�?�?  └── advanced_demo.py         # 高级功能演示
�?├── data/                  # 数据目录
�?  └── vector_store/     # 向量数据库文�?�?├── logs/                  # 日志目录
�?├── requirements.txt       # Python依赖
├── .gitignore
└── README.md             # 本文�?```

### 核心模块说明

#### 1. `src/agents/customer_service.py` - 客服Agent

LangGraph状态图的核心实现：

- `_classify_intent()` - 意图分类节点
- `_retrieve_knowledge()` - 知识检索节�?- `_call_tools()` - 工具调用节点
- `_generate_response()` - 回复生成节点
- `_check_satisfaction()` - 满意度检查节�?
#### 2. `src/state.py` - 状态管�?
定义对话状态模型：

```python
class ConversationState:
    messages: List[Message]          # 对话历史
    intent: str                      # 当前意图
    entities: Dict[str, Any]         # 提取的实�?    tool_calls: List[Dict]           # 工具调用记录
    retrieved_docs: List[str]        # 检索结�?    requires_human: bool             # 是否需要转人工
```

#### 3. `src/knowledge_base/vector_store.py` - 知识�?
向量检索实现：

- `add_documents()` - 添加文档
- `search()` - 语义检�?- `save()/load()` - 持久�?
---

## 🏭 生产部署

### 性能优化建议

1. **模型优化**
   - 使用量化模型减少内存占用
   - 部署本地模型服务（如vLLM�?   - 实现请求批处�?
2. **向量数据�?*
   - 对于大规模数据，使用Milvus/Qdrant替代FAISS
   - 实现分片和副本机�?   - 添加缓存�?
3. **系统架构**
   - 使用FastAPI提供REST API
   - 添加Redis做会话管�?   - 实现消息队列异步处理

4. **监控告警**
   - 集成Prometheus指标
   - 添加响应时间监控
   - 异常自动告警

### 扩展API服务（可选）

创建`api/main.py`�?
```python
from fastapi import FastAPI
from langraph_customer_service.agents import CustomerServiceAgent

app = FastAPI()
agent = CustomerServiceAgent()

@app.post("/chat")
async def chat(message: str, session_id: str):
    response, state = agent.chat(message)
    return {"response": response, "session_id": session_id}
```

运行�?```bash
uvicorn api.main:app --reload
```

---

## 🎓 实际应用场景

### 1. 电商客服

**适用场景**�?- 商品咨询（价格、参数、库存）
- 订单管理（查询、修改、取消）
- 售后服务（退换货、投诉）

**集成方式**�?- 对接订单系统API
- 连接商品数据�?- 集成物流接口

### 2. 技术支�?
**适用场景**�?- 软件使用问题
- 故障诊断
- 配置指导

**知识库内�?*�?- 操作手册
- 常见问题解答
- 故障排查流程

### 3. 金融客服

**适用场景**�?- 账户查询
- 产品咨询
- 业务办理

**安全考虑**�?- 身份验证
- 敏感信息脱敏
- 审计日志

### 4. 企业内部助手

**适用场景**�?- IT工单处理
- HR政策查询
- 行政流程指导

**特点**�?- 私有化部�?- 权限管理
- 多系统集�?
---

## 🔑 关键技术点

### 1. LangGraph状态图设计

```python
# 条件路由示例
workflow.add_conditional_edges(
    "classify_intent",
    self._route_after_intent,
    {
        "knowledge": "retrieve_knowledge",
        "tool": "call_tools",
        "general": "generate_response"
    }
)
```

**优势**�?- 流程可视�?- 易于调试
- 灵活扩展

### 2. 意图识别与实体提�?
使用LLM进行结构化输出：

```python
{
    "intent": "order_query",
    "entities": {
        "order_id": "ORD001"
    },
    "needs_tool": true
}
```

### 3. RAG检索增�?
```python
# 1. 向量化查�?query_embedding = model.encode(query)

# 2. 检索相似文�?results = index.search(query_embedding, top_k=3)

# 3. 注入到prompt
context = "\n".join([r["document"] for r in results])
```

### 4. 工具调用模式

```python
tools = {
    "query_order": query_order,
    "process_refund": process_refund,
}

# 根据意图调用工具
if intent == "order_query":
    result = tools["query_order"](order_id)
```

---

## 📊 测试数据

项目内置测试数据�?
**订单数据**�?- ORD001 - 已发货的iPhone订单
- ORD002 - 处理中的MacBook订单

**物流单号**�?- SF1234567890 - 顺丰快�?
**商品**�?- iPhone 15 Pro
- MacBook Pro
- AirPods Pro

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下规范�?
1. **代码风格**：遵循PEP 8
2. **文档**：为新功能添加文档字符串
3. **测试**：添加单元测�?4. **日志**：使用统一的日志格�?
---

## 📄 许可�?
MIT License

---

## 💡 学习建议

### 对于初学�?
1. 先运行`simple_chat.py`理解基本流程
2. 查看`customer_service.py`了解LangGraph用法
3. 研究`state.py`理解状态设�?4. 尝试添加新的工具函数

### 对于进阶�?
1. 优化意图识别的准确�?2. 实现多模态支持（图片、语音）
3. 添加对话策略学习
4. 接入真实业务系统

### 推荐资源

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [硅基流动API文档](https://docs.siliconflow.cn/)
- [FAISS文档](https://github.com/facebookresearch/faiss)

---

## 🆘 常见问题

### Q: 如何更换LLM模型�?
A: 修改`.env`中的`DEFAULT_MODEL`配置，或在代码中指定�?
```python
from langraph_customer_service.llm_client import LLMClient
llm = LLMClient(model="Qwen/Qwen2.5-72B-Instruct")
```

### Q: 知识库支持多大规模？

A: FAISS支持百万级向量。更大规模建议使用Milvus/Qdrant�?
### Q: 如何添加新的业务工具�?
A: 在`src/tools/business_tools.py`中添加函数，然后在Agent中注册：

```python
def my_tool(param: str) -> Dict:
    return {"result": "..."}

# 在CustomerServiceAgent中注�?self.tools["my_tool"] = my_tool
```

### Q: 如何提高回复速度�?
A: 
1. 使用更小的模�?2. 减少检索的top_k数量
3. 实现结果缓存
4. 异步处理

---

## 📮 联系方式

- 项目地址：https://github.com/your-repo/langraph_demo
- 问题反馈：提交Issue

---

**�?如果这个项目对你有帮助，请给个Star�?*
