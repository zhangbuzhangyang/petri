from src.core.world_state import WorldState, Market
from src.core.logger import get_logger
from .config import MARKET_CONFIGS, get_market_inventory

logger = get_logger("MarketInitializer")

def initialize_markets(world: WorldState):
    """
    初始化商店
    """
    logger.info("初始化商店...")

    for node_id, config in MARKET_CONFIGS.items():
        world.markets[node_id] = Market(
            node_id=node_id,
            name=config.name,
            inventory=get_market_inventory(node_id)
        )
        logger.debug(f"创建商店: {config.name} (位置: {node_id})")
        for item_id, item_config in config.items.items():
            logger.debug(f"  - {item_config.description}: {item_config.price}金币")

    logger.info(f"商店初始化完成，创建了 {len(world.markets)} 个商店")