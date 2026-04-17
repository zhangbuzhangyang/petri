from src.core.world_state import WorldState, Item, ItemType
from src.core.logger import get_logger

logger = get_logger("ItemInitializer")

def initialize_items(world: WorldState):
    """
    初始化世界物品
    创建基础的物品并放置在合适的地点
    """
    logger.info("初始化世界物品...")

    world.items["item_knife_01"] = Item(
        id="item_knife_01", name="生锈的铁刀", item_type=ItemType.WEAPON, damage=25,
        current_holder_id=None, current_node_id="saloon"
    )

    # 酒水
    world.items["item_beer"] = Item(
        id="item_beer", name="普通啤酒", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=5, value=2,
        current_holder_id="saloon", current_node_id="saloon"
    )
    world.items["item_wine"] = Item(
        id="item_wine", name="葡萄酒", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=8, value=5,
        current_holder_id="saloon", current_node_id="saloon"
    )
    world.items["item_whiskey"] = Item(
        id="item_whiskey", name="威士忌", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=12, value=8,
        current_holder_id="saloon", current_node_id="saloon"
    )

    world.items["item_apple"] = Item(
        id="item_apple", name="新鲜苹果", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=15, value=2,
        current_holder_id="general_store", current_node_id="general_store"
    )

    world.items["item_bread"] = Item(
        id="item_bread", name="黑麦面包", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=25, value=3,
        current_holder_id="general_store", current_node_id="general_store"
    )

    world.items["item_water"] = Item(
        id="item_water", name="清水", item_type=ItemType.FOOD,
        is_edible=True, hunger_restore=10, value=1,
        current_holder_id="general_store", current_node_id="general_store"
    )

    world.items["item_iron_ore"] = Item(
        id="item_iron_ore", name="铁矿石", item_type=ItemType.RESOURCE,
        value=5, current_holder_id="mine", current_node_id="mine"
    )

    world.items["item_coal"] = Item(
        id="item_coal", name="煤矿炭", item_type=ItemType.RESOURCE,
        value=3, current_holder_id="mine", current_node_id="mine"
    )

    world.items["item_iron_sword"] = Item(
        id="item_iron_sword", name="铁剑", item_type=ItemType.WEAPON,
        damage=35, value=30,
        current_holder_id="blacksmith", current_node_id="blacksmith"
    )

    world.items["item_herb"] = Item(
        id="item_herb", name="草药", item_type=ItemType.RESOURCE,
        value=4, current_holder_id="forest", current_node_id="forest"
    )

    # 医疗用品
    world.items["item_bandage"] = Item(
        id="item_bandage", name="绷带", item_type=ItemType.MISC,
        value=5, current_holder_id="clinic", current_node_id="clinic"
    )
    world.items["item_medicine"] = Item(
        id="item_medicine", name="治疗药水", item_type=ItemType.MISC,
        value=10, current_holder_id="clinic", current_node_id="clinic"
    )
    world.items["item_antidote"] = Item(
        id="item_antidote", name="解毒剂", item_type=ItemType.MISC,
        value=15, current_holder_id="clinic", current_node_id="clinic"
    )

    # 违禁品和稀有物品
    world.items["item_poison"] = Item(
        id="item_poison", name="毒药", item_type=ItemType.MISC,
        value=25, current_holder_id="blackmarket", current_node_id="blackmarket"
    )
    world.items["item_gold_ring"] = Item(
        id="item_gold_ring", name="金戒指", item_type=ItemType.MISC,
        value=50, current_holder_id="blackmarket", current_node_id="blackmarket"
    )
    world.items["item_magic_potion"] = Item(
        id="item_magic_potion", name="魔法药水", item_type=ItemType.MISC,
        value=75, current_holder_id="blackmarket", current_node_id="blackmarket"
    )

    logger.info(f"物品初始化完成，创建了 {len(world.items)} 个物品")
