from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType, AgentStatus
from src.core.rule_engine.models import Judgement
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("MoveAction")

def judge_move(intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
    """
    裁决移动动作
    """
    target_node = intent.target_node_id
    if not target_node or target_node not in world.nodes:
        logger.warning(f"⚠️ 移动目标地点不存在: {target_node}")
        return Judgement(success=False, reason="移动目标地点不存在。")
        
    current_node = world.nodes[agent.current_node_id]
    if target_node not in current_node.connected_nodes:
        logger.info(f"🚶 {agent.name} 无法移动到 {target_node}，路径不通")
        return Judgement(success=False, reason=f"无法直达 {target_node}，路径不通。")
        
    logger.info(f"✅ {agent.name} 移动到 {world.nodes[target_node].name}")
    return Judgement(
        success=True, 
        reason=f"移动到 {world.nodes[target_node].name}。",
        state_deltas={agent.id: {"current_node_id": target_node}}
    )
