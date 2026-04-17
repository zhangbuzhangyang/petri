import json
from typing import Optional, Tuple, List, Dict, Any
from src.core.world_state import ActionIntent, ActionType, AgentState, WorldState
from src.agents.cognitive import Perceptor
from src.llm.model_manager import model_manager
from src.core.agent_config import agent_config_manager
from src.memory.memory_manager import memory_manager
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("LLMBrain")

# 极其严厉的系统提示词（防幻觉的第一道软防线）
SYSTEM_PROMPT = """<no_think>
你是一个虚拟世界中的角色。你必须完全沉浸在当前的角色设定中。
【重要】你的每一次回复都必须且只能是一个合法的 JSON 对象，不要输出任何其他文字！
【禁止】不要输出 <think>、思考过程、解释、或其他说明文字，直接输出 JSON！
【禁止】不要使用 ```json 代码块包裹，直接输出纯 JSON！
【强制】不要输出任何与 JSON 无关的内容！

你只能输出纯 JSON 格式的动作决策，不要包含任何其他内容。

你可以执行的动作类型(action_type)只能是以下几种：
- "move": 移动到另一个地点。需要提供 target_node_id。
- "attack": 攻击某人。需要提供 target_id，可选提供 item_id(武器)。
- "pick_up": 捡起地上的物品。需要提供 item_id。
- "trade": 与商人交易。需要提供 offered_items(我给出的物品ID列表)、requested_items(我索要的物品ID列表)。
- "eat": 吃背包里的食物。需要提供 item_id。
- "speak": 说话。需要提供 dialogue_content。
- "idle": 发呆/什么都不做。

【交易规则】:
- 如果你要买东西(用金币换物品)，只提供 requested_items，offered_items 留空[]
- 如果你要卖东西(用物品换金币)，只提供 offered_items，requested_items 留空[]

【警告】你只能使用你当前环境中真实存在的东西！如果你试图使用不存在的武器或移动到看不见的地方，物理法则会惩罚你。

请严格按照以下格式输出：
{
"action_type": "动作类型",
"target_id": "目标ID(如无则填null)",
"item_id": "物品ID(如无则填null)",
"target_node_id": "地点ID(如无则填null)",
"offered_items": ["物品ID列表，如无则空数组"],
"requested_items": ["物品ID列表，如无则空数组"],
"dialogue_content": "你说的话(如不是说话动作则填null)"
}"""


