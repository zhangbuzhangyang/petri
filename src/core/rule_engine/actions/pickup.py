from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType, AgentStatus
from src.core.rule_engine.models import Judgement
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("PickupAction")

def judge_pickup(intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
    """
    裁决拾取动作
    """
    item_id = intent.item_id
    if not item_id or item_id not in world.items:
        logger.warning(f"⚠️ 物品不存在: {item_id}")
        return Judgement(success=False, reason="物品不存在。")
        
    item = world.items[item_id]
    
    # 必须在同一个节点，且物品没有主人
    if item.current_node_id != agent.current_node_id or item.current_holder_id is not None:
        logger.info(f"📦 {agent.name} 无法捡起 {item.name}，不在当前区域或已被拾取")
        return Judgement(success=False, reason="物品不在当前区域，或者已经被别人拿起了。")
        
    logger.info(f"✅ {agent.name} 捡起了 {item.name}")
    return Judgement(
        success=True,
        reason=f"捡起了 {item.name}。",
        state_deltas={
            item_id: {"current_holder_id": agent.id},
            agent.id: {"inventory": [item_id]} # 注意：调度器处理列表追加逻辑
        }
    )
