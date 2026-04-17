from typing import Dict, Any
from src.core.world_state import WorldState
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("StateManager")

class StateManager:
    """
    状态管理器，负责应用状态变更
    """
    def __init__(self, world: WorldState):
        self.world = world

    def apply_state_deltas(self, deltas: Dict[str, Any]):
        """
        将规则引擎的判决书应用到权威世界状态上
        """
        delta_type = deltas.get("type")

        if delta_type == "market_trade":
            self._apply_market_trade(deltas)
        elif delta_type == "peer_trade":
            self._apply_peer_trade(deltas)
        elif delta_type == "eat":
            self._apply_eat(deltas)
        else:
            self._apply_legacy_deltas(deltas)

        logger.debug(f"应用状态变更: {delta_type}")

    def _apply_market_trade(self, deltas: Dict[str, Any]):
        agent = self.world.agents.get(deltas["from_agent"])
        if not agent:
            return

        for item_id in deltas.get("offered_items", []):
            if item_id == "GOLD":
                agent.gold -= deltas.get("offered_item_count", 0)
            elif item_id in agent.inventory:
                agent.inventory.remove(item_id)
                item = self.world.items.get(item_id)
                if item:
                    item.current_holder_id = None
                    item.current_node_id = agent.current_node_id

        for item_id in deltas.get("requested_items", []):
            if item_id == "GOLD":
                agent.gold += deltas.get("requested_item_count", 0)
            elif item_id in self.world.items:
                item = self.world.items[item_id]
                agent.inventory.append(item_id)
                item.current_holder_id = agent.id
                item.current_node_id = None

    def _apply_peer_trade(self, deltas: Dict[str, Any]):
        from_agent = self.world.agents.get(deltas["from_agent"])
        to_agent = self.world.agents.get(deltas["to_agent"])
        if not from_agent or not to_agent:
            return

        for item_id in deltas.get("offered_items", []):
            if item_id in from_agent.inventory:
                from_agent.inventory.remove(item_id)
                to_agent.inventory.append(item_id)
                item = self.world.items.get(item_id)
                if item:
                    item.current_holder_id = to_agent.id

        for item_id in deltas.get("requested_items", []):
            if item_id in to_agent.inventory:
                to_agent.inventory.remove(item_id)
                from_agent.inventory.append(item_id)
                item = self.world.items.get(item_id)
                if item:
                    item.current_holder_id = from_agent.id

    def _apply_eat(self, deltas: Dict[str, Any]):
        agent = self.world.agents.get(deltas["agent_id"])
        if not agent:
            return

        item_id = deltas.get("item_id")
        if item_id in agent.inventory:
            agent.inventory.remove(item_id)

        agent.hunger = max(0, agent.hunger - deltas.get("hunger_restore", 0))

        if item_id in self.world.items:
            item = self.world.items[item_id]
            item.current_holder_id = None

    def _apply_legacy_deltas(self, deltas: Dict[str, Dict[str, Any]]):
        for entity_id, changes in deltas.items():
            if entity_id == "type":
                continue
            entity = self.world.agents.get(entity_id) or self.world.items.get(entity_id)
            if not entity:
                continue

            for key, delta_value in changes.items():
                current_value = getattr(entity, key)

                if isinstance(current_value, int) and isinstance(delta_value, int):
                    if delta_value < 0:
                        setattr(entity, key, current_value + delta_value)
                    else:
                        setattr(entity, key, delta_value)
                elif isinstance(current_value, list) and isinstance(delta_value, list):
                    current_value.extend(delta_value)
                else:
                    setattr(entity, key, delta_value)
