"""
快速启动脚�?
一键初始化并测试系�?
"""
# 导入所有依赖（缺少依赖会直接报错，这是正确的行为）
import langgraph
import langchain
import faiss
import sentence_transformers

from langraph_customer_service.utils import log
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.agents import CustomerServiceAgent


def init_knowledge_base():
    """初始化知识库"""
    log.info("\n初始化知识库...")
    
    kb = KnowledgeBase()
    
    # 检查是否已存在
    if kb.load():
        log.info("�?知识库已存在，跳过初始化")
        return kb
    
    log.info("创建新知识库...")
    
    # 添加示例文档
    docs = [
        """iPhone 15 Pro产品信息�?
        - 价格�?999元起
        - 屏幕�?.1英寸超视网膜XDR
        - 芯片：A17 Pro
        - 存储�?28GB/256GB/512GB/1TB
        """,
        """退换货政策�?
        - 7天无理由退�?
        - 15天质量问题换�?
        - 1年保修服�?
        - 退�?-5工作日到�?
        """,
        """配送说明：
        - 1-3个工作日发货
        - 3-7天送达
        - 支持顺丰、京东物�?
        - 部分地区支持当日�?
        """
    ]
    
    kb.add_documents(docs)
    kb.save()
    
    log.info("�?知识库初始化完成")
    return kb


def run_quick_test(kb):
    """运行快速测�?""
    log.info("\n运行快速测�?..")
    
    agent = CustomerServiceAgent(knowledge_base=kb)
    
    test_cases = [
        "iPhone 15 Pro多少钱？",
        "帮我查订单ORD001",
        "怎么退货？"
    ]
    
    print("\n" + "="*60)
    print("开始测试对话功�?)
    print("="*60 + "\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"【测�?{i}�?)
        print(f"👤 用户: {query}")
        
        try:
            response, state = agent.chat(query)
            print(f"🤖 客服: {response}")
            print(f"📊 意图: {state.intent}")
            print()
        except Exception as e:
            log.error(f"测试失败: {e}")
            print(f"�?错误: {e}\n")
    
    print("="*60)
    log.info("�?快速测试完�?)


def main():
    """主函�?""
    print("""
╔══════════════════════════════════════════════════════════╗
�?                                                         �?
�?     🤖 智能客服系统 - LangGraph实战项目                  �?
�?                                                         �?
�?     快速启动脚�?                                        �?
�?                                                         �?
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 1. 初始化知识库
    try:
        kb = init_knowledge_base()
    except Exception as e:
        log.error(f"知识库初始化失败: {e}")
        log.info("正在使用无知识库模式...")
        kb = None
    
    # 2. 运行测试
    try:
        run_quick_test(kb)
    except Exception as e:
        log.error(f"测试运行失败: {e}", exc_info=True)
        return
    
    # 3. 提示下一�?
    print("\n" + "="*60)
    print("🎉 系统启动成功�?)
    print("="*60)
    print("\n接下来你可以�?)
    print("\n1. 运行交互式对话：")
    print("   python examples/simple_chat.py")
    print("\n2. 查看完整功能演示�?)
    print("   python examples/advanced_demo.py")
    print("\n3. 初始化完整知识库�?)
    print("   python examples/init_knowledge_base.py")
    print("\n4. 查看详细文档�?)
    print("   打开 README.md")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

