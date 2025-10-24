# 📚 学习指南

本文档专为学习者设计，帮助你理解智能客服系统的核心概念、实现细节和最佳实践。

---

## 🎯 学习目标

通过这个项目，你将学到：

1. **LangGraph状态图编程** - 如何用图结构组织AI应用逻辑
2. **RAG检索增强生成** - 如何让AI基于知识库回答问题
3. **Function Calling** - 如何让AI调用外部工具
4. **生产级工程实践** - 配置管理、日志、错误处理等
5. **实际业务场景** - 真实客服系统的设计思路

---

## 🗺️ 学习路径

### 阶段1: 基础理解（1-2天）

#### 1.1 运行第一个示例

```bash
# 快速体验
python quickstart.py

# 交互式对话
python examples/simple_chat.py
```

**学习要点**：
- 观察系统如何理解你的问题
- 尝试不同类型的问题（产品咨询、订单查询等）
- 注意系统的回复风格和准确性

#### 1.2 阅读核心代码

按以下顺序阅读：

1. **`src/state.py`** - 理解对话状态的数据结构
   ```python
   # 关注这些字段
   messages: List[Message]      # 对话历史怎么存储
   intent: str                  # 意图如何表示
   entities: Dict[str, Any]     # 实体信息如何组织
   ```

2. **`src/llm_client.py`** - 了解如何调用LLM
   ```python
   # 关键方法
   def invoke(messages):  # 同步调用
   async def ainvoke(messages):  # 异步调用
   ```

3. **`src/agents/customer_service.py`** - 核心逻辑
   ```python
   # 重点理解
   _build_graph()           # 状态图构建
   _classify_intent()       # 意图识别
   _call_tools()           # 工具调用
   _generate_response()    # 回复生成
   ```

**练习任务**：
- [ ] 画出系统的数据流图
- [ ] 列出所有支持的意图类型
- [ ] 理解消息如何在节点间传递

### 阶段2: 深入实践（3-5天）

#### 2.1 理解LangGraph工作流

**关键代码**：`src/agents/customer_service.py` 中的 `_build_graph()`

```python
# 1. 创建状态图
workflow = StateGraph(ConversationState)

# 2. 添加节点（每个节点是一个函数）
workflow.add_node("classify_intent", self._classify_intent)
workflow.add_node("call_tools", self._call_tools)

# 3. 设置入口
workflow.set_entry_point("classify_intent")

# 4. 添加条件边（根据状态决定路由）
workflow.add_conditional_edges(
    "classify_intent",
    self._route_after_intent,  # 路由函数
    {
        "knowledge": "retrieve_knowledge",
        "tool": "call_tools",
        "general": "generate_response"
    }
)

# 5. 编译成可执行图
graph = workflow.compile()
```

**实验**：
1. 修改路由逻辑，观察行为变化
2. 添加一个新节点（如：情感分析）
3. 调整节点执行顺序

#### 2.2 掌握RAG检索

**关键代码**：`src/knowledge_base/vector_store.py`

```python
# 向量化流程
documents = ["文档1", "文档2", "文档3"]
embeddings = model.encode(documents)  # 文本→向量
index.add(embeddings)                 # 添加到索引

# 检索流程
query_vector = model.encode("用户问题")
distances, indices = index.search(query_vector, k=3)
results = [documents[i] for i in indices[0]]
```

**核心概念**：
- **嵌入（Embedding）**：文本转向量的过程
- **相似度**：向量间的距离（L2、余弦等）
- **索引（Index）**：快速检索的数据结构

**实验**：
1. 添加自己的知识文档
   ```python
   kb = KnowledgeBase()
   kb.add_documents([
       "你的知识1",
       "你的知识2"
   ])
   kb.save()
   ```

2. 测试检索效果
   ```python
   results = kb.search("你的问题", top_k=3)
   for r in results:
       print(f"相似度: {r['score']}")
       print(f"文档: {r['document']}")
   ```

3. 调整参数观察影响
   - `top_k`：返回结果数量
   - `score_threshold`：相似度阈值

#### 2.3 实现工具调用

**关键代码**：`src/tools/business_tools.py`

工具函数的标准模式：

```python
def my_tool(param1: str, param2: int) -> Dict[str, Any]:
    """
    工具功能说明
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        {
            "success": bool,
            "data": {...},
            "message": str
        }
    """
    try:
        # 1. 参数验证
        if not param1:
            return {"success": False, "message": "参数错误"}
        
        # 2. 执行业务逻辑
        result = do_something(param1, param2)
        
        # 3. 返回结果
        return {
            "success": True,
            "data": result,
            "message": "操作成功"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
```

**练习任务**：
- [ ] 添加一个"查询天气"工具
- [ ] 实现一个"发送邮件"工具
- [ ] 创建一个"数据库查询"工具

示例实现：

