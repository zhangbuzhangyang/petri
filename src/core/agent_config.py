import os
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.core.world_state import AgentStatus
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AgentConfig(BaseModel):
    """
    Agent 配置类，包含 Agent 的基本信息和模型配置
    """
    id: str = Field(..., description="Agent 唯一标识符")
    name: str = Field(..., description="Agent 名称")
    system_prompt_base: str = Field(..., description="Agent 基础人设提示词")

    initial_node_id: str = Field(..., description="初始所在节点")
    initial_hp: int = Field(100, ge=0, le=100, description="初始生命值")
    initial_hunger: int = Field(0, ge=0, le=100, description="初始饥饿度")
    initial_inventory: list = Field(default_factory=list, description="初始背包物品")
    initial_gold: int = Field(default=10, description="初始金币")

    personality: Dict[str, float] = Field(
        default_factory=lambda: {"aggression": 0.5, "greed": 0.5, "social": 0.5},
        description="性格参数，0.0-1.0"
    )

    model_name: str = Field("gpt-4o-mini", description="使用的模型名称")
    api_key: Optional[str] = Field(None, description="API 密钥")
    api_base: Optional[str] = Field(None, description="API 基础 URL")

    temperature: float = Field(0.7, ge=0.0, le=1.0, description="模型温度参数")
    max_tokens: int = Field(200, description="最大生成 tokens")

class AgentConfigManager:
    """
    Agent 配置管理器，负责加载和管理 Agent 配置
    """
    def __init__(self):
        self.configs: Dict[str, AgentConfig] = {}

    def add_config(self, config: AgentConfig):
        """
        添加 Agent 配置
        """
        self.configs[config.id] = config

    def get_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        获取 Agent 配置
        """
        return self.configs.get(agent_id)

    def load_default_configs(self):
        """
        加载默认 Agent 配置
        """
        # 铁匠配置
        blacksmith_config = AgentConfig(
            id="agent_blacksmith",
            name="铁匠",
            system_prompt_base="你是一个暴躁、贪婪的暴徒。你喜欢欺负弱小，看到武器就想抢。",
            initial_node_id="saloon",
            initial_hp=100,
            initial_hunger=0,
            initial_inventory=[],
            personality={"aggression": 0.8, "greed": 0.9, "social": 0.2},
            model_name=os.getenv("OMLX_MODEL_NAME", "Qwen3.5-9B-MLX-4bit"),
            api_key=os.getenv("OMLX_API_KEY", "1234"),
            api_base=os.getenv("OMLX_API_BASE", "http://127.0.0.1:56788/v1"),
            temperature=0.8,
            model_type = "OMLX",
            max_tokens=2000
        )
        self.add_config(blacksmith_config)

        # 农夫配置
        farmer_config = AgentConfig(
            id="agent_farmer",
            name="农夫",
            system_prompt_base="你极其胆小怕事。如果看到有人拿武器，你会想尽办法逃跑。",
            initial_node_id="saloon",
            initial_hp=50,
            initial_hunger=0,
            initial_inventory=[],
            personality={"aggression": 0.2, "greed": 0.3, "social": 0.7},
            model_name=os.getenv("VOLCANO_MODEL_NAME", "doubao-pro-1.5"),  # 农夫使用 火山引擎 模型
            api_key=os.getenv("VOLCANO_API_KEY", "ark-e56a0023-b874-4a94-ab46-c0bda288f4a7-eb629"),
            api_base=os.getenv("VOLCANO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
            temperature=0.6
        )
        self.add_config(farmer_config)

        # 本地模型 Agent 配置 - 使用 Ollama
        local_agent_config = AgentConfig(
            id="agent_local",
            name="本地居民",
            system_prompt_base="你是一个普通的本地居民，性格温和，喜欢与人交流。",
            initial_node_id="saloon",
            initial_hp=75,
            initial_hunger=0,
            initial_inventory=[],
            personality={"aggression": 0.3, "greed": 0.4, "social": 0.8},
            model_name=os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b"),  # 使用环境变量中的 Ollama 模型
            api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1"),  # Ollama OpenAI 兼容端点
            temperature=0.7
        )
        self.add_config(local_agent_config)

# 创建全局 Agent 配置管理器实例
agent_config_manager = AgentConfigManager()
agent_config_manager.load_default_configs()
