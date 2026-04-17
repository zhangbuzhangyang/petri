from src.core.world_state import WorldState, WorldNode
from src.core.logger import get_logger

logger = get_logger("SpaceInitializer")

def initialize_spaces(world: WorldState):
    """
    初始化世界空间
    创建基础的地点节点和连接
    """
    logger.info("初始化世界空间...")

    # 中心区域
    world.nodes["square"] = WorldNode(id="square", name="中心广场", connected_nodes=["saloon", "clinic", "blackmarket", "blacksmith"])
    world.nodes["saloon"] = WorldNode(id="saloon", name="破旧酒馆", connected_nodes=["square", "alley", "general_store"])
    
    # 商业区域
    world.nodes["blacksmith"] = WorldNode(id="blacksmith", name="老王铁匠铺", connected_nodes=["square"])
    world.nodes["general_store"] = WorldNode(id="general_store", name="老张杂货店", connected_nodes=["saloon", "forest"])
    
    # 服务区域
    world.nodes["clinic"] = WorldNode(id="clinic", name="李医生诊所", connected_nodes=["square"])
    
    # 地下/隐蔽区域
    world.nodes["alley"] = WorldNode(id="alley", name="阴暗后巷", connected_nodes=["saloon", "blackmarket"])
    world.nodes["blackmarket"] = WorldNode(id="blackmarket", name="黑市", connected_nodes=["alley", "square"])
    
    # 资源区域
    world.nodes["mine"] = WorldNode(id="mine", name="废弃矿洞", connected_nodes=["forest"])
    world.nodes["forest"] = WorldNode(id="forest", name="幽暗森林", connected_nodes=["mine", "general_store"])

    logger.info(f"空间初始化完成，创建了 {len(world.nodes)} 个地点")
