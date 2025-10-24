"""
LangGraph智能客服系统
"""
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "基于LangGraph和硅基流动API的生产级智能客服系统"

# 导出主要组件
from .agents import CustomerServiceAgent
from .knowledge_base import KnowledgeBase
from .state import ConversationState, Message
from .llm_client import llm_client
from .tools import query_order, process_refund, check_inventory, get_logistics_info

__all__ = [
    "CustomerServiceAgent",
    "KnowledgeBase", 
    "ConversationState",
    "Message",
    "llm_client",
    "query_order",
    "process_refund",
    "check_inventory",
    "get_logistics_info",
]
