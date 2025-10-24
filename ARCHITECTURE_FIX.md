# 项目架构修复说明

## ✅ 修复内容

### 1. 包结构修正

**问题**：使用 `src` 作为包名是错误的！
- ❌ 旧版本：`from src.agents import ...`  
- ✅ 新版本：`from langraph_customer_service.agents import ...`

**修改**：
```bash
# 目录重命名
src/ → langraph_customer_service/
```

### 2. 符合 Python 最佳实践

参考标准：
- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 517](https://peps.python.org/pep-0517/) - Build System
- [PEP 518](https://peps.python.org/pep-0518/) - pyproject.toml

### 3. 项目结构（正确版本）

```
langraph_demo/                          # 项目根目录
├── langraph_customer_service/          # ✅ 真正的包名（有业务含义）
│   ├── __init__.py                     # 导出主要组件
│   ├── agents/                         # Agent 模块
│   │   ├── __init__.py
│   │   └── customer_service.py
│   ├── knowledge_base/                 # 知识库模块
│   │   ├── __init__.py
│   │   └── vector_store.py
│   ├── tools/                          # 工具模块
│   │   ├── __init__.py
│   │   └── business_tools.py
│   ├── state.py                        # 状态定义（TypedDict for LangGraph）
│   ├── llm_client.py                   # LLM 客户端
│   └── utils.py                        # 工具函数
├── config/                             # 配置模块
│   ├── __init__.py
│   └── settings.py
├── examples/                           # 示例代码
│   ├── simple_chat.py
│   ├── advanced_demo.py
│   └── init_knowledge_base.py
├── api/                                # API 服务
│   ├── __init__.py
│   └── main.py
├── tests/                              # 测试（待添加）
├── data/                               # 数据目录
├── models/                             # 模型文件
├── logs/                               # 日志目录
├── setup.py                            # 安装配置
├── pyproject.toml                      # 现代 Python 项目配置
├── requirements.txt                    # 依赖列表
├── config.env                          # 环境变量
└── README.md                           # 项目说明
```

### 4. 关键修改点

#### 4.1 所有导入语句更新

```python
# ❌ 旧版本
from src.agents import CustomerServiceAgent
from src.knowledge_base import KnowledgeBase
from src.utils import log

# ✅ 新版本
from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.utils import log
```

#### 4.2 移除 sys.path hack

```python
# ❌ 旧版本 - 不专业的做法
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ✅ 新版本 - 直接导入
from langraph_customer_service.agents import CustomerServiceAgent
```

#### 4.3 使用相对导入（包内部）

`langraph_customer_service/__init__.py`:
```python
# ✅ 包的主入口，使用相对导入
from .agents import CustomerServiceAgent
from .knowledge_base import KnowledgeBase
from .state import ConversationState, Message
from .llm_client import llm_client
```

`langraph_customer_service/agents/__init__.py`:
```python
# ✅ 子模块内使用相对导入
from .customer_service import CustomerServiceAgent
```

### 5. LangGraph 状态管理修复

**问题**：LangGraph 0.2.45 要求使用 TypedDict，不能用 Pydantic BaseModel

**修改** (`langraph_customer_service/state.py`):
```python
# ❌ 旧版本
class ConversationState(BaseModel):
    messages: List[Message] = Field(...)

# ✅ 新版本
from typing import TypedDict, Annotated
import operator

class ConversationState(TypedDict, total=False):
    messages: Annotated[List[Message], operator.add]  # 自动追加
    tool_calls: Annotated[List[Dict], operator.add]   # 自动追加
```

### 6. 安装与使用

#### 开发模式安装（推荐）

```bash
# 在项目根目录
pip install -e .
```

#### 运行示例

```bash
# 不需要激活虚拟环境的情况下
python examples/simple_chat.py

# 或使用虚拟环境
venv\Scripts\python.exe examples/simple_chat.py
```

### 7. 为什么这样做？

#### ❌ `src` 作为包名的问题：
1. `src` 没有业务含义
2. 不符合 Python 命名规范
3. 导入语句不清晰：`from src.xxx` 看不出是什么项目

#### ✅ `langraph_customer_service` 的优势：
1. 有明确的业务含义
2. 符合 Python 社区规范
3. 可以发布到 PyPI
4. 导入语句清晰：`from langraph_customer_service.agents import ...`

### 8. 参考资料

- [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🎯 总结

修复后的项目符合：
- ✅ Python 社区最佳实践
- ✅ PEP 517/518 标准
- ✅ LangGraph 状态管理要求
- ✅ 清晰的模块结构
- ✅ 无需 `sys.path` hack
- ✅ 可安装、可发布的标准包

