from pydantic import BaseModel, Field
from typing import Optional, List
from src.core.world_state.enums import ActionType

# ==========================================
# 3. 动作意图：大模型必须吐出这个格式，多一个字都不行
# ==========================================
class ActionIntent(BaseModel):
    """这是从 LLM 的输出中强行提取出来的结构化意图"""
    action_type: ActionType
    target_id: Optional[str] = Field(None, description="动作目标，比如打谁、跟谁交易")
    item_id: Optional[str] = Field(None, description="使用的物品ID")
    target_node_id: Optional[str] = Field(None, description="移动的目标地点")
    
    # 对于交易动作的额外参数
    offered_items: List[str] = Field(default_factory=list, description="我给出的物品ID列表")
    requested_items: List[str] = Field(default_factory=list, description="我索要的物品ID列表")
    
    # 纯文本输出（仅用于 SPEAK 动作或内心戏）
    dialogue_content: Optional[str] = Field(None, description="说的话")
