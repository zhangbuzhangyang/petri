from src.core.world_state import WorldState, Item
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("ItemInitializer")

def initialize_items(world: WorldState):
    """
    初始化世界物品
    创建基础的物品并放置在合适的地点
    """
    logger.info("初始化世界物品...")
    
    # 构建物品 (刀掉在酒馆地上)
    world.items["item_knife_01"] = Item(
        id="item_knife_01", name="生锈的铁刀", damage=25, 
        current_holder_id=None, current_node_id="saloon"
    )
    
    # 可以在这里添加更多物品
    # 例如：
    # world.items["item_apple_01"] = Item(
    #     id="item_apple_01", name="新鲜苹果", is_edible=True, hunger_restore=10, 
    #     current_holder_id=None, current_node_id="saloon"
    # )
    # world.items["item_gold_01"] = Item(
    #     id="item_gold_01", name="金币", value=10, 
    #     current_holder_id=None, current_node_id="alley"
    # )
    
    logger.info(f"物品初始化完成，创建了 {len(world.items)} 个物品")