class LLMBrain:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.perceptor = Perceptor()
        self.config = agent_config_manager.get_config(agent_id)

    def build_context(self, agent: AgentState, world: WorldState) -> Tuple[str, str, str, List, Dict, Dict, Dict, Dict]:
        """构建环境上下文"""
        # 获取感知信息
        self_perception = self.perceptor.get_self_perception(agent)
        env_perception = self.perceptor.get_environment_perception(agent, world)

        # 构建可见物品、节点、人物的映射
        visible_items = {item.name: item.id for item in world.items.values()
                         if item.current_node_id == agent.current_node_id}
        visible_nodes = {node.name: node.id for node in world.nodes.values()
                         if node.id in world.nodes[agent.current_node_id].connected_nodes + [agent.current_node_id]}
        visible_agents = {a.name: a.id for a in world.agents.values()
                          if a.current_node_id == agent.current_node_id and a.id != agent.id}

        # 获取市场信息
        market = world.get_market_at_node(agent.current_node_id)
        market_info = None
        if market:
            market_items = {}
            for item_id, price in market.inventory.items():
                item = world.items.get(item_id)
                if item:
                    market_items[f"{item.name}(价格:{price}金币)"] = item_id
            market_info = {
                "name": market.name,
                "items": market_items
            }

        # 检索相关记忆
        query = f"{agent.system_prompt_base} {self_perception} {env_perception}"
        relevant_memories = memory_manager.retrieve_relevant_memories(agent.id, query, limit=3)

        # 构建记忆字符串
        memories_str = ""
        if relevant_memories:
            memories_str = "【最近记忆】: "
            for i, memory in enumerate(relevant_memories):
                memories_str += f"{i+1}. {memory.content} "

        # 构建市场信息字符串
        market_context = ""
        if market_info:
            market_context = f"【当前商店({market_info['name']})商品】: {json.dumps(market_info['items'])}"

        # 构建完整上下文
        context = f"""
【角色基础设定】: {agent.system_prompt_base}
【当前状态】: 金币={agent.gold}, 饥饿度={agent.hunger}
【当前感知】: {self_perception} {env_perception}
{memories_str}
【可见物品映射(名字->ID)】: {json.dumps(visible_items)}
【可见人物映射(名字->ID)】: {json.dumps(visible_agents)}
【可见/相邻地点映射(名字->ID)】: {json.dumps(visible_nodes)}
{market_context}
请做出你的行动决策："""

        return (
            context,
            self_perception,
            env_perception,
            relevant_memories,
            visible_items,
            visible_agents,
            visible_nodes,
            market_info
        )

    def build_thinking_data(self, agent: AgentState, context: str, self_perception: str, 
                          env_perception: str, relevant_memories: list, 
                          visible_items: dict, visible_agents: dict, 
                          visible_nodes: dict, market_info: dict) -> dict:
        """构建思考数据"""
        # 构建思考数据（用于灵魂解剖台）
        thinking_data = {
            "system_prompt": SYSTEM_PROMPT,
            "role_prompt": agent.system_prompt_base,
            "self_perception": self_perception,
            "env_perception": env_perception,
            "relevant_memories": [{"content": m.content, "importance": m.importance} for m in relevant_memories] if relevant_memories else [],
            "visible_items": visible_items,
            "visible_agents": visible_agents,
            "visible_nodes": visible_nodes,
            "market_info": market_info,
            "full_context": context
        }

        # 打印记忆信息
        if relevant_memories:
            logger.info(f"📝 {agent.name} 相关记忆:")
            for i, memory in enumerate(relevant_memories):
                logger.info(f"  {i+1}. {memory.content}")

        # 打印思考过程信息
        logger.info(f"\n🤔 {agent.name} 的思考过程:")
        logger.info(f"🎭 角色设定: {agent.system_prompt_base}")
        logger.info(f"👁️ 当前感知: {self_perception} {env_perception}")

        # 打印可见上下文
        visible_context = {
            "物品": {name: item_id for name, item_id in visible_items.items()} if visible_items else "无",
            "人物": {name: agent_id for name, agent_id in visible_agents.items()} if visible_agents else "无",
            "地点": {name: node_id for name, node_id in visible_nodes.items()} if visible_nodes else "无"
        }
        logger.info(f"🗺️ 可见上下文: {visible_context}")

        return thinking_data

    def extract_json(self, raw_content: str) -> str:
        """提取和解析 JSON 内容"""
        import re
        
        # 首先移除所有 <think>...</think> 标签对
        cleaned_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL)
        
        # 尝试从清理后的内容中提取 JSON
        json_match = re.search(r'(\{[\s\S]*\})', cleaned_content, re.DOTALL)
        if json_match:
            extracted_json = json_match.group(1).strip()
            logger.info(f"提取到 JSON: {extracted_json[:100]}...")
            return extracted_json
        else:
            # 没有找到 JSON，使用默认 IDLE
            logger.warning("未找到 JSON 内容，强制 IDLE")
            return '{"action_type": "idle", "target_id": null, "item_id": null, "target_node_id": null, "offered_items": [], "requested_items": [], "dialogue_content": null}'

    def validate_intent(self, intent_data: dict, thinking_data: dict) -> ActionIntent:
        """验证意图"""
        # 用 Pydantic 进行最后的强制校验（防幻觉的第三道硬防线）
        # 如果大模型返回了不在枚举里的 action_type，这里会直接抛错进入 except
        intent = ActionIntent(**intent_data)
        logger.info(f"✅ 生成的意图: {intent.action_type.value}")
        
        # 将解析后的意图添加到 thinking_data
        thinking_data["parsed_intent"] = intent_data
        
        return intent

    def think(self, agent: AgentState, world: WorldState) -> Optional[ActionIntent]:
        """让大模型思考并返回结构化意图"""

        # 1. 构建环境上下文
        (
            context,
            self_perception,
            env_perception,
            relevant_memories,
            visible_items,
            visible_agents,
            visible_nodes,
            market_info
        ) = self.build_context(agent, world)

        # 2. 构建思考数据
        thinking_data = self.build_thinking_data(
            agent, context, self_perception, env_perception, 
            relevant_memories, visible_items, visible_agents, 
            visible_nodes, market_info
        )

        raw_content = None
        try:
            # 3. 获取 Agent 配置
            model_name = "gpt-4o-mini"  # 默认模型
            temperature = 0.7  # 默认温度
            max_tokens = 200  # 默认最大 tokens
            api_key = None  # API 密钥
            api_base = None  # API 基础 URL
            model_type = None  # 模型类型

            if self.config:
                model_name = self.config.model_name
                temperature = self.config.temperature
                max_tokens = self.config.max_tokens
                api_key = self.config.api_key
                api_base = self.config.api_base
                model_type = getattr(self.config, 'model_type', None)
                if model_type:
                    logger.info(f"🔧 使用显式模型类型: {model_type}")
                logger.info(f"⚙️ 使用模型: {model_name}, API端点: {api_base}, 温度: {temperature}")

            # 4. 调用大模型 (使用模型管理器)
            logger.info(f"📡 调用模型...")
            raw_content = model_manager.generate(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                model_name=model_name,
                api_key=api_key,
                api_base=api_base,
                model_type=model_type,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if not raw_content:
                raise Exception("模型返回为空")
            logger.info(f"🤖 模型输出: {raw_content[:200]}...")

            # 5. 将模型输出添加到 thinking_data
            thinking_data["model_output"] = raw_content

            # 6. 提取和解析 JSON
            extracted_json = self.extract_json(raw_content)
            intent_data = json.loads(extracted_json)
            logger.info(f"📝 解析后的意图: {json.dumps(intent_data)}")

            # 7. 验证意图
            intent = self.validate_intent(intent_data, thinking_data)
            return intent, thinking_data

        except Exception as e:
            # 任何解析失败、格式错误、网络错误，全部兜底为 IDLE（发呆）
            logger.error(f"❌ {agent.name} 思考过程崩溃: {e}")
            if raw_content:
                logger.error(f"崩溃时的模型输出: {raw_content[:500]}")
            logger.error(f"[系统警告] {agent.name} 的思考过程崩溃: {e}")
            thinking_data["error"] = str(e)
            return ActionIntent(action_type=ActionType.IDLE), thinking_data
