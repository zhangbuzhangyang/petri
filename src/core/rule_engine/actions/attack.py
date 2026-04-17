from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType, AgentStatus
from src.core.rule_engine.models import Judgement
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("AttackAction")

def judge_attack(intent: ActionIntent, agent: AgentState, world: WorldState) -> Judgement:
    """
    裁决攻击动作
    """
    # 1. 目标合法性校验
    target_id = intent.target_id
    if not target_id or target_id not in world.agents:
        logger.warning(f"⚠️ 攻击目标不存在: {target_id}")
        return Judgement(success=False, reason="攻击目标不存在。")
        
    target = world.agents[target_id]
    
    # 2. 空间校验：必须在同一个节点
    if target.current_node_id != agent.current_node_id:
        logger.info(f"⚔️ {agent.name} 无法攻击 {target.name}，不在同一区域")
        return Judgement(success=False, reason=f"目标 {target.name} 不在当前区域。")
        
    # 3. 武器合法性校验 (防幻觉核心！)
    base_damage = 1  # 空手伤害
    weapon_name = "拳头"
    
    if intent.item_id:
        weapon = world.items.get(intent.item_id)
        # 严苛检查：物品必须在世界中存在，且在Agent自己的背包里
        if not weapon:
            logger.warning(f"🔮 幻觉拦截: {agent.name} 尝试使用不存在的武器 {intent.item_id}")
            return Judgement(success=False, reason=f"幻觉拦截：世界不存在物品 {intent.item_id}。")
        if intent.item_id not in agent.inventory:
            logger.warning(f"🔮 幻觉拦截: {agent.name} 尝试使用不在背包中的武器 {weapon.name}")
            return Judgement(success=False, reason=f"幻觉拦截：你想用 {weapon.name}，但它不在你的背包里！强制动作取消。")
        
        weapon_name = weapon.name
        base_damage = weapon.damage

    # 4. 计算结果
    new_hp = max(0, target.hp - base_damage)
    status_update = {"hp": new_hp}  # 直接设置新HP值

    if new_hp <= 0:
        status_update["status"] = AgentStatus.DEAD
        logger.info(f"💀 {agent.name} 杀死了 {target.name}")
    else:
        logger.info(f"⚔️ {agent.name} 用 {weapon_name} 攻击了 {target.name}，造成 {base_damage} 点伤害")

    return Judgement(
        success=True,
        reason=f"你用 {weapon_name} 攻击了 {target.name}，造成 {base_damage} 点伤害。",
        state_deltas={
            target_id: status_update
        }
    )
