"""
智能客服Agent
基于LangGraph实现的多轮对话客服系统
"""
from typing import Dict, Any, List, Optional, Literal
import json
import re
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from langraph_customer_service.state import ConversationState, Message
from langraph_customer_service.llm_client import llm_client
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.tools import query_order, process_refund, check_inventory, get_logistics_info
from config import settings
from langraph_customer_service.utils import log


class CustomerServiceAgent:
    """智能客服Agent"""
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """
        初始化客服Agent
        
        Args:
            knowledge_base: 知识库实例
        """
        self.knowledge_base = knowledge_base
        self.graph = self._build_graph()
        
        # 工具映射
        self.tools = {
            "query_order": query_order,
            "process_refund": process_refund,
            "check_inventory": check_inventory,
            "get_logistics_info": get_logistics_info
        }
        
        log.info("智能客服Agent初始化完成")
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph工作流"""
        
        # 创建状态图
        workflow = StateGraph(ConversationState)
        
        # 添加节点
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge)
        workflow.add_node("call_tools", self._call_tools)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("check_satisfaction", self._check_satisfaction)
        
        # 设置入口点
        workflow.set_entry_point("classify_intent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_after_intent,
            {
                "knowledge": "retrieve_knowledge",
                "tool": "call_tools",
                "general": "generate_response"
            }
        )
        
        # 知识检索后生成回复
        workflow.add_edge("retrieve_knowledge", "generate_response")
        
        # 工具调用后生成回复
        workflow.add_edge("call_tools", "generate_response")
        
        # 生成回复后检查满意度
        workflow.add_edge("generate_response", "check_satisfaction")
        
        # 条件结束
        workflow.add_conditional_edges(
            "check_satisfaction",
            self._should_continue,
            {
                "continue": END,
                "escalate": END
            }
        )
        
        return workflow.compile()
    
    def _classify_intent(self, state: ConversationState) -> Dict[str, Any]:
        """
        意图分类节点
        识别用户意图并提取实体
        """
        log.info("执行意图分类")
        
        # 获取最新用户消息
        messages = state.get("messages", [])
        user_message = messages[-1].content if messages else ""
        
        # 构造意图分类prompt
        recent_messages = messages[-3:] if len(messages) > 3 else messages
        prompt = f"""你是一个专业的客服意图分类器。请分析用户的问题，识别意图和提取关键实体。

对话历史：
{self._format_history(recent_messages)}

当前用户问题：{user_message}

请识别以下意图类型：
1. order_query - 订单查询（包含订单号）
2. refund_request - 退款申请（包含订单号和退款原因）
3. inventory_check - 库存查询（包含商品名称）
4. logistics_query - 物流查询（包含物流单号）
5. product_info - 产品咨询（通用产品信息）
6. general_chat - 一般聊天

