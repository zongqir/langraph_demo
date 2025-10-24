"""
简单对话示例
演示基本的客服对话功能
"""
import sys
from pathlib import Path

# 开发调试：添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langraph_customer_service.agents import CustomerServiceAgent
from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.utils import log


def main():
    """运行简单对话示例"""

    print("=" * 60)
    print("智能客服系统 - 简单对话示例")
    print("=" * 60)
    print()

    # 初始化知识库
    log.info("加载知识库...")
    kb = KnowledgeBase()
    if not kb.load():
        log.warning("知识库未找到，运行知识库功能前请先执行 init_knowledge_base.py")
        kb = None

    # 创建客服Agent
    log.info("初始化客服Agent...")
    agent = CustomerServiceAgent(knowledge_base=kb)

    # 创建会话状态
    state = None

    print("\n客服已上线！输入 'quit' 或 'exit' 退出\n")

    while True:
        # 获取用户输入
        user_input = input("👤 用户: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("\n感谢使用，再见！\n")
            break

        try:
            # 处理对话
            response, state = agent.chat(user_input, state)

            # 显示回复
            print(f"\n🤖 客服: {response}\n")

            # 显示调试信息（state 现在是字典）
            if state.get("intent"):
                print(f"[调试] 意图: {state['intent']}")
            if state.get("entities"):
                print(f"[调试] 实体: {state['entities']}")
            if state.get("requires_human"):
                print("[系统] 检测到需要人工介入，正在为您转接人工客服...")
            print()

        except Exception as e:
            log.error(f"处理对话时出错: {e}", exc_info=True)
            print(f"\n❌ 抱歉，系统出现错误: {e}\n")


if __name__ == "__main__":
    main()
