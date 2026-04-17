import sys
sys.path.insert(0, 'src')
from src.core.initialization import build_initial_world

print('=== 验证新地点、商店和物品 ===')
world = build_initial_world()

print('\n1. 地点列表:')
for node_id, node in world.nodes.items():
    print(f'  - {node.name} (ID: {node_id})')
    print(f'    连接: {node.connected_nodes}')

print('\n2. 商店列表:')
for node_id, market in world.markets.items():
    print(f'  - {market.name} (位置: {node_id})')
    print(f'    商品: {market.inventory}')

print('\n3. 物品列表:')
item_count = 0
for item_id, item in world.items.items():
    print(f'  - {item.name} (ID: {item_id})')
    print(f'    类型: {item.item_type}')
    print(f'    持有者: {item.current_holder_id}')
    print(f'    位置: {item.current_node_id}')
    item_count += 1

print(f'\n=== 验证完成 ===')
print(f'总地点数: {len(world.nodes)}')
print(f'总商店数: {len(world.markets)}')
print(f'总物品数: {item_count}')