请以JSON格式返回：
{{
    "intent": "意图类型",
    "entities": {{
        "order_id": "订单号（如适用）",
        "product_name": "商品名称（如适用）",
        "tracking_number": "物流单号（如适用）",
        "reason": "退款原因（如适用）"
    }},
    "confidence": 0.95,
    "needs_tool": true/false,
    "needs_knowledge": true/false
}}
"""
        
        response = llm_client.invoke([
            {"role": "system", "content": "你是一个专业的意图分类器，只返回JSON格式的结果。"},
            {"role": "user", "content": prompt}
        ])
        
        try:
            # 解析意图
            result = self._extract_json(response)
            intent = result.get("intent", "general_chat")
            entities = result.get("entities", {})
            
            # 获取或初始化 context
            context = dict(state.get("context", {}))
            context["needs_tool"] = result.get("needs_tool", False)
            context["needs_knowledge"] = result.get("needs_knowledge", False)
            
            log.info(f"意图识别: {intent}, 实体: {entities}")
            
            return {
                "intent": intent,
                "entities": entities,
                "context": context
            }
            
        except Exception as e:
            log.error(f"意图分类失败: {e}")
            return {
                "intent": "general_chat",
                "entities": {},
                "context": {"needs_tool": False, "needs_knowledge": False}
            }
    
    def _retrieve_knowledge(self, state: ConversationState) -> Dict[str, Any]:
        """
        知识检索节点
        从知识库检索相关信息
        """
        log.info("执行知识检索")
        
        if self.knowledge_base is None:
            log.warning("知识库未初始化")
            return {"retrieved_docs": []}
        
        messages = state.get("messages", [])
        user_message = messages[-1].content if messages else ""
        
        # 检索相关文档
        results = self.knowledge_base.search(user_message, top_k=3)
        
        if results:
            retrieved_docs = [r["document"] for r in results]
            log.info(f"检索到 {len(results)} 条相关文档")
            return {"retrieved_docs": retrieved_docs}
        else:
            log.info("未检索到相关文档")
            return {"retrieved_docs": []}
    
    def _call_tools(self, state: ConversationState) -> Dict[str, Any]:
        """
        工具调用节点
        根据意图调用相应的业务工具
        """
        intent = state.get("intent")
        entities = state.get("entities", {})
        tool_calls = state.get("tool_calls", [])
        log.info(f"执行工具调用: intent={intent}")
        
        tool_result = None
        
        try:
            if intent == "order_query":
                order_id = entities.get("order_id")
                if order_id:
                    tool_result = query_order(order_id)
                
            elif intent == "refund_request":
                order_id = entities.get("order_id")
                reason = entities.get("reason", "用户申请退款")
                if order_id:
                    tool_result = process_refund(order_id, reason)
            
            elif intent == "inventory_check":
                product_name = entities.get("product_name")
                if product_name:
                    tool_result = check_inventory(product_name)
            
            elif intent == "logistics_query":
                tracking_number = entities.get("tracking_number")
                
                # 如果当前没有物流单号，尝试从上一次订单查询中获取
                if not tracking_number and tool_calls:
                    for call in reversed(tool_calls):
                        if call.get("intent") == "order_query":
                            result = call.get("result", {})
                            if result.get("success"):
                                data = result.get("data", {})
                                tracking_number = data.get("tracking_number")
                                if tracking_number:
                                    log.info(f"从上下文中获取物流单号: {tracking_number}")
                                    break
                
                if tracking_number:
                    tool_result = get_logistics_info(tracking_number)
            
            if tool_result:
                # 使用 operator.add，直接返回新的工具调用，会自动追加
                new_tool_call = {
                    "intent": intent,
                    "result": tool_result,
                    "timestamp": datetime.now().isoformat()
                }
                log.info(f"工具调用成功: {intent}")
                return {"tool_calls": [new_tool_call]}
            else:
                log.warning(f"工具调用失败: 缺少必要参数")
                # 返回一个错误信息的工具调用记录，而不是空字典
                error_call = {
                    "intent": intent,
                    "result": {
                        "success": False,
                        "message": f"缺少必要参数，无法执行{intent}操作",
                        "data": None
                    },
                    "timestamp": datetime.now().isoformat()
                }
                return {"tool_calls": [error_call]}
                
        except Exception as e:
            log.error(f"工具调用异常: {e}")
            # 返回异常信息，而不是空字典
            error_call = {
                "intent": intent,
                "result": {
                    "success": False,
                    "message": f"工具调用异常: {str(e)}",
                    "data": None
                },
                "timestamp": datetime.now().isoformat()
            }
            return {"tool_calls": [error_call]}
    
    def _generate_response(self, state: ConversationState) -> Dict[str, Any]:
        """
        生成回复节点
        基于上下文生成自然语言回复
        """
        log.info("生成回复")
        
        messages = state.get("messages", [])
        tool_calls = state.get("tool_calls", [])
        retrieved_docs = state.get("retrieved_docs", [])
        intent = state.get("intent", "general_chat")
        
        user_message = messages[-1].content
        
        # 构建上下文
        context_parts = []
        
        # 添加工具调用结果
        if tool_calls:
            latest_tool_call = tool_calls[-1]
            context_parts.append(f"工具调用结果：\n{json.dumps(latest_tool_call['result'], ensure_ascii=False, indent=2)}")
        
        # 添加检索到的知识
        if retrieved_docs:
            context_parts.append(f"相关知识：\n" + "\n".join(retrieved_docs))
        
        context = "\n\n".join(context_parts) if context_parts else "无额外上下文"
        
        # 构建系统提示
        system_prompt = f"""你是{settings.customer_service_name}，代表{settings.company_name}为客户提供专业、友好的服务。

