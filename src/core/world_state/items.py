from pydantic import BaseModel, Field
from typing import Optional

# ==========================================
# 2. 物品实体：它具有绝对的物理属性
# ==========================================
class Item(BaseModel):
    id: str = Field(..., description="全局唯一物品ID，如 item_apple_01")
    name: str = Field(..., description="物品显示名")
    
    # 物理属性 (引擎只看这些数字)
    is_edible: bool = False
    hunger_restore: int = 0
    damage: int = 0
    value: int = 0  # 金币价值
    
    # 状态标记
    current_holder_id: Optional[str] = Field(None, description="如果为None，说明在地上；如果有值，说明在某Agent背包里")
    current_node_id: Optional[str] = Field(None, description="所在的具体地点节点")
