from typing import Dict, Any, Optional
from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType, AgentStatus
from src.core.logger import get_logger
from src.core.rule_engine.models import Judgement
from src.core.rule_engine.actions.attack import judge_attack
from src.core.rule_engine.actions.move import judge_move
from src.core.rule_engine.actions.pickup import judge_pickup

# 获取日志器
logger = get_logger("RuleEngine")

class RuleEngine:
    """
    纯逻辑裁决器。
    绝对禁止在这里调用任何 LLM API！
    """
    
    def judge(self, intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
        """总调度入口"""
        logger.debug(f"裁决动作: {agent.name} 尝试 {intent.action_type.value}")
        
        # 前置校验：死人不能做事
        if agent.status != AgentStatus.ALIVE:
            logger.info(f"裁决结果: {agent.name} 已死亡，无法行动")
            return Judgement(success=False, reason="你已死亡，无法行动。")
            
        # 路由到具体的动作校验器
        if intent.action_type == ActionType.ATTACK:
            return judge_attack(intent, agent, world)
        elif intent.action_type == ActionType.MOVE:
            return judge_move(intent, agent, world)
        elif intent.action_type == ActionType.PICK_UP:
            return judge_pickup(intent, agent, world)
        elif intent.action_type == ActionType.SPEAK:
            logger.info(f"裁决结果: {agent.name} 说话，无需物理校验")
            return Judgement(success=True, reason="说话不改变物理状态。")
        elif intent.action_type == ActionType.IDLE:
            logger.info(f"裁决结果: {agent.name} 发呆，无需物理校验")
            return Judgement(success=True, reason="发呆不改变物理状态。")
        
        logger.warning(f"裁决结果: {agent.name} 尝试未知动作类型: {intent.action_type.value}")
        return Judgement(success=False, reason="未知的动作类型。")