服务准则：
1. 保持礼貌、专业、耐心
2. 基于提供的上下文和工具结果回答问题
3. 如果信息不足，主动询问用户提供更多细节
4. 对于无法处理的复杂问题，建议转人工客服
5. 回复要简洁明了，条理清晰

当前用户意图：{intent}
"""
        
        # 构建对话历史
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        history = self._format_history(recent_messages)
        
        # 生成回复
        prompt = f"""对话历史：
{history}

上下文信息：
{context}

用户最新问题：{user_message}

请生成专业、友好的回复："""
        
        response = llm_client.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        # 创建新消息 - 使用 operator.add，messages 会自动追加
        new_message = Message(role="assistant", content=response)
        
        log.info(f"回复生成完成: {len(response)} 字符")
        
        return {
            "current_response": response,
            "messages": [new_message]  # 会自动追加到现有消息列表
        }
    
    def _check_satisfaction(self, state: ConversationState) -> Dict[str, Any]:
        """
        满意度检查节点
        判断是否需要转人工
        """
        log.info("检查满意度")
        
        messages = state.get("messages", [])
        # 简单逻辑：检查是否有明确的负面情绪或要求人工
        user_message = messages[-2].content if len(messages) >= 2 else ""
        
        negative_keywords = ["人工", "转人工", "不满意", "投诉", "经理"]
        
        if any(keyword in user_message for keyword in negative_keywords):
            log.info("检测到需要人工介入")
            return {
                "requires_human": True,
                "status": "escalated"
            }
        else:
            return {"status": "completed"}
    
    def _route_after_intent(self, state: ConversationState) -> Literal["knowledge", "tool", "general"]:
        """意图分类后的路由决策"""
        context = state.get("context", {})
        if context.get("needs_tool"):
            return "tool"
        elif context.get("needs_knowledge"):
            return "knowledge"
        else:
            return "general"
    
    def _should_continue(self, state: ConversationState) -> Literal["continue", "escalate"]:
        """判断是否继续对话"""
        if state.get("requires_human", False):
            return "escalate"
        return "continue"
    
    def _format_history(self, messages: List[Message]) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in messages:
            role_name = "用户" if msg.role == "user" else "客服"
            formatted.append(f"{role_name}: {msg.content}")
        return "\n".join(formatted)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        从LLM响应中提取JSON
        处理可能的markdown代码块包裹
        """
        # 尝试提取代码块中的JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 尝试提取大括号内容
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        raise ValueError("无法从响应中提取JSON")
    
    def chat(self, user_input: str, state: Optional[Dict[str, Any]] = None) -> tuple[str, Dict[str, Any]]:
        """
        处理用户输入并返回回复
        
        Args:
            user_input: 用户输入
            state: 对话状态（可选，如果是新对话则为None）
        
        Returns:
            (回复文本, 更新后的状态)
        """
        # 创建或更新状态
        if state is None:
            state = {
                "session_id": f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "messages": [],
                "intent": None,
                "entities": {},
                "context": {},
                "tool_calls": [],
                "retrieved_docs": [],
                "current_response": "",
                "requires_human": False,
                "status": "active"
            }
        
        # 创建新的用户消息 - 使用 operator.add，会自动追加
        user_message = Message(role="user", content=user_input)
        
        # 准备输入状态 - 添加用户消息
        input_state = dict(state)
        input_state["messages"] = [user_message]  # 会自动追加到现有消息
        
        # 执行工作流
        result_state = self.graph.invoke(input_state)
        
        # LangGraph 返回的是字典
        response = result_state.get("current_response", "")
        
        return response, result_state
