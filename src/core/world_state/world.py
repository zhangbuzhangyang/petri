from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from src.core.world_state.nodes import WorldNode
from src.core.world_state.agents import AgentState
from src.core.world_state.items import Item
from src.core.world_state.market import Market
from src.core.world_state.enums import AgentStatus

# ==========================================
# 6. 世界总状态：唯一的"真理"
# ==========================================
class WorldState(BaseModel):
    """这是一个巨大的单例状态树，整个世界只存在这一个绝对真相"""
    tick_count: int = 0

    nodes: Dict[str, WorldNode] = Field(default_factory=dict)
    agents: Dict[str, AgentState] = Field(default_factory=dict)
    items: Dict[str, Item] = Field(default_factory=dict)
    markets: Dict[str, Market] = Field(default_factory=dict, description="商店列表，node_id -> Market")

    # --- 便捷查询接口 (供规则引擎调用) ---
    def get_agent_inventory_items(self, agent_id: str) -> List[Item]:
        """获取一个 Agent 真实的物品对象列表"""
        agent = self.agents.get(agent_id)
        if not agent: return []
        return [self.items[item_id] for item_id in agent.inventory if item_id in self.items]

    def get_agents_at_node(self, node_id: str) -> List[AgentState]:
        """获取某个地点的所有活人"""
        return [a for a in self.agents.values() if a.current_node_id == node_id and a.status == AgentStatus.ALIVE]

    def get_market_at_node(self, node_id: str) -> Optional[Market]:
        """获取某个地点的商店"""
        return self.markets.get(node_id)
