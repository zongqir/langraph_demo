"""
向量知识库模块
使用FAISS进行向量检索
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings
from langraph_customer_service.utils import log


class KnowledgeBase:
    """向量知识库"""
    
    def __init__(self, embedding_model: Optional[str] = None):
        """
        初始化知识库
        
        Args:
            embedding_model: 嵌入模型名称
        """
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        self.index_path = Path(settings.vector_store_path) / "faiss.index"
        self.docs_path = Path(settings.vector_store_path) / "documents.pkl"
        
        log.info(f"初始化知识库: embedding_model={self.embedding_model_name}")
    
    def _load_embedding_model(self):
        """加载嵌入模型"""
        if self.model is None:
            log.info("加载嵌入模型...")
            # 检查本地模型路径
            local_model_path = Path("./models/bge-large-zh-v1.5")
            if local_model_path.exists():
                log.info(f"使用本地模型: {local_model_path}")
                self.model = SentenceTransformer(str(local_model_path))
            else:
               raise "务必搞清楚，不允许自动下载 太慢了！"
            log.info("嵌入模型加载完成")
    
    def add_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        添加单条文档到知识库
        
        Args:
            document: 文档内容
            metadata: 元数据
        """
        self.add_documents([document], [metadata] if metadata else None)
    
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ):
        """
        添加文档到知识库
        
        Args:
            documents: 文档列表
            metadata: 元数据列表
        """
        self._load_embedding_model()
        
        log.info(f"添加 {len(documents)} 条文档到知识库")
        
        # 生成嵌入向量
        embeddings = self.model.encode(documents, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # 创建或更新FAISS索引
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings)
        self.documents.extend(documents)
        
        # 添加元数据
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in documents])
        
        log.info(f"知识库当前文档数: {len(self.documents)}")
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回top-k个结果
            score_threshold: 相似度阈值（L2距离，越小越相似）
        
        Returns:
            检索结果列表，score字段为相似度（0-1，越大越相似）
        """
        if self.index is None or len(self.documents) == 0:
            log.warning("知识库为空，无法检索")
            return []
        
        self._load_embedding_model()
        
        # 生成查询向量
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # 检索
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        # 整理结果
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if dist <= score_threshold:
                # 将L2距离转换为相似度分数 (0-1, 越大越相似)
                # 使用负指数函数将距离转换为相似度
                similarity = np.exp(-dist)
                
                results.append({
                    "document": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(similarity),  # 相似度 (0-1)
                    "distance": float(dist),      # 原始L2距离
                    "index": int(idx)
                })
        
        log.debug(f"检索到 {len(results)} 条相关文档")
        return results
    
    def save(self):
        """保存知识库到磁盘"""
        if self.index is None:
            log.warning("知识库为空，跳过保存")
            return
        
        # 保存FAISS索引
        faiss.write_index(self.index, str(self.index_path))
        
        # 保存文档和元数据
        with open(self.docs_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        log.info(f"知识库已保存: {self.index_path}")
    
    def load(self):
        """从磁盘加载知识库"""
        if not self.index_path.exists() or not self.docs_path.exists():
            log.warning("知识库文件不存在，跳过加载")
            return False
        
        self._load_embedding_model()
        
        # 加载FAISS索引
        self.index = faiss.read_index(str(self.index_path))
        
        # 加载文档和元数据
        with open(self.docs_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
        
        log.info(f"知识库已加载: {len(self.documents)} 条文档")
        return True
    
    def clear(self):
        """清空知识库"""
        self.index = None
        self.documents = []
        self.metadata = []
        log.info("知识库已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_documents': len(self.documents),
            'vector_dim': self.index.d if self.index is not None else 0,
            'index_built': self.index is not None,
            'categories': {}
        }
        
        # 统计分类
        for meta in self.metadata:
            category = meta.get('category', '未分类')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        return stats
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        获取所有文档
        
        Returns:
            文档列表，每个文档包含content和metadata
        """
        return [
            {
                'content': doc,
                'metadata': meta
            }
            for doc, meta in zip(self.documents, self.metadata)
        ]

