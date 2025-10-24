"""
状态管理模块
定义对话状态和消息结构
"""
from typing import List, Dict, Any, Optional, Literal, TypedDict, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
import operator


class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system"] = Field(description="消息角色")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ConversationState(TypedDict, total=False):
    """对话状态模型 - 使用 TypedDict 以兼容 LangGraph"""
    
    # 对话历史 - 使用 operator.add 来追加消息
    messages: Annotated[List[Message], operator.add]
    
    # 用户信息
    user_id: Optional[str]
    session_id: str
    
    # 意图和实体
    intent: Optional[str]
    entities: Dict[str, Any]
    
    # 业务上下文
    context: Dict[str, Any]
    
    # 工具调用记录 - 使用 operator.add 来追加工具调用
    tool_calls: Annotated[List[Dict[str, Any]], operator.add]
    
    # 检索结果
    retrieved_docs: List[str]
    
    # 当前回复
    current_response: str
    
    # 是否需要人工介入
    requires_human: bool
    
    # 对话状态
    status: Literal["active", "waiting", "completed", "escalated"]

