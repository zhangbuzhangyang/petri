from src.core.world_state import WorldState, AgentState
from src.core.agent_config import agent_config_manager
from src.core.logger import get_logger

logger = get_logger("AgentInitializer")

def initialize_agents(world: WorldState):
    """
    初始化世界 Agent
    根据配置创建 Agent 并放置在合适的地点
    """
    logger.info("初始化世界 Agent...")

    for config in agent_config_manager.configs.values():
        world.agents[config.id] = AgentState(
            id=config.id,
            name=config.name,
            current_node_id=config.initial_node_id,
            hp=config.initial_hp,
            hunger=config.initial_hunger,
            gold=config.initial_gold,
            inventory=config.initial_inventory,
            system_prompt_base=config.system_prompt_base,
            personality=config.personality
        )

    logger.info(f"Agent 初始化完成，创建了 {len(world.agents)} 个角色")
