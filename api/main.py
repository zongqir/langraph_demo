"""
FastAPI REST API服务
提供HTTP接口供外部调用
"""
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.state import ConversationState
from langraph_customer_service.utils import log
from config import settings


# 请求/响应模型
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="客服回复")
    session_id: str = Field(..., description="会话ID")
    intent: Optional[str] = Field(None, description="识别的意图")
    requires_human: bool = Field(False, description="是否需要人工")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]


# 创建FastAPI应用
app = FastAPI(
    title="智能客服系统 API",
    description="基于LangGraph的生产级智能客服系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量：存储Agent和会话状态
agent: Optional[CustomerServiceAgent] = None
sessions: Dict[str, ConversationState] = {}


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global agent
    
    log.info("初始化智能客服API服务...")
    
    try:
        # 加载知识库
        kb = KnowledgeBase()
        if kb.load():
            log.info("知识库加载成功")
        else:
            log.warning("知识库未找到，使用无知识库模式")
            kb = None
        
        # 创建Agent
        agent = CustomerServiceAgent(knowledge_base=kb)
        log.info("智能客服Agent初始化完成")
        
    except Exception as e:
        log.error(f"初始化失败: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    log.info("关闭智能客服API服务...")
    sessions.clear()


@app.get("/", tags=["系统"])
async def root():
    """根路由"""
    return {
        "name": "智能客服系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查"""
    services = {
        "agent": agent is not None,
        "knowledge_base": agent.knowledge_base is not None if agent else False
    }
    
    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        services=services
    )


@app.post("/chat", response_model=ChatResponse, tags=["对话"])
async def chat(request: ChatRequest):
    """
    处理用户消息并返回客服回复
    
    Args:
        request: 聊天请求
    
    Returns:
        ChatResponse: 客服回复
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="服务未就绪")
    
    try:
        # 获取或创建会话状态
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        state = sessions.get(session_id)
        
        # 如果是新会话，创建状态
        if state is None:
            state = ConversationState(
                session_id=session_id,
                user_id=request.user_id
            )
        
        # 处理对话
        log.info(f"处理消息: session_id={session_id}, message={request.message[:50]}...")
        response_text, updated_state = agent.chat(request.message, state)
        
        # 更新会话缓存
        sessions[session_id] = updated_state
        
        # 清理过期会话（保留最近100个）
        if len(sessions) > 100:
            oldest_keys = sorted(sessions.keys())[:50]
            for key in oldest_keys:
                del sessions[key]
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            intent=updated_state.intent,
            requires_human=updated_state.requires_human
        )
        
    except Exception as e:
        log.error(f"处理对话时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.delete("/session/{session_id}", tags=["会话"])
async def delete_session(session_id: str):
    """
    删除会话
    
    Args:
        session_id: 会话ID
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"会话 {session_id} 已删除"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@app.get("/session/{session_id}", tags=["会话"])
async def get_session(session_id: str):
    """
    获取会话信息
    
    Args:
        session_id: 会话ID
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    state = sessions[session_id]
    
    return {
        "session_id": session_id,
        "user_id": state.user_id,
        "message_count": len(state.messages),
        "intent": state.intent,
        "status": state.status,
        "requires_human": state.requires_human,
        "recent_messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in state.get_recent_messages(5)
        ]
    }


@app.get("/stats", tags=["统计"])
async def get_stats():
    """获取系统统计信息"""
    return {
        "active_sessions": len(sessions),
        "total_messages": sum(len(s.messages) for s in sessions.values()),
        "agent_status": "active" if agent else "inactive",
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    log.error(f"未捕获的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            "type": type(exc).__name__
        }
    )


def main():
    """启动API服务"""
    log.info(f"启动API服务: http://0.0.0.0:8000")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，生产环境应设为False
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()

