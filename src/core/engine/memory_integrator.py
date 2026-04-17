from src.core.world_state import AgentState, ActionIntent, ActionType
from src.core.rule_engine import Judgement
from src.memory.memory_manager import memory_manager
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("MemoryIntegrator")

class MemoryIntegrator:
    """
    记忆集成器，负责为 Agent 添加记忆
    """
    def __init__(self):
        pass
    
    def add_memory(self, agent: AgentState, intent: ActionIntent, judgement: Judgement):
        """
        为 Agent 添加记忆
        """
        # 生成记忆内容
        if intent.action_type == ActionType.SPEAK:
            memory_content = f"你说：{intent.dialogue_content}"
        else:
            memory_content = f"你尝试{intent.action_type.value}，结果：{judgement.reason}"
        
        # 计算记忆的重要性
        importance = 0.5  # 默认重要性
        if judgement.success:
            if intent.action_type == ActionType.ATTACK:
                importance = 0.8  # 攻击行为更重要
            elif intent.action_type == ActionType.PICK_UP:
                importance = 0.7  # 拾取物品较重要
        else:
            if "幻觉拦截" in judgement.reason:
                importance = 0.6  # 幻觉拦截需要记住
        
        # 添加记忆
        memory_manager.add_memory(agent.id, memory_content, importance)
        
        # 记录日志
        logger.debug(f"为 Agent {agent.name} 添加记忆: {memory_content[:50]}...")
