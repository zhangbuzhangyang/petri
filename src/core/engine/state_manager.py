from typing import Dict, Any
from src.core.world_state import WorldState
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("StateManager")

class StateManager:
    """
    状态管理器，负责应用状态变更
    """
    def __init__(self, world: WorldState):
        self.world = world
    
    def apply_state_deltas(self, deltas: Dict[str, Dict[str, Any]]):
        """
        将规则引擎的判决书应用到权威世界状态上
        """
        for entity_id, changes in deltas.items():
            # 寻找实体 (可能是 Agent，也可能是 Item)
            entity = self.world.agents.get(entity_id) or self.world.items.get(entity_id)
            if not entity:
                continue

            for key, delta_value in changes.items():
                current_value = getattr(entity, key)

                # 智能应用逻辑
                if isinstance(current_value, int) and isinstance(delta_value, int):
                    # 如果 delta_value 是负数，做减法；如果是正数，直接覆盖
                    # 这样可以支持 HP 直接设置（如设置新HP值）或者减少（如扣血）
                    if delta_value < 0:
                        setattr(entity, key, current_value + delta_value)
                    else:
                        # 对于HP等属性，如果是正数增量（如饱腹度增加），做加法
                        # 如果是绝对值设置，需要调用方传入负数增量
                        setattr(entity, key, delta_value)
                elif isinstance(current_value, list) and isinstance(delta_value, list):
                    # 如果是列表，做追加 (比如 inventory 追加物品)
                    current_value.extend(delta_value)
                else:
                    # 其他情况直接覆盖 (比如状态从 ALIVE 变成 DEAD)
                    setattr(entity, key, delta_value)

        logger.debug(f"应用状态变更，涉及 {len(deltas)} 个实体")
