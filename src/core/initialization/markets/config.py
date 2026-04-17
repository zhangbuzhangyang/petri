from pydantic import BaseModel, Field
from typing import Dict
from src.core.world_state import MarketItem

class MarketItemConfig(BaseModel):
    """商店商品配置"""
    price: int = Field(..., description="商品价格（金币）")
    quantity: int = Field(default=3, ge=0, description="商品初始数量")
    description: str = Field(..., description="商品描述")
    category: str = Field(..., description="商品类别")

class MarketConfig(BaseModel):
    """商店配置"""
    name: str = Field(..., description="商店名称")
    description: str = Field(..., description="商店描述")
    items: Dict[str, MarketItemConfig] = Field(default_factory=dict, description="商品配置")

# 商店配置表
MARKET_CONFIGS = {
    "saloon": MarketConfig(
        name="破旧酒馆",
        description="小镇中心的破旧酒馆，提供休息场所和各类酒水",
        items={
            "item_beer": MarketItemConfig(
                price=2,
                quantity=10,
                description="普通啤酒，清凉解渴",
                category="酒水"
            ),
            "item_wine": MarketItemConfig(
                price=5,
                quantity=5,
                description="葡萄酒，香醇可口",
                category="酒水"
            ),
            "item_whiskey": MarketItemConfig(
                price=8,
                quantity=3,
                description="烈性威士忌，辛辣暖身",
                category="酒水"
            )
        }
    ),
    "blacksmith": MarketConfig(
        name="老王铁匠铺",
        description="专门打造和销售武器及原料的店铺",
        items={
            "item_iron_ore": MarketItemConfig(
                price=5,
                quantity=5,
                description="从矿洞采集的铁矿石，用于制作武器",
                category="原料"
            ),
            "item_coal": MarketItemConfig(
                price=3,
                quantity=5,
                description="煤矿炭，用于炼铁和锻造",
                category="原料"
            ),
            "item_iron_sword": MarketItemConfig(
                price=30,
                quantity=2,
                description="用铁矿石打造的铁剑，攻击力较高",
                category="武器"
            )
        }
    ),
    "general_store": MarketConfig(
        name="老张杂货店",
        description="出售日常食品和生活必需品的商店",
        items={
            "item_apple": MarketItemConfig(
                price=2,
                quantity=10,
                description="新鲜的苹果，可食用恢复饥饿",
                category="食品"
            ),
            "item_bread": MarketItemConfig(
                price=3,
                quantity=8,
                description="黑麦面包，能提供较多饱腹感",
                category="食品"
            ),
            "item_water": MarketItemConfig(
                price=1,
                quantity=15,
                description="清水，解渴并恢复少量饥饿",
                category="食品"
            )
        }
    ),
    "clinic": MarketConfig(
        name="李医生诊所",
        description="提供医疗服务和药品的诊所",
        items={
            "item_bandage": MarketItemConfig(
                price=5,
                quantity=10,
                description="绷带，用于治疗轻伤",
                category="医疗用品"
            ),
            "item_medicine": MarketItemConfig(
                price=10,
                quantity=5,
                description="治疗药水，恢复生命值",
                category="医疗用品"
            ),
            "item_antidote": MarketItemConfig(
                price=15,
                quantity=3,
                description="解毒剂，治疗中毒",
                category="医疗用品"
            )
        }
    ),
    "blackmarket": MarketConfig(
        name="黑市",
        description="出售违禁品和稀有物品的地下市场",
        items={
            "item_poison": MarketItemConfig(
                price=25,
                quantity=2,
                description="毒药，可用于攻击",
                category="违禁品"
            ),
            "item_gold_ring": MarketItemConfig(
                price=50,
                quantity=1,
                description="金戒指，价值昂贵",
                category="稀有物品"
            ),
            "item_magic_potion": MarketItemConfig(
                price=75,
                quantity=1,
                description="魔法药水，增强能力",
                category="稀有物品"
            )
        }
    )
}

# 导出库存（供 Market 类使用）
def get_market_inventory(node_id: str) -> Dict[str, MarketItem]:
    """
    获取商店的库存
    返回格式: {item_id: MarketItem}
    """
    config = MARKET_CONFIGS.get(node_id)
    if not config:
        return {}
    return {
        item_id: MarketItem(price=item.price, quantity=item.quantity)
        for item_id, item in config.items.items()
    }