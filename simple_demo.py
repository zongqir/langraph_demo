"""
简单的知识库 DEMO
1. 添加一个条目
2. 查询
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langraph_customer_service.knowledge_base import KnowledgeBase

kb = None


def add_and_find():
    # 1. 添加一个条目
    kb.add_document("iPhone 15 Pro 价格是 7999 元起")
    # 2. 查询
    results = kb.search("iPhone 15 Pro 多少钱")
    # 输出结果
    print(f"找到 {len(results)} 条结果：")
    for r in results:
        print(f"- {r['document']}")


def find():
    results = kb.search("iPhone 15 Pro 多少钱")
    # 输出结果
    print(f"找到 {len(results)} 条结果：")
    for r in results:
        print(f"- {r['document']}")


if __name__ == '__main__':
    # 创建知识库
    kb = KnowledgeBase()
    find()

    # add_and_find()
