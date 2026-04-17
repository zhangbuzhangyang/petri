from src.core.initialization import build_initial_world
from src.core.engine.state_manager import StateManager
from src.core.rule_engine.actions.trade import judge_trade
from src.core.rule_engine.actions.eat import judge_eat
from src.core.world_state import ActionIntent, ActionType

world = build_initial_world()
state_manager = StateManager(world)

print("=== 测试1：购买苹果 ===")
agent = world.agents['agent_farmer']
agent.current_node_id = 'general_store'
agent.gold = 10
print(f"购买前: {agent.name} 金币={agent.gold}")

intent = ActionIntent(
    action_type=ActionType.TRADE,
    requested_items=['item_apple']
)
judgement = judge_trade(intent, agent, world)
print(f"裁决: {judgement.success}, {judgement.reason}")
if judgement.success:
    state_manager.apply_state_deltas(judgement.state_deltas)
print(f"购买后: {agent.name} 金币={agent.gold}, 背包={agent.inventory}")

print()
print("=== 测试2：吃苹果 ===")
print(f"吃前: {agent.name} 饥饿度={agent.hunger}")
intent2 = ActionIntent(
    action_type=ActionType.EAT,
    item_id='item_apple'
)
judgement2 = judge_eat(intent2, agent, world)
print(f"裁决: {judgement2.success}, {judgement2.reason}")
if judgement2.success:
    state_manager.apply_state_deltas(judgement2.state_deltas)
print(f"吃后: {agent.name} 饥饿度={agent.hunger}, 背包={agent.inventory}")

print()
print("=== 测试3：卖东西到商店 ===")
agent2 = world.agents['agent_local']
agent2.current_node_id = 'blacksmith'
agent2.gold = 5
world.items['item_iron_ore'].current_holder_id = agent2.id
agent2.inventory = ['item_iron_ore']
print(f"卖前: {agent2.name} 金币={agent2.gold}, 背包={agent2.inventory}")

intent3 = ActionIntent(
    action_type=ActionType.TRADE,
    offered_items=['item_iron_ore']
)
judgement3 = judge_trade(intent3, agent2, world)
print(f"裁决: {judgement3.success}, {judgement3.reason}")
if judgement3.success:
    state_manager.apply_state_deltas(judgement3.state_deltas)
print(f"卖后: {agent2.name} 金币={agent2.gold}, 背包={agent2.inventory}")