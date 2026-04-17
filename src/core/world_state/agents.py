from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from src.core.world_state.enums import AgentStatus

# ==========================================
# 4. Agent 状态：肉体与灵魂的分离
# ==========================================
class AgentState(BaseModel):
    id: str = Field(..., description="全局唯一ID")
    name: str = Field(..., description="角色名")
    
    # --- 物理层 (绝对真实，不可被 LLM 直接篡改) ---
    status: AgentStatus = AgentStatus.ALIVE
    current_node_id: str = Field(..., description="当前所在节点")
    hp: int = Field(100, ge=0, le=100)
    hunger: int = Field(0, ge=0, le=100, description="0为不饿，100为饿死边缘")
    
    # --- 持有物 (引用关系，不是真把物品存这里) ---
    inventory: List[str] = Field(default_factory=list, description="持有的 Item ID 列表")
    
    # --- 认知/心理层 (这些参数会影响 Prompt 的组装，进而影响 LLM 决策) ---
    personality: Dict[str, float] = Field(
        default_factory=lambda: {"aggression": 0.5, "greed": 0.5, "social": 0.5},
        description="性格参数，0.0-1.0，会随经历动态漂移"
    )
    system_prompt_base: str = Field(..., description="基础人设提示词，如'你是一个暴躁的铁匠'")

    @validator('inventory')
    def validate_inventory_not_empty_strings(cls, v):
        # 防御性编程，防止空字符串混入
        return [item_id for item_id in v if item_id]
