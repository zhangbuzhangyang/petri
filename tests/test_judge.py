import pytest
from src.core.world_state import WorldState, AgentState, Item, WorldNode, ActionType, ActionIntent, AgentStatus
from src.core.rule_engine import RuleEngine

@pytest.fixture
def setup_world():
    """构建一个极小的假世界用于测试"""
    world = WorldState()
    
    # 1. 创建地图节点 (酒馆 和 街道，两者相连)
    world.nodes["saloon"] = WorldNode(id="saloon", name="酒馆", connected_nodes=["street"])
    world.nodes["street"] = WorldNode(id="street", name="街道", connected_nodes=["saloon"])
    
    # 2. 创建物品
    # 铁匠有一把刀
    knife = Item(id="item_knife_01", name="生锈的铁刀", damage=15, current_holder_id="agent_blacksmith", current_node_id="saloon")
    world.items["item_knife_01"] = knife
    
    # 幻觉武器：大模型幻想出来的火箭筒 (它只存在于大模型的嘴里，不存在于 WorldState 中)
    # 注意：我们不把它加进 world.items
    
    # 3. 创建 Agent
    world.agents["agent_blacksmith"] = AgentState(
        id="agent_blacksmith", name="铁匠", current_node_id="saloon", hp=100, inventory=["item_knife_01"]
    )
    world.agents["agent_farmer"] = AgentState(
        id="agent_farmer", name="农夫", current_node_id="saloon", hp=50, inventory=[]
    )
    # 在远处街道的Agent
    world.agents["agent_sheriff"] = AgentState(
        id="agent_sheriff", name="警长", current_node_id="street", hp=100, inventory=[]
    )
    
    return world

def test_hallucination_intercepted(setup_world):
    """测试用例 1：大模型产生幻觉，试图使用不存在的火箭筒"""
    engine = RuleEngine()
    world = setup_world
    blacksmith = world.agents["agent_blacksmith"]
    farmer = world.agents["agent_farmer"]
    
    # 大模型输出的恶意/幻觉 JSON
    hallucinated_intent = ActionIntent(
        action_type=ActionType.ATTACK,
        target_id="agent_farmer",
        item_id="item_rocket_launcher_999" # 致命幻觉
    )
    
    judgement = engine.judge(hallucinated_intent, blacksmith, world)
    
    # 断言：动作必须失败
    assert judgement.success is False
    # 断言：必须明确指出是幻觉拦截
    assert "幻觉拦截" in judgement.reason
    # 断言：农夫的血量绝对不能变 (因为 state_deltas 为空)
    assert judgement.state_deltas == {}
    print(f"✅ 幻觉拦截成功: {judgement.reason}")

def test_legitimate_attack(setup_world):
    """测试用例 2：合法的物理攻击"""
    engine = RuleEngine()
    world = setup_world
    blacksmith = world.agents["agent_blacksmith"]
    farmer = world.agents["agent_farmer"]
    
    # 正常的攻击意图
    legit_intent = ActionIntent(
        action_type=ActionType.ATTACK,
        target_id="agent_farmer",
        item_id="item_knife_01" # 使用背包里真实的刀
    )
    
    judgement = engine.judge(legit_intent, blacksmith, world)
    
    # 断言：动作成功
    assert judgement.success is True
    # 断言：返回了正确的状态增量 (农夫扣血)
    assert "agent_farmer" in judgement.state_deltas
    assert judgement.state_deltas["agent_farmer"]["hp"] == -15 # 刀的伤害是15
    print(f"✅ 合法攻击成功: {judgement.reason}, 农夫剩余血量预期: {farmer.hp - 15}")

def test_distance_attack_blocked(setup_world):
    """测试用例 3：空间法则校验，不能隔山打牛"""
    engine = RuleEngine()
    world = setup_world
    blacksmith = world.agents["agent_blacksmith"]
    sheriff = world.agents["agent_sheriff"]
    
    # 铁匠试图攻击在街道上的警长
    distance_intent = ActionIntent(
        action_type=ActionType.ATTACK,
        target_id="agent_sheriff",
        item_id="item_knife_01"
    )
    
    judgement = engine.judge(distance_intent, blacksmith, world)
    
    assert judgement.success is False
    assert "不在当前区域" in judgement.reason
    print(f"✅ 空间法则生效: {judgement.reason}")
