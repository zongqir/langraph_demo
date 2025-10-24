"""
高级演示
展示完整的客服功能：知识库检索、工具调用、多轮对话
"""
import sys
from pathlib import Path
import json

# 开发调试：添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.utils import log


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def run_test_case(agent: CustomerServiceAgent, query: str, state = None):
    """运行测试用例"""
    print(f"👤 用户: {query}")
    
    try:
        response, state = agent.chat(query, state)
        print(f"\n🤖 客服: {response}")
        
        # 显示详细信息（state 现在是字典）
        print(f"\n📊 详细信息:")
        print(f"   - 意图: {state.get('intent')}")
        print(f"   - 实体: {json.dumps(state.get('entities', {}), ensure_ascii=False)}")
        
        tool_calls = state.get('tool_calls', [])
        if tool_calls:
            print(f"   - 工具调用: {len(tool_calls)} �?)
            latest_call = tool_calls[-1]
            print(f"   - 最新结�? {latest_call['result'].get('message', 'N/A')}")
        
        retrieved_docs = state.get('retrieved_docs', [])
        if retrieved_docs:
            print(f"   - 检索文�? {len(retrieved_docs)} �?)
        
        print(f"   - 状�? {state.get('status')}")
        
        if state.get('requires_human'):
            print("   ⚠️  需要人工介�?)
        
        return state
        
    except Exception as e:
        log.error(f"测试用例执行失败: {e}", exc_info=True)
        print(f"�?错误: {e}")
        return state


def main():
    """运行高级演示"""
    
    print_section("智能客服系统 - 高级功能演示")
    
    # 初始化知识库
    log.info("加载知识�?..")
    kb = KnowledgeBase()
    if not kb.load():
        print("⚠️  警告: 知识库未找到，请先运�?init_knowledge_base.py")
        print("知识检索功能将不可用，但工具调用仍可正常工作\n")
        kb = None
    else:
        print("�?知识库加载成功\n")
    
    # 创建客服Agent
    agent = CustomerServiceAgent(knowledge_base=kb)
    
    # ========== 场景1: 产品咨询（知识库检索） ==========
    print_section("场景1: 产品咨询 - 知识库检�?)
    
    state = None
    state = run_test_case(agent, "iPhone 15 Pro有什么特点？多少钱？", state)
    
    # ========== 场景2: 订单查询（工具调用） ==========
    print_section("场景2: 订单查询 - 工具调用")
    
    state = None  # 新会�?
    state = run_test_case(agent, "帮我查一下订单ORD001的状�?, state)
    
    # ========== 场景3: 物流跟踪（工具调用） ==========
    print_section("场景3: 物流跟踪 - 工具调用")
    
    # 继续上一个会�?
    state = run_test_case(agent, "物流单号是多少？帮我查一下物�?, state)
    
    # ========== 场景4: 退款申请（工具调用�?==========
    print_section("场景4: 退款申�?- 工具调用")
    
    state = None  # 新会�?
    state = run_test_case(agent, "我要退订单ORD002，商品有质量问题", state)
    
    # ========== 场景5: 库存查询（工具调用） ==========
    print_section("场景5: 库存查询 - 工具调用")
    
    state = None
    state = run_test_case(agent, "MacBook Pro还有货吗�?, state)
    
    # ========== 场景6: 多轮对话 ==========
    print_section("场景6: 多轮对话 - 上下文理�?)
    
    state = None
    state = run_test_case(agent, "我想买AirPods", state)
    state = run_test_case(agent, "有什么型号？", state)
    state = run_test_case(agent, "Pro版本怎么样？", state)
    
    # ========== 场景7: 常见问题 ==========
    if kb is not None:
        print_section("场景7: 常见问题 - 知识库检�?)
        
        state = None
        state = run_test_case(agent, "你们的退换货政策是什么？", state)
        state = run_test_case(agent, "配送要多久�?, state)
    
    # ========== 场景8: 转人�?==========
    print_section("场景8: 复杂问题 - 转人工客�?)
    
    state = None
    state = run_test_case(agent, "我要投诉！让你们经理来！", state)
    
    print_section("演示完成")
    print("以上展示了智能客服系统的核心功能�?)
    print("�?知识库检索（RAG�?)
    print("�?工具调用（订单、物流、退款、库存）")
    print("�?多轮对话与上下文理解")
    print("�?意图识别与实体提�?)
    print("�?智能转人�?)
    print()


if __name__ == "__main__":
    main()

