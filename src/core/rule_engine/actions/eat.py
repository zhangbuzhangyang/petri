from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType
from src.core.rule_engine.models import Judgement
from src.core.logger import get_logger

logger = get_logger("RuleEngine.eat")

def judge_eat(intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
    if not intent.item_id:
        return Judgement(success=False, reason="指定要吃的物品")

    if intent.item_id not in agent.inventory:
        return Judgement(success=False, reason="你没有这个物品")

    item = world.items.get(intent.item_id)
    if not item:
        return Judgement(success=False, reason="物品不存在")

    if not item.is_edible:
        return Judgement(success=False, reason=f"{item.name} 不能食用")

    deltas = {
        "type": "eat",
        "agent_id": agent.id,
        "item_id": intent.item_id,
        "hunger_restore": item.hunger_restore,
    }
    return Judgement(success=True, reason=f"吃掉了 {item.name}，恢复 {item.hunger_restore} 点饥饿", state_deltas=deltas)