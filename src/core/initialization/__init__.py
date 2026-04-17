from src.core.world_state import WorldState
from src.core.initialization.spaces import initialize_spaces
from src.core.initialization.items import initialize_items
from src.core.initialization.agents import initialize_agents
from src.core.initialization.markets import initialize_markets
from src.core.logger import get_logger
from src.core.engine import GameEngine

logger = get_logger("Initialization")

def build_initial_world() -> WorldState:
    """
    构建初始世界状态
    创建基础的空间、物品、商店和角色
    """
    logger.info("开始构建初始世界...")
    world = WorldState()

    initialize_spaces(world)
    initialize_items(world)
    initialize_markets(world)
    initialize_agents(world)

    logger.info(f"初始世界构建完成，包含 {len(world.nodes)} 个地点、{len(world.items)} 个物品、{len(world.markets)} 个商店、{len(world.agents)} 个角色")
    return world


# 构建引擎
def build_engine():
    logger.info("🌍 正在初始化 Petri 世界...")

    world = build_initial_world()
    engine = GameEngine(world)
    # 不再需要手动注入 LLM 大脑，GameEngine 会自动为每个 Agent 创建大脑
    
    logger.info("⏱️ 开始推进时间 (运行 3 个 Tick)...")
    for _ in range(3):
        engine.run_tick()
        
    logger.info("🌌 世界演化暂停。")
