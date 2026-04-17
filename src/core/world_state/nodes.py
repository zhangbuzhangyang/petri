from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 5. 世界节点：空间容器
# ==========================================
class WorldNode(BaseModel):
    id: str = Field(..., description="节点ID，如 node_saloon")
    name: str = Field(..., description="节点名称，如'破旧酒馆'")
    description: str = Field(default="", description="节点描述")
    connected_nodes: List[str] = Field(default_factory=list, description="相邻的可直达节点ID列表")
