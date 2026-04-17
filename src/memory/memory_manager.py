from typing import Dict
from src.memory.memory_store import MemoryStore
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("MemoryManager")

class MemoryManager:
    """
    记忆管理器，负责管理所有 Agent 的记忆存储
    """
    def __init__(self):
        # 存储每个 Agent 的记忆存储
        self.memory_stores: Dict[str, MemoryStore] = {}

    def get_memory_store(self, agent_id: str) -> MemoryStore:
        """
        获取或创建 Agent 的记忆存储
        """
        if agent_id not in self.memory_stores:
            self.memory_stores[agent_id] = MemoryStore(agent_id)
            logger.info(f"为 Agent {agent_id} 创建记忆存储")
        return self.memory_stores[agent_id]

    def add_memory(self, agent_id: str, content: str, importance: float = 0.5):
        """
        为 Agent 添加记忆
        """
        memory_store = self.get_memory_store(agent_id)
        memory_store.add_memory(content, importance)

    def get_recent_memories(self, agent_id: str, limit: int = 10):
        """
        获取 Agent 的最近记忆
        """
        memory_store = self.get_memory_store(agent_id)
        return memory_store.get_recent_memories(limit)

    def retrieve_relevant_memories(self, agent_id: str, query: str, limit: int = 5):
        """
        为 Agent 检索相关记忆
        """
        memory_store = self.get_memory_store(agent_id)
        return memory_store.retrieve_relevant_memories(query, limit)

    def clear_memories(self, agent_id: str):
        """
        清空 Agent 的所有记忆
        """
        if agent_id in self.memory_stores:
            self.memory_stores[agent_id].clear_memories()

    def clear_all_memories(self):
        """
        清空所有 Agent 的记忆
        """
        for agent_id in self.memory_stores:
            self.clear_memories(agent_id)
        self.memory_stores.clear()
        logger.info("清空所有 Agent 的记忆")

    def get_memory_count(self, agent_id: str) -> int:
        """
        获取 Agent 的记忆数量
        """
        memory_store = self.get_memory_store(agent_id)
        return memory_store.get_memory_count()

# 创建全局记忆管理器实例
memory_manager = MemoryManager()
