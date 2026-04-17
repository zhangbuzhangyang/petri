from pydantic import BaseModel, Field
from typing import Optional
from src.core.world_state.enums import ItemType

# ==========================================
# 2. 物品实体：它具有绝对的物理属性
# ==========================================
class Item(BaseModel):
    id: str = Field(..., description="全局唯一物品ID，如 item_apple_01")
    name: str = Field(..., description="物品显示名")

    item_type: ItemType = Field(ItemType.MISC, description="物品类型：resource(原料)/product(产品)/food(食物)/weapon(武器)/misc(杂物)")

    is_edible: bool = Field(default=False, description="是否可食用")
    hunger_restore: int = Field(default=0, description="食用后恢复的饥饿度点数")
    damage: int = Field(default=0, description="武器攻击力")
    value: int = Field(default=1, description="金币价值/价格")

    current_holder_id: Optional[str] = Field(None, description="如果为None，说明在地上；如果有值，说明在某Agent背包里")
    current_node_id: Optional[str] = Field(None, description="所在的具体地点节点")