```python
# src/tools/weather_tools.py
def get_weather(city: str) -> Dict[str, Any]:
    """查询天气"""
    # 模拟天气数据
    weather_data = {
        "北京": {"temp": 15, "condition": "晴"},
        "上海": {"temp": 20, "condition": "多云"}
    }
    
    if city in weather_data:
        return {
            "success": True,
            "data": weather_data[city],
            "message": f"{city}天气查询成功"
        }
    else:
        return {
            "success": False,
            "message": f"未找到{city}的天气信息"
        }

# 在Agent中注册
self.tools["get_weather"] = get_weather
```

### 阶段3: 高级特性（5-7天）

#### 3.1 优化意图识别

**当前实现**：使用LLM零样本分类

**优化方向**：
1. **Few-shot学习**：提供示例提升准确性
   ```python
   examples = """
   示例1：
   用户：我的订单什么时候到？
   意图：logistics_query
   
   示例2：
   用户：iPhone 15多少钱？
   意图：product_info
   """
   prompt = f"{examples}\n\n用户：{user_input}\n意图："
   ```

2. **意图缓存**：相似问题直接返回
   ```python
   @lru_cache(maxsize=100)
   def classify_intent(message: str) -> str:
       # LLM分类逻辑
       pass
   ```

3. **置信度阈值**：低置信度转人工
   ```python
   if result["confidence"] < 0.7:
       state.requires_human = True
   ```

#### 3.2 实现会话管理

**需求**：支持多个用户并发对话

**实现方案**：

```python
# 使用Redis存储会话
import redis
import pickle

redis_client = redis.Redis()

class SessionManager:
    def save_session(self, session_id: str, state: ConversationState):
        """保存会话"""
        data = pickle.dumps(state)
        redis_client.setex(f"session:{session_id}", 3600, data)
    
    def load_session(self, session_id: str) -> Optional[ConversationState]:
        """加载会话"""
        data = redis_client.get(f"session:{session_id}")
        if data:
            return pickle.loads(data)
        return None
```

#### 3.3 添加流式输出

**需求**：逐字显示回复，提升用户体验

**实现**：

```python
async def stream_chat(message: str):
    """流式对话"""
    async for chunk in llm.astream(message):
        yield chunk.content
        
# 使用
async for text in stream_chat("你好"):
    print(text, end="", flush=True)
```

#### 3.4 多模态支持

**扩展**：支持图片、语音输入

```python
# 图片理解
from langchain.schema.messages import HumanMessage

message = HumanMessage(
    content=[
        {"type": "text", "text": "这是什么产品？"},
        {"type": "image_url", "image_url": {"url": image_url}}
    ]
)

response = llm.invoke([message])
```

### 阶段4: 生产部署（7-10天）

#### 4.1 性能优化

**瓶颈分析**：

```python
import time

def profile_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@profile_function
def classify_intent(state):
    # 测量意图分类耗时
    pass
```

**优化策略**：
1. **模型量化**：减少内存和推理时间
2. **批处理**：同时处理多个请求
3. **缓存**：常见问题缓存结果
4. **异步**：非阻塞I/O操作

#### 4.2 监控告警

**指标收集**：

```python
from prometheus_client import Counter, Histogram

# 请求计数
requests = Counter('requests_total', 'Total requests', ['status'])
requests.labels(status='success').inc()

# 响应时间
latency = Histogram('request_duration_seconds', 'Request latency')
with latency.time():
    process_request()
```

**告警规则**：
- 错误率 > 5%
- 响应时间 > 10s
- 内存使用 > 80%

#### 4.3 A/B测试

**对比不同策略**：

```python
import random

def get_agent(user_id: str):
    """根据用户分流"""
    if hash(user_id) % 2 == 0:
        # 实验组：新版本
        return AgentV2()
    else:
        # 对照组：旧版本
        return AgentV1()
```

---

## 💡 核心概念解析

### 1. 什么是LangGraph？

**传统方式**：
```python
# 线性流程
intent = classify(message)
if intent == "order":
    result = query_order()
response = generate(result)
```

**LangGraph方式**：
```python
# 图结构，支持条件分支、循环
graph = StateGraph(State)
graph.add_node("classify", classify_fn)
graph.add_conditional_edges("classify", router, {
    "order": "query_order",
    "product": "search_knowledge"
})
```

**优势**：
- 可视化流程
- 灵活的路由
- 易于调试
- 状态可追溯

### 2. 什么是RAG？

**定义**：Retrieval-Augmented Generation（检索增强生成）

**流程**：
```
用户问题 
  → 检索相关知识 
  → 注入到Prompt 
  → LLM基于知识回答
```

**为什么需要RAG？**
- LLM的知识有限（训练数据截止日期）
- 私有知识LLM不知道（公司产品、内部政策）
- 减少幻觉（基于事实回答）

**实现要点**：
1. 高质量的知识库
2. 准确的检索（相似度）
3. 合理的Prompt设计

### 3. Function Calling是什么？

**概念**：让LLM调用外部函数获取信息或执行操作

**流程**：
```
用户："查订单ORD001"
  → LLM识别需要调用工具
  → 提取参数：order_id="ORD001"
  → 调用：query_order("ORD001")
  → 获取结果：{"status": "已发货"}
  → LLM生成回复："您的订单已发货"
```

**应用场景**：
- 数据库查询
- API调用
- 文件操作
- 系统命令

### 4. Prompt Engineering技巧

**好的Prompt特征**：

1. **清晰的角色定位**
   ```
   你是专业的客服代表，代表XX公司为客户服务。
   ```

2. **明确的任务说明**
   ```
   请基于以下知识回答用户问题，如果知识库中没有，
   请诚实地告知用户。
   ```

3. **结构化的输出要求**
   ```
   请以JSON格式返回：
   {
       "intent": "...",
       "entities": {...}
   }
   ```

4. **相关的上下文**
   ```
   对话历史：
   用户：...
   客服：...
   
   当前问题：...
   ```

---

## 🔧 常见问题排查

### Q1: 知识库检索不准确

**排查步骤**：
1. 检查嵌入模型是否适合中文
2. 调整top_k数量
3. 查看检索结果的相似度分数
4. 优化知识文档的质量

**解决方案**：
```python
# 1. 使用更好的嵌入模型
kb = KnowledgeBase(embedding_model="BAAI/bge-large-zh-v1.5")

# 2. 增加检索结果数量
results = kb.search(query, top_k=5)

# 3. 过滤低相似度结果
results = [r for r in results if r['score'] < 0.5]
```

### Q2: LLM回复不稳定

**原因**：温度参数太高导致随机性强

**解决方案**：
```python
llm = LLMClient(temperature=0.3)  # 降低温度
```

### Q3: 意图识别错误

**原因**：Prompt不够明确或示例不足

**解决方案**：
```python
# 添加更多示例
prompt = f"""
意图类型：
- order_query: 订单查询（关键词：订单、快递、物流）
- refund_request: 退款申请（关键词：退款、退货、不想要）
...

示例：
用户：我的订单到哪了？
意图：order_query

用户：我要退货
意图：refund_request

用户：{user_message}
意图：
"""
```

### Q4: 内存占用过高

**排查**：
```python
import psutil
process = psutil.Process()
print(f"内存使用: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

**解决方案**：
1. 减少会话缓存数量
2. 定期清理历史消息
3. 使用更小的嵌入模型
4. 实现分页加载

---

## 🎯 项目扩展建议

### 初级扩展

1. **添加新的业务工具**
   - 优惠券查询
   - 积分查询
   - 地址管理

2. **丰富知识库**
   - 添加更多产品信息
   - 补充FAQ
   - 行业知识

3. **优化用户体验**
   - 添加欢迎语
   - 提供快捷回复
   - 显示打字动画

### 中级扩展

1. **多渠道接入**
   - 微信公众号
   - 企业微信
   - 钉钉机器人

2. **数据分析**
   - 用户行为统计
   - 热门问题分析
   - 满意度评分

3. **智能推荐**
   - 相关问题推荐
   - 商品推荐
   - 服务推荐

### 高级扩展

1. **强化学习优化**
   - 基于反馈优化回复
   - 对话策略学习
   - 个性化推荐

2. **多模态交互**
   - 语音识别与合成
   - 图片理解
   - 视频客服

3. **知识图谱集成**
   - 构建实体关系
   - 推理能力增强
   - 复杂查询支持

---

## 📖 推荐阅读

### 入门资料
- [LangChain官方教程](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph快速开始](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [提示工程指南](https://www.promptingguide.ai/zh)

### 进阶资料
- [RAG技术详解](https://arxiv.org/abs/2005.11401)
- [向量数据库对比](https://github.com/erikbern/ann-benchmarks)
- [大模型应用实践](https://github.com/datawhalechina/llm-cookbook)

### 最佳实践
- [生产级LLM应用](https://github.com/jerryjliu/llama_index)
- [AI Agent设计模式](https://www.deeplearning.ai/short-courses/)
- [Prompt工程技巧](https://github.com/dair-ai/Prompt-Engineering-Guide)

---

## 🤝 学习交流

### 建议学习节奏

- **第1周**：运行示例，理解基本概念
- **第2周**：修改代码，添加简单功能
- **第3周**：实现完整的新特性
- **第4周**：性能优化和部署实践

### 实践项目建议

选择一个实际场景练习：
1. **学校咨询系统**：招生、课程、宿舍等
2. **餐厅点餐助手**：菜单查询、下单、配送
3. **健康咨询机器人**：症状分析、建议、预约
4. **旅游规划助手**：景点推荐、路线规划、酒店预订

---

**学习贵在坚持，祝你学习愉快！** 🎉

