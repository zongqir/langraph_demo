"""
状态管理模块
定义对话状态和消息结构
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system"] = Field(description="消息角色")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ConversationState(BaseModel):
    """对话状态模型"""
    
    # 对话历史
    messages: List[Message] = Field(default_factory=list, description="对话消息列表")
    
    # 用户信息
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: str = Field(description="会话ID")
    
    # 意图和实体
    intent: Optional[str] = Field(default=None, description="当前意图")
    entities: Dict[str, Any] = Field(default_factory=dict, description="提取的实体信息")
    
    # 业务上下文
    context: Dict[str, Any] = Field(default_factory=dict, description="业务上下文")
    
    # 工具调用记录
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用历史")
    
    # 检索结果
    retrieved_docs: List[str] = Field(default_factory=list, description="检索到的文档")
    
    # 当前回复
    current_response: str = Field(default="", description="当前生成的回复")
    
    # 是否需要人工介入
    requires_human: bool = Field(default=False, description="是否需要转人工")
    
    # 对话状态
    status: Literal["active", "waiting", "completed", "escalated"] = Field(
        default="active", 
        description="对话状态"
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_message(self, role: str, content: str, **metadata) -> None:
        """添加消息到历史"""
        self.messages.append(
            Message(role=role, content=content, metadata=metadata)
        )
    
    def get_recent_messages(self, n: int = 5) -> List[Message]:
        """获取最近的n条消息"""
        return self.messages[-n:] if len(self.messages) > n else self.messages
    
    def clear_context(self) -> None:
        """清空临时上下文"""
        self.retrieved_docs = []
        self.current_response = ""

