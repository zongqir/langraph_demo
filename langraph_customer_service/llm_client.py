"""
LLM客户端模块
封装硅基流动API调用
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config import settings
from langraph_customer_service.utils import log


class LLMClient:
    """LLM客户端封装"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化LLM客户端
        
        Args:
            model: 模型名称，默认使用配置中的模型
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大token数
        """
        self.model = model or settings.default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.client = ChatOpenAI(
            model=self.model,
            openai_api_key=settings.siliconflow_api_key,
            openai_api_base=settings.siliconflow_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        log.info(f"初始化LLM客户端: model={self.model}, temperature={temperature}")
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        调用LLM生成回复
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
        
        Returns:
            生成的回复文本
        """
        try:
            # 转换消息格式
            lc_messages = self._convert_messages(messages)
            
            # 调用模型
            response = self.client.invoke(lc_messages, **kwargs)
            
            log.debug(f"LLM调用成功: {len(response.content)} 字符")
            return response.content
            
        except Exception as e:
            log.error(f"LLM调用失败: {e}")
            raise
    
    async def ainvoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """异步调用LLM"""
        try:
            lc_messages = self._convert_messages(messages)
            response = await self.client.ainvoke(lc_messages, **kwargs)
            log.debug(f"LLM异步调用成功: {len(response.content)} 字符")
            return response.content
        except Exception as e:
            log.error(f"LLM异步调用失败: {e}")
            raise
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将字典格式的消息转换为LangChain消息对象"""
        lc_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:  # user
                lc_messages.append(HumanMessage(content=content))
        
        return lc_messages


# 创建全局LLM客户端实例
llm_client = LLMClient()

