from pydantic import BaseModel, Field
from typing import Dict, Any

class Judgement(BaseModel):
    """规则引擎的判决书"""
    success: bool = Field(..., description="动作是否合法允许")
    reason: str = Field(..., description="判决原因，如果失败，这里会说明原因（可转化为游戏内的反馈）")
    
    # 状态变更指令 (增量)
    # 格式: {"agent_id": {"hp": -10}, "item_id": {"current_holder_id": None}}
    state_deltas: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
