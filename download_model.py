"""
Download embedding model to local
Use China mirror for faster download
"""
from pathlib import Path
from sentence_transformers import SentenceTransformer

print("="*60)
print("Model Download")
print("="*60)
print("Model: BAAI/bge-large-zh-v1.5")
print("Size: ~1.3GB")
print("Mirror: https://hf-mirror.com")
print("Cache location: C:\\Users\\User\\.cache\\huggingface\\hub\\")
print("="*60)
print()
print("Downloading... This may take 5-10 minutes...")
print()

try:
    # 下载模型
    model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
    
    # 测试模型
    print("\n模型下载成功！")
    print("测试模型...")
    
    test_text = ["你好", "世界"]
    embeddings = model.encode(test_text)
    
    print(f"✓ 模型工作正常！")
    print(f"  向量维度: {embeddings.shape}")
    print(f"  模型已缓存到: {model._modules['0'].auto_model.config._name_or_path}")
    print()
    print("现在可以运行项目了！")
    
except Exception as e:
    print(f"\n下载失败: {e}")
    print("\n备选方案:")
    print("1. 使用VPN/代理")
    print("2. 手动下载: https://hf-mirror.com/BAAI/bge-large-zh-v1.5")
    print("3. 跳过知识库功能，直接测试对话")

