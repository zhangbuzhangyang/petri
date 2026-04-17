from pydantic import BaseModel, Field
from typing import Dict, Optional

class MarketItem(BaseModel):
    """商店商品"""
    price: int = Field(..., description="商品价格（金币）")
    quantity: int = Field(default=1, ge=0, description="商品数量")

class Market(BaseModel):
    node_id: str = Field(..., description="商店所在节点ID")
    name: str = Field(..., description="商店名称，如'老张杂货店'")
    inventory: Dict[str, MarketItem] = Field(default_factory=dict, description="商品库存，item_id -> MarketItem")

    def get_price(self, item_id: str) -> Optional[int]:
        item = self.inventory.get(item_id)
        return item.price if item else None

    def get_quantity(self, item_id: str) -> int:
        item = self.inventory.get(item_id)
        return item.quantity if item else 0

    def has_item(self, item_id: str) -> bool:
        item = self.inventory.get(item_id)
        return item is not None and item.quantity > 0