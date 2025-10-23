"""
快速启动脚本
一键初始化并测试系统
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import log


def check_dependencies():
    """检查依赖是否安装"""
    log.info("检查依赖...")
    
    try:
        import langgraph
        import langchain
        import faiss
        import sentence_transformers
        log.info("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        log.error(f"❌ 缺少依赖: {e}")
        log.info("请运行: pip install -r requirements.txt")
        return False


def init_knowledge_base():
    """初始化知识库"""
    log.info("\n初始化知识库...")
    
    from src.knowledge_base import KnowledgeBase
    
    kb = KnowledgeBase()
    
    # 检查是否已存在
    if kb.load():
        log.info("✅ 知识库已存在，跳过初始化")
        return kb
    
    log.info("创建新知识库...")
    
    # 添加示例文档
    docs = [
        """iPhone 15 Pro产品信息：
        - 价格：7999元起
        - 屏幕：6.1英寸超视网膜XDR
        - 芯片：A17 Pro
        - 存储：128GB/256GB/512GB/1TB
        """,
        """退换货政策：
        - 7天无理由退货
        - 15天质量问题换货
        - 1年保修服务
        - 退款3-5工作日到账
        """,
        """配送说明：
        - 1-3个工作日发货
        - 3-7天送达
        - 支持顺丰、京东物流
        - 部分地区支持当日达
        """
    ]
    
    kb.add_documents(docs)
    kb.save()
    
    log.info("✅ 知识库初始化完成")
    return kb


def run_quick_test(kb):
    """运行快速测试"""
    log.info("\n运行快速测试...")
    
    from src.agents import CustomerServiceAgent
    
    agent = CustomerServiceAgent(knowledge_base=kb)
    
    test_cases = [
        "iPhone 15 Pro多少钱？",
        "帮我查订单ORD001",
        "怎么退货？"
    ]
    
    print("\n" + "="*60)
    print("开始测试对话功能")
    print("="*60 + "\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"【测试 {i}】")
        print(f"👤 用户: {query}")
        
        try:
            response, state = agent.chat(query)
            print(f"🤖 客服: {response}")
            print(f"📊 意图: {state.intent}")
            print()
        except Exception as e:
            log.error(f"测试失败: {e}")
            print(f"❌ 错误: {e}\n")
    
    print("="*60)
    log.info("✅ 快速测试完成")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║      🤖 智能客服系统 - LangGraph实战项目                  ║
║                                                          ║
║      快速启动脚本                                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 1. 检查依赖
    if not check_dependencies():
        return
    
    # 2. 初始化知识库
    try:
        kb = init_knowledge_base()
    except Exception as e:
        log.error(f"知识库初始化失败: {e}")
        log.info("正在使用无知识库模式...")
        kb = None
    
    # 3. 运行测试
    try:
        run_quick_test(kb)
    except Exception as e:
        log.error(f"测试运行失败: {e}", exc_info=True)
        return
    
    # 4. 提示下一步
    print("\n" + "="*60)
    print("🎉 系统启动成功！")
    print("="*60)
    print("\n接下来你可以：")
    print("\n1. 运行交互式对话：")
    print("   python examples/simple_chat.py")
    print("\n2. 查看完整功能演示：")
    print("   python examples/advanced_demo.py")
    print("\n3. 初始化完整知识库：")
    print("   python examples/init_knowledge_base.py")
    print("\n4. 查看详细文档：")
    print("   打开 README.md")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

