from typing import Dict
from src.llm.brain import LLMBrain
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("BrainManager")

class BrainManager:
    """
    大脑管理器，负责为每个 Agent 初始化和管理大脑
    """
    def __init__(self):
        # 存储每个 Agent 的大脑
        self.agent_brains: Dict[str, LLMBrain] = {}
    
    def get_brain(self, agent_id: str) -> LLMBrain:
        """
        获取或创建 Agent 的大脑
        """
        if agent_id not in self.agent_brains:
            self.agent_brains[agent_id] = LLMBrain(agent_id)
            logger.info(f"为 Agent {agent_id} 创建大脑")
        return self.agent_brains[agent_id]
    
    def initialize_brains(self, agent_ids: list):
        """
        初始化多个 Agent 的大脑
        """
        for agent_id in agent_ids:
            self.get_brain(agent_id)
        logger.info(f"初始化了 {len(agent_ids)} 个 Agent 大脑")
    
    def clear_brains(self):
        """
        清空所有大脑
        """
        self.agent_brains.clear()
        logger.info("清空所有 Agent 大脑")
