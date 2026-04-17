from src.core.world_state import WorldState, AgentState
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("Cognitive")

class Perceptor:
    """将 WorldState 翻译成 Agent 能理解的文本感知"""
    
    def get_self_perception(self, agent: AgentState) -> str:
        """感知自身状态"""
        hp_status = "濒死" if agent.hp < 20 else "受伤" if agent.hp < 50 else "健康"
        hunger_status = "极度饥饿，快饿死了" if agent.hunger > 80 else "有些饥饿" if agent.hunger > 40 else "不饿"
        
        inventory_str = "空空如也"
        if agent.inventory:
            # 实际项目中这里应该去查物品名字，为简化演示，先直接显示ID
            inventory_str = ", ".join(agent.inventory)
            
        return f"你的身体状态：{hp_status} (HP:{agent.hp})。饥饿感：{hunger_status}。你的背包里有：[{inventory_str}]。"

    def get_environment_perception(self, agent: AgentState, world: WorldState) -> str:
        """感知周围环境"""
        current_node = world.nodes[agent.current_node_id]
        perception = f"你当前在 [{current_node.name}]。"
        
        # 看到周围的人
        nearby_agents = world.get_agents_at_node(agent.current_node_id)
        other_people = [a.name for a in nearby_agents if a.id != agent.id]
        if other_people:
            perception += f"你看到附近有这些人：{', '.join(other_people)}。"
        else:
            perception += "附近没有其他人。"
            
        # 看到地上的物品
        items_on_ground = [item.name for item in world.items.values()
                           if item.current_node_id == agent.current_node_id and item.current_holder_id is None]
        if items_on_ground:
            perception += f"你看到地上散落着：{', '.join(items_on_ground)}。"
            
        return perception



