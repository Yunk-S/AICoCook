"""
向量数据库集成模块

提供统一的向量数据库接口，支持 FAISS、Pinecone、Weaviate 等。
"""

import json
import os
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
import structlog
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import VectorDBException

logger = structlog.get_logger()
settings = get_settings()


class VectorSearchResult(BaseModel):
    """向量搜索结果"""
    id: str
    score: float
    metadata: Dict[str, Any] = {}
    content: Optional[str] = None


class VectorDBInterface(ABC):
    """向量数据库抽象接口"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化向量数据库连接"""
        pass
    
    @abstractmethod
    async def add_vectors(
        self,
        vectors: np.ndarray,
        ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """添加向量"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """搜索相似向量"""
        pass
    
    @abstractmethod
    async def delete_vectors(self, ids: List[str]) -> None:
        """删除向量"""
        pass
    
    @abstractmethod
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        """更新元数据"""
        pass
    
    @abstractmethod
    async def get_vector_count(self) -> int:
        """获取向量数量"""
        pass


class FAISSVectorDB(VectorDBInterface):
    """FAISS 向量数据库实现"""
    
    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.dimension: int = 768  # 默认维度，将根据实际向量调整
        
        # 文件路径
        self.embeddings_dir = Path(settings.EMBEDDINGS_DIR)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.embeddings_dir / "recipe_index.faiss"
        self.metadata_file = self.embeddings_dir / "recipe_metadata.pkl"
        self.id_mapping_file = self.embeddings_dir / "id_mapping.pkl"
    
    async def initialize(self) -> None:
        """初始化 FAISS 索引"""
        try:
            if self.index_file.exists():
                await self._load_index()
                logger.info("Loaded existing FAISS index", vector_count=self.index.ntotal)
            else:
                await self._create_index()
                logger.info("Created new FAISS index")
        except Exception as e:
            logger.error("Failed to initialize FAISS index", error=str(e))
            raise VectorDBException(f"Failed to initialize FAISS: {str(e)}")
    
    async def _create_index(self) -> None:
        """创建新的 FAISS 索引"""
        # 使用 L2 距离的平面索引
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}
        self.id_to_index = {}
        self.index_to_id = {}
    
    async def _load_index(self) -> None:
        """加载现有的 FAISS 索引"""
        # 加载索引
        self.index = faiss.read_index(str(self.index_file))
        self.dimension = self.index.d
        
        # 加载元数据
        if self.metadata_file.exists():
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
        
        # 加载 ID 映射
        if self.id_mapping_file.exists():
            with open(self.id_mapping_file, 'rb') as f:
                mapping_data = pickle.load(f)
                self.id_to_index = mapping_data['id_to_index']
                self.index_to_id = mapping_data['index_to_id']
    
    async def _save_index(self) -> None:
        """保存 FAISS 索引"""
        # 保存索引
        faiss.write_index(self.index, str(self.index_file))
        
        # 保存元数据
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # 保存 ID 映射
        with open(self.id_mapping_file, 'wb') as f:
            mapping_data = {
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id
            }
            pickle.dump(mapping_data, f)
    
    async def add_vectors(
        self,
        vectors: np.ndarray,
        ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """添加向量到 FAISS 索引"""
        if len(vectors) != len(ids):
            raise ValueError("Vectors and IDs must have the same length")
        
        # 调整索引维度
        if vectors.shape[1] != self.dimension:
            self.dimension = vectors.shape[1]
            if self.index is None or self.index.ntotal == 0:
                self.index = faiss.IndexFlatL2(self.dimension)
        
        # 确保向量为 float32 类型
        vectors = vectors.astype(np.float32)
        
        # 添加向量到索引
        start_index = self.index.ntotal
        self.index.add(vectors)
        
        # 更新 ID 映射和元数据
        for i, vector_id in enumerate(ids):
            index_pos = start_index + i
            self.id_to_index[vector_id] = index_pos
            self.index_to_id[index_pos] = vector_id
            
            if metadata and i < len(metadata):
                self.metadata[vector_id] = metadata[i]
        
        # 保存到磁盘
        await self._save_index()
        
        logger.info(
            "Added vectors to FAISS index",
            count=len(vectors),
            total_vectors=self.index.ntotal
        )
    
    async def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """搜索相似向量"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 确保查询向量维度正确
        if query_vector.shape[0] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[0]} doesn't match index dimension {self.dimension}")
        
        # 优化搜索策略：根据过滤器决定搜索数量
        search_count = top_k
        if filters:
            # 如果有过滤器，预计会过滤掉一些结果，增加搜索数量
            search_count = min(top_k * 3, self.index.ntotal)
        else:
            # 没有过滤器时直接搜索所需数量
            search_count = min(top_k, self.index.ntotal)
        
        # 搜索
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_vector, search_count)
        
        results = []
        for distance, index in zip(distances[0], indices[0]):
            if index == -1:  # FAISS 返回 -1 表示无效结果
                continue
            
            vector_id = self.index_to_id.get(index)
            if vector_id is None:
                continue
            
            # 应用过滤器
            metadata = self.metadata.get(vector_id, {})
            if filters and not self._apply_filters(metadata, filters):
                continue
            
            results.append(VectorSearchResult(
                id=vector_id,
                score=float(distance),
                metadata=metadata,
                content=metadata.get('content')
            ))
            
            # 早期退出优化：一旦获得足够结果就停止
            if len(results) >= top_k:
                break
        
        return results
    
    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """应用元数据过滤器"""
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            metadata_value = metadata[key]
            
            # 支持不同类型的过滤
            if isinstance(value, list):
                if metadata_value not in value:
                    return False
            elif isinstance(value, dict):
                # 支持范围过滤，如 {"gte": 0.5, "lte": 1.0}
                if "gte" in value and metadata_value < value["gte"]:
                    return False
                if "gt" in value and metadata_value <= value["gt"]:
                    return False
                if "lte" in value and metadata_value > value["lte"]:
                    return False
                if "lt" in value and metadata_value >= value["lt"]:
                    return False
            else:
                if metadata_value != value:
                    return False
        
        return True
    
    async def delete_vectors(self, ids: List[str]) -> None:
        """删除向量（FAISS 不支持直接删除，需要重建索引）"""
        if not ids:
            return
        
        # 获取要保留的向量
        remaining_ids = []
        remaining_vectors = []
        remaining_metadata = []
        
        for vector_id, index_pos in self.id_to_index.items():
            if vector_id not in ids:
                remaining_ids.append(vector_id)
                # 重建向量需要从原始数据源获取，这里暂时跳过实现
                # 在实际应用中，可能需要存储原始向量数据
        
        # 注意：完整的删除实现需要重建整个索引
        logger.warning("FAISS vector deletion requires index rebuilding, not implemented yet")
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        """更新向量元数据"""
        if id in self.metadata:
            self.metadata[id].update(metadata)
            await self._save_index()
        else:
            raise ValueError(f"Vector with ID {id} not found")
    
    async def get_vector_count(self) -> int:
        """获取向量数量"""
        return self.index.ntotal if self.index else 0


