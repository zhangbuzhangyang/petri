from typing import Optional
from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType
from src.core.rule_engine.models import Judgement
from src.core.logger import get_logger

logger = get_logger("RuleEngine.trade")

def judge_trade(intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
    if not intent.offered_items and not intent.requested_items:
        return Judgement(success=False, reason="交易必须包含至少一个 offered_items 或 requested_items")

    market = world.get_market_at_node(agent.current_node_id)

    if not market:
        other_agent = None
        if intent.target_id:
            other_agent = world.agents.get(intent.target_id)

        if not other_agent:
            return Judgement(success=False, reason="附近没有商店也没有可交易的商人")

        if other_agent.current_node_id != agent.current_node_id:
            return Judgement(success=False, reason=f"{other_agent.name}不在同一个地点")

        if not intent.offered_items and not intent.requested_items:
            return Judgement(success=False, reason="peer_trade_requires_items")

        for item_id in intent.offered_items:
            if item_id not in agent.inventory:
                return Judgement(success=False, reason=f"你没有 {item_id}")

        for item_id in intent.requested_items:
            if item_id not in other_agent.inventory:
                return Judgement(success=False, reason=f"{other_agent.name}没有 {item_id}")

        deltas = {
            "type": "peer_trade",
            "from_agent": agent.id,
            "to_agent": other_agent.id,
            "offered_items": intent.offered_items,
            "requested_items": intent.requested_items,
        }
        return Judgement(success=True, reason=f"与 {other_agent.name} 交易成功", state_deltas=deltas)

    total_offer_value = 0
    for item_id in intent.offered_items:
        if item_id not in agent.inventory:
            return Judgement(success=False, reason=f"你没有 {item_id}")
        item = world.items.get(item_id)
        if item:
            total_offer_value += item.value

    total_request_value = 0
    for item_id in intent.requested_items:
        if not market.has_item(item_id):
            return Judgement(success=False, reason=f"商店没有 {item_id}")
        price = market.get_price(item_id)
        total_request_value += price

    if intent.offered_items and not intent.requested_items:
        if total_offer_value < 0:
            return Judgement(success=False, reason="无效的物品")
        net = total_offer_value
        intent.requested_items.append("GOLD")
        intent.requested_item_count = net
    elif intent.requested_items and not intent.offered_items:
        if total_request_value > agent.gold:
            return Judgement(success=False, reason=f"金币不足，需要 {total_request_value} 金币，你只有 {agent.gold}")
        net = total_request_value
        intent.offered_items.append("GOLD")
        intent.offered_item_count = net
    else:
        return Judgement(success=False, reason="market_trade_no_mixed")

    deltas = {
        "type": "market_trade",
        "market_node": market.node_id,
        "from_agent": agent.id,
        "offered_items": intent.offered_items,
        "offered_item_count": getattr(intent, 'offered_item_count', 0),
        "requested_items": intent.requested_items,
        "requested_item_count": getattr(intent, 'requested_item_count', 0),
    }
    return Judgement(success=True, reason=f"在 {market.name} 交易成功", state_deltas=deltas)