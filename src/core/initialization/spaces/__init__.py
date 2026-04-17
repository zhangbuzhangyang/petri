from src.core.world_state import WorldState, WorldNode
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("SpaceInitializer")

def initialize_spaces(world: WorldState):
    """
    初始化世界空间
    创建基础的地点节点和连接
    """
    logger.info("初始化世界空间...")
    
    # 构建空间 (酒馆和后巷相连)
    world.nodes["saloon"] = WorldNode(id="saloon", name="破旧酒馆", connected_nodes=["alley"])
    world.nodes["alley"] = WorldNode(id="alley", name="阴暗后巷", connected_nodes=["saloon"])
    
    # 可以在这里添加更多地点
    # 例如：
    # world.nodes["market"] = WorldNode(id="market", name="热闹市场", connected_nodes=["saloon"])
    # world.nodes["church"] = WorldNode(id="church", name="古老教堂", connected_nodes=["alley"])
    
    logger.info(f"空间初始化完成，创建了 {len(world.nodes)} 个地点")
