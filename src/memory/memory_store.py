from typing import List, Dict, Any, Optional
from datetime import datetime
from src.core.logger import get_logger

# 尝试导入 ChromaDB
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# 获取日志器
logger = get_logger("MemoryStore")

class Memory:
    """
    单个记忆的结构
    """
    def __init__(self, content: str, timestamp: datetime = None, importance: float = 0.5):
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.importance = importance  # 0-1，记忆的重要性

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        """
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """
        从字典创建 Memory 对象
        """
        return cls(
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            importance=data.get("importance", 0.5)
        )

class MemoryStore:
    """
    记忆存储系统，负责存储和检索 Agent 的记忆
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.memories: List[Memory] = []
        self.chroma_client = None
        self.collection = None

        # 初始化 ChromaDB
        if CHROMADB_AVAILABLE:
            try:
                logger.info(f"正在初始化 ChromaDB，可能需要下载嵌入模型（all-MiniLM-L6-v2）...")
                self.chroma_client = chromadb.PersistentClient(path="./snapshots/memory")
                self.collection = self.chroma_client.get_or_create_collection(
                    name=f"agent_{agent_id}_memories"
                )
                logger.info(f"\033[92mChromaDB 初始化成功，为 Agent {agent_id} 创建记忆库\033[0m")
            except Exception as e:
                logger.error(f"ChromaDB 初始化失败: {e}")
                self.chroma_client = None
                self.collection = None
        else:
            logger.warning("ChromaDB 不可用，将使用内存存储")

    def add_memory(self, content: str, importance: float = 0.5):
        """
        添加新记忆
        """
        # 检查是否已存在完全相同的记忆（去重）
        if any(m.content == content for m in self.memories):
            logger.debug(f"记忆已存在，跳过添加: {content[:50]}...")
            return

        memory = Memory(content, importance=importance)
        self.memories.append(memory)
        memory_id = f"memory_{self.agent_id}_{len(self.memories)}_{memory.timestamp.timestamp()}"

        # 如果 ChromaDB 可用，也存储到向量数据库
        if CHROMADB_AVAILABLE and self.collection:
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[{
                        "timestamp": memory.timestamp.isoformat(),
                        "importance": importance
                    }],
                    ids=[memory_id]
                )
            except Exception as e:
                logger.error(f"存储记忆到 ChromaDB 失败: {e}")

        logger.debug(f"为 Agent {self.agent_id} 添加记忆: {content[:50]}...")

    def get_recent_memories(self, limit: int = 10) -> List[Memory]:
        """
        获取最近的记忆
        """
        return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:limit]

    def retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """
        根据查询检索相关记忆
        """
        if CHROMADB_AVAILABLE and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                # 构建记忆列表
                relevant_memories = []
                for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                    memory = Memory(
                        content=doc,
                        timestamp=datetime.fromisoformat(metadata["timestamp"]),
                        importance=metadata.get("importance", 0.5)
                    )
                    relevant_memories.append(memory)
                
                return relevant_memories
            except Exception as e:
                logger.error(f"从 ChromaDB 检索记忆失败: {e}")
                # 失败时返回最近的记忆
                return self.get_recent_memories(limit)
        else:
            # ChromaDB 不可用时，返回最近的记忆
            return self.get_recent_memories(limit)

    def clear_memories(self):
        """
        清空所有记忆
        """
        self.memories.clear()
        if CHROMADB_AVAILABLE and self.collection:
            try:
                # 获取所有 ID 并删除
                all_ids = [f"memory_{i}" for i in range(1, len(self.memories) + 1)]
                if all_ids:
                    self.collection.delete(ids=all_ids)
            except Exception as e:
                logger.error(f"清空 ChromaDB 记忆失败: {e}")
        logger.info(f"清空 Agent {self.agent_id} 的所有记忆")

    def get_memory_count(self) -> int:
        """
        获取记忆数量
        """
        return len(self.memories)
