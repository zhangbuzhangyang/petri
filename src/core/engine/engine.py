from typing import Callable, List
import asyncio
from src.core.world_state import WorldState, AgentState, ActionIntent, ActionType, AgentStatus
from src.core.rule_engine import RuleEngine, Judgement
from src.core.engine.state_manager import StateManager
from src.core.engine.memory_integrator import MemoryIntegrator
from src.core.engine.brain_manager import BrainManager
from src.core.engine.event_broadcaster import EventBroadcaster
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("PetriEngine")

class GameEngine:
    def __init__(self, world_state: WorldState):
        self.world = world_state
        self.rule_engine = RuleEngine()
        
        # 初始化各个模块
        self.state_manager = StateManager(self.world)
        self.memory_integrator = MemoryIntegrator()
        self.brain_manager = BrainManager()
        self.event_broadcaster = EventBroadcaster()
        
        # 自动初始化 Agent 大脑
        self.brain_manager.initialize_brains(list(self.world.agents.keys()))

    def run_tick(self):
        """
        推进一个时间切片（世界心跳一次）
        同步版本，用于命令行测试
        """
        self.world.tick_count += 1
        logger.info(f"\n{'='*20} [Tick {self.world.tick_count}] {'='*20}")
        
        # 1. 环境步进：所有活人饥饿度 +1
        for agent in self.world.agents.values():
            if agent.status == AgentStatus.ALIVE:
                agent.hunger = min(100, agent.hunger + 1)

        # 2. 收集所有活人的意图并依次结算
        alive_agents = [a for a in self.world.agents.values() if a.status == AgentStatus.ALIVE]
        
        for agent in alive_agents:
            # 获取意图 (使用真实的 LLM 大脑)
            brain = self.brain_manager.get_brain(agent.id)
            intent = brain.think(agent, self.world)
            
            if not intent:
                continue

            # 3. 规则引擎裁决
            judgement: Judgement = self.rule_engine.judge(intent, agent, self.world)
            
            # 4. 控制台输出剧情 (上帝视角)
            if intent.action_type == ActionType.SPEAK:
                logger.info(f"💬 [{agent.name}] 说: \"{intent.dialogue_content}\"")
            else:
                status_icon = "✅" if judgement.success else "🚫"
                logger.info(f"🎯 [{agent.name}] 意图: {intent.action_type.value} | 判决: {status_icon} {judgement.reason}")

            # 5. 应用状态变更 (核心物理法则生效时刻)
            if judgement.success and judgement.state_deltas:
                self.state_manager.apply_state_deltas(judgement.state_deltas)
            
            # 6. 为 Agent 添加记忆
            self.memory_integrator.add_memory(agent, intent, judgement)
        
        # 打印当前世界快照
        self._print_world_snapshot()

    async def run_tick_async(self):
        """
        异步版本，适配 FastAPI 的 WebSocket
        """
        self.world.tick_count += 1
        
        # 构造一个 Tick 报头推送给前端
        await self.event_broadcaster.broadcast_tick_header(self.world.tick_count)
        
        # 1. 环境步进：所有活人饥饿度 +1
        for agent in self.world.agents.values():
            if agent.status == AgentStatus.ALIVE:
                agent.hunger = min(100, agent.hunger + 1)

        # 2. 收集所有活人的意图并依次结算
        alive_agents = [a for a in self.world.agents.values() if a.status == AgentStatus.ALIVE]
        
        for agent in alive_agents:
            # 获取意图 (使用真实的 LLM 大脑)
            brain = self.brain_manager.get_brain(agent.id)
            intent = brain.think(agent, self.world)
            
            if not intent:
                continue

            # 3. 规则引擎裁决
            judgement: Judgement = self.rule_engine.judge(intent, agent, self.world)
            
            # 4. 广播事件给前端
            if intent.action_type == ActionType.SPEAK:
                await self.event_broadcaster.broadcast_dialogue(agent, intent.dialogue_content)
            else:
                await self.event_broadcaster.broadcast_action(agent, intent, judgement)

            # 5. 应用状态变更 (核心物理法则生效时刻)
            if judgement.success and judgement.state_deltas:
                self.state_manager.apply_state_deltas(judgement.state_deltas)
            
            # 6. 为 Agent 添加记忆
            self.memory_integrator.add_memory(agent, intent, judgement)
        
        # 7. 广播状态快照给前端
        await self.event_broadcaster.broadcast_state_snapshot(self.world)

    def _print_world_snapshot(self):
        """
        打印当前世界快照
        """
        logger.info("-" * 40)
        for agent in self.world.agents.values():
            status_str = f"❤️{agent.hp} 🍖{agent.hunger} 背包:{agent.inventory}"
            if agent.status == AgentStatus.DEAD:
                status_str = "💀 已死亡"
            logger.info(f"  > {agent.name}: {status_str}")

    async def get_event(self):
        """
        获取队列中的事件
        """
        return await self.event_broadcaster.get_event()

    def is_event_queue_empty(self):
        """
        检查事件队列是否为空
        """
        return self.event_broadcaster.is_empty()
