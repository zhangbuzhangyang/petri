from enum import Enum

# ==========================================
# 1. 基础枚举：拒绝魔法字符串
# ==========================================
class AgentStatus(str, Enum):
    ALIVE = "alive"
    DEAD = "dead"
    UNCONSCIOUS = "unconscious" # 预留：被打晕

class ActionType(str, Enum):
    MOVE = "move"
    ATTACK = "attack"
    TRADE = "trade"
    PICK_UP = "pick_up"
    DROP = "drop"
    SPEAK = "speak"         # 对白不影响物理状态，但会被记录
    IDLE = "idle"           # 强制兜底动作
