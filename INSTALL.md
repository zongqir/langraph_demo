# 安装指南

## 标准安装方式

本项目采用标准的 Python 包结构，支持多种安装方式。

### 方式 1：开发模式安装（推荐用于开发）

```bash
# 在项目根目录下
pip install -e .
```

这样安装后，你可以在任何地方直接导入：

```python
from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase
```

### 方式 2：标准安装

```bash
pip install .
```

### 方式 3：从 requirements.txt 安装依赖

```bash
pip install -r requirements.txt
```

然后直接运行（不需要 sys.path.insert）：

```bash
python examples/simple_chat.py
```

## 项目结构说明

```
langraph_demo/
├── langraph_customer_service/    # ✅ 真正的包名（不是 src！）
│   ├── __init__.py              # 导出主要组件
│   ├── agents/                  # Agent 模块
│   ├── knowledge_base/          # 知识库模块
│   ├── tools/                   # 工具模块
│   ├── state.py                 # 状态定义
│   ├── llm_client.py           # LLM 客户端
│   └── utils.py                # 工具函数
├── examples/                    # 示例代码
├── config/                      # 配置模块
├── setup.py                     # 安装配置
├── pyproject.toml              # 现代 Python 项目配置
└── requirements.txt            # 依赖列表
```

## 为什么不用 `src` 作为包名？

- ✅ `langraph_customer_service` 是**包名**（有业务含义）
- ❌ `src` 只是**布局目录**（不是包名）

符合 Python 社区最佳实践：
- https://packaging.python.org/
- https://py-pkgs.org/
- PEP 517, PEP 518

## 安装后使用

安装后，所有导入都是标准的：

```python
# ✅ 正确的导入方式
from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase

# ❌ 不需要这样的 hack
import sys
sys.path.insert(0, ...)
```


