import sys
sys.path.insert(0, 'src')
from src.core.initialization import build_initial_world
from src.core.rule_engine.actions.pickup import judge_pickup
from src.core.world_state import ActionIntent, ActionType

print('=== 测试：验证商店商品不可直接拾取 ===')
world = build_initial_world()

# 测试拾取面包
agent = world.agents['agent_blacksmith']
intent = ActionIntent(
    action_type=ActionType.PICK_UP,
    item_id='item_bread',
    target_node_id=None
)

judgement = judge_pickup(intent, agent, world)
print(f'拾取面包：{judgement.success} - {judgement.reason}')

# 测试拾取苹果
intent = ActionIntent(
    action_type=ActionType.PICK_UP,
    item_id='item_apple',
    target_node_id=None
)

judgement = judge_pickup(intent, agent, world)
print(f'拾取苹果：{judgement.success} - {judgement.reason}')

# 测试拾取铁剑
intent = ActionIntent(
    action_type=ActionType.PICK_UP,
    item_id='item_iron_sword',
    target_node_id=None
)

judgement = judge_pickup(intent, agent, world)
print(f'拾取铁剑：{judgement.success} - {judgement.reason}')

# 测试拾取地上的刀（应该可以）
intent = ActionIntent(
    action_type=ActionType.PICK_UP,
    item_id='item_knife_01',
    target_node_id=None
)

agent.current_node_id = 'saloon'  # 移动到酒馆
judgement = judge_pickup(intent, agent, world)
print(f'拾取地上的刀：{judgement.success} - {judgement.reason}')

print('\n=== 测试完成 ===')