class PineconeVectorDB(VectorDBInterface):
    """Pinecone 向量数据库实现"""
    
    def __init__(self):
        # 这里可以实现 Pinecone 集成
        raise NotImplementedError("Pinecone integration not implemented yet")
    
    async def initialize(self) -> None:
        pass
    
    async def add_vectors(self, vectors: np.ndarray, ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        pass
    
    async def search(self, query_vector: np.ndarray, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        return []
    
    async def delete_vectors(self, ids: List[str]) -> None:
        pass
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        pass
    
    async def get_vector_count(self) -> int:
        return 0


class WeaviateVectorDB(VectorDBInterface):
    """Weaviate 向量数据库实现"""
    
    def __init__(self):
        # 这里可以实现 Weaviate 集成
        raise NotImplementedError("Weaviate integration not implemented yet")
    
    async def initialize(self) -> None:
        pass
    
    async def add_vectors(self, vectors: np.ndarray, ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        pass
    
    async def search(self, query_vector: np.ndarray, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        return []
    
    async def delete_vectors(self, ids: List[str]) -> None:
        pass
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        pass
    
    async def get_vector_count(self) -> int:
        return 0


def get_vector_db() -> VectorDBInterface:
    """获取向量数据库实例"""
    db_type = settings.VECTOR_DB_TYPE.lower()
    
    if db_type == "faiss":
        return FAISSVectorDB()
    elif db_type == "pinecone":
        return PineconeVectorDB()
    elif db_type == "weaviate":
        return WeaviateVectorDB()
    else:
        raise ValueError(f"Unsupported vector database type: {db_type}")


# 全局向量数据库实例
_vector_db_instance: Optional[VectorDBInterface] = None

async def get_vector_db_instance() -> VectorDBInterface:
    """获取全局向量数据库实例"""
    global _vector_db_instance
    
    if _vector_db_instance is None:
        _vector_db_instance = get_vector_db()
        await _vector_db_instance.initialize()
    
    return _vector_db_instance