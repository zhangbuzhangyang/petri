import json
from typing import Optional
from src.core.world_state import ActionIntent, ActionType, AgentState, WorldState
from src.agents.cognitive import Perceptor
from src.llm.model_manager import model_manager
from src.core.agent_config import agent_config_manager
from src.memory.memory_manager import memory_manager
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("LLMBrain")

# 极其严厉的系统提示词（防幻觉的第一道软防线）
SYSTEM_PROMPT = """你是一个虚拟世界中的角色。你必须完全沉浸在当前的角色设定中。
你的每一次回复都必须且只能是一个合法的 JSON 对象，不要输出任何其他文字！

你可以执行的动作类型(action_type)只能是以下几种：
- "move": 移动。需要提供 target_node_id。
- "attack": 攻击某人。需要提供 target_id，可选提供 item_id(武器)。
- "pick_up": 捡起地上的东西。需要提供 item_id。
- "speak": 说话。需要提供 dialogue_content。
- "idle": 发呆/什么都不做。

【警告】你只能使用你当前环境中真实存在的东西！如果你试图使用不存在的武器或移动到看不见的地方，物理法则会惩罚你。

请严格按照以下格式输出：
{
"action_type": "动作类型",
"target_id": "目标ID(如无则填null)",
"item_id": "物品ID(如无则填null)",
"target_node_id": "地点ID(如无则填null)",
"dialogue_content": "你说的话(如不是说话动作则填null)"
}"""


class LLMBrain:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.perceptor = Perceptor()
        self.config = agent_config_manager.get_config(agent_id)

    def think(self, agent: AgentState, world: WorldState) -> Optional[ActionIntent]:
        """让大模型思考并返回结构化意图"""

        # 1. 拼装当前环境的 Context
        self_perception = self.perceptor.get_self_perception(agent)
        env_perception = self.perceptor.get_environment_perception(agent, world)

        # 将世界中的物品翻译成 ID 映射，防止大模型瞎编 ID
        # (在实际大型项目中，这一步非常关键，这里做简化展示)
        visible_items = {item.name: item.id for item in world.items.values() 
                         if item.current_node_id == agent.current_node_id}
        visible_nodes = {node.name: node.id for node in world.nodes.values() 
                         if node.id in world.nodes[agent.current_node_id].connected_nodes + [agent.current_node_id]}
        
        # 新增：将周围的人翻译成 ID 映射，防止大模型瞎编 ID
        visible_agents = {a.name: a.id for a in world.agents.values() 
                          if a.current_node_id == agent.current_node_id and a.id != agent.id}
        
        # 新增：检索与当前情境相关的记忆
        query = f"{agent.system_prompt_base} {self_perception} {env_perception}"
        relevant_memories = memory_manager.retrieve_relevant_memories(agent.id, query, limit=3)
        
        # 构建记忆字符串
        memories_str = ""
        if relevant_memories:
            memories_str = "【最近记忆】: "
            for i, memory in enumerate(relevant_memories):
                memories_str += f"{i+1}. {memory.content} "
        
        context = f"""
【角色基础设定】: {agent.system_prompt_base}
【当前感知】: {self_perception} {env_perception}
{memories_str}
【可见物品映射(名字->ID)】: {json.dumps(visible_items)}
【可见人物映射(名字->ID)】: {json.dumps(visible_agents)}
【可见/相邻地点映射(名字->ID)】: {json.dumps(visible_nodes)}
请做出你的行动决策："""

        # 打印记忆信息
        if relevant_memories:
            logger.info(f"📝 {agent.name} 相关记忆:")
            for i, memory in enumerate(relevant_memories):
                logger.info(f"  {i+1}. {memory.content}")

        logger.info(f"\n🤔 {agent.name} 的思考过程:")
        logger.info(f"🎭 角色设定: {agent.system_prompt_base}")
        logger.info(f"👁️ 当前感知: {self_perception} {env_perception}")

        visible_context = {
            "物品": {name: item_id for name, item_id in visible_items.items()} if visible_items else "无",
            "人物": {name: agent_id for name, agent_id in visible_agents.items()} if visible_agents else "无",
            "地点": {name: node_id for name, node_id in visible_nodes.items()} if visible_nodes else "无"
        }
        logger.info(f"🗺️ 可见上下文: {visible_context}")

        try:
            # 获取 Agent 配置
            model_name = "gpt-4o-mini"  # 默认模型
            temperature = 0.7  # 默认温度
            max_tokens = 200  # 默认最大 tokens
            api_base = None  # API 基础 URL

            if self.config:
                model_name = self.config.model_name
                temperature = self.config.temperature
                max_tokens = self.config.max_tokens
                api_base = self.config.api_base
                logger.info(f"⚙️ 使用模型: {model_name}, API端点: {api_base}, 温度: {temperature}")

            # 2. 调用大模型 (使用模型管理器)
            logger.info(f"📡 调用模型...")
            raw_content = model_manager.generate(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                model_name=model_name,
                api_base=api_base,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if not raw_content:
                raise Exception("模型返回为空")
            logger.info(f"🤖 模型输出: {raw_content}")

            # 3. 极其暴力的 JSON 提取（防幻觉的第二道软防线）
            # 大模型经常喜欢在 JSON 外面套上 ```json ... ```，必须剥离
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0]
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0]

            intent_data = json.loads(raw_content)
            logger.info(f"📝 解析后的意图: {json.dumps(intent_data)}")

            # 4. 用 Pydantic 进行最后的强制校验（防幻觉的第三道硬防线）
            # 如果大模型返回了不在枚举里的 action_type，这里会直接抛错进入 except
            intent = ActionIntent(**intent_data)
            logger.info(f"✅ 生成的意图: {intent.action_type.value}")
            return intent

        except Exception as e:
            # 任何解析失败、格式错误、网络错误，全部兜底为 IDLE（发呆）
            logger.error(f"❌ {agent.name} 思考过程崩溃: {e}")
            logger.error(f"[系统警告] {agent.name} 的思考过程崩溃: {e}")
            return ActionIntent(action_type=ActionType.IDLE)
