import asyncio
from typing import Dict, Any
from datetime import datetime
from src.core.world_state import AgentState, ActionIntent, ActionType, AgentStatus
from src.core.rule_engine import Judgement
from src.core.logger import get_logger

# 获取日志器
logger = get_logger("EventBroadcaster")

def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class EventBroadcaster:
    """
    事件广播器，负责向前端推送事件
    """
    def __init__(self):
        # 事件队列
        self.event_queue: asyncio.Queue = asyncio.Queue()

    async def broadcast_tick_header(self, tick: int):
        """
        广播 Tick 报头
        """
        await self.event_queue.put({
            "type": "tick_header",
            "tick": tick,
            "timestamp": get_timestamp()
        })
        logger.debug(f"广播 Tick 报头: {tick}")

    async def broadcast_dialogue(self, agent: AgentState, content: str):
        """
        广播对话事件
        """
        await self.event_queue.put({
            "type": "dialogue",
            "agent_name": agent.name,
            "agent_id": agent.id,
            "content": content,
            "timestamp": get_timestamp()
        })
        logger.debug(f"广播对话事件: {agent.name} 说: {content[:50]}...")

    async def broadcast_action(self, agent: AgentState, intent: ActionIntent, judgement: Judgement):
        """
        广播动作事件
        """
        await self.event_queue.put({
            "type": "action",
            "agent_name": agent.name,
            "agent_id": agent.id,
            "intent": intent.action_type.value,
            "success": judgement.success,
            "reason": judgement.reason,
            "is_hallucination": "幻觉拦截" in judgement.reason,
            "timestamp": get_timestamp()
        })
        logger.debug(f"广播动作事件: {agent.name} 尝试 {intent.action_type.value}")

    async def broadcast_state_snapshot(self, world):
        """
        广播状态快照
        """
        await self.event_queue.put({
            "type": "state_snapshot",
            "agents": {
                aid: {
                    "name": a.name, "hp": a.hp, "hunger": a.hunger,
                    "status": a.status.value, "inventory": a.inventory,
                    "node": a.current_node_id
                } for aid, a in world.agents.items()
            },
            "nodes": {
                nid: {
                    "id": n.id, "name": n.name, "description": n.description,
                    "agents": [agent_id for agent_id, agent in world.agents.items() if agent.current_node_id == nid]
                } for nid, n in world.nodes.items()
            },
            "timestamp": get_timestamp()
        })
        logger.debug("广播状态快照")

    async def broadcast_game_over(self):
        """
        广播游戏结束事件
        """
        await self.event_queue.put({
            "type": "game_over",
            "message": "所有角色都已死亡，游戏结束",
            "timestamp": get_timestamp()
        })
        logger.info("广播游戏结束事件")

    async def get_event(self):
        """
        获取队列中的事件
        """
        return await self.event_queue.get()

    def is_empty(self):
        """
        检查队列是否为空
        """
        return self.event_queue.empty()
