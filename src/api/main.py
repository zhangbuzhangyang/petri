from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime
from src.core.initialization import build_initial_world
from src.core.engine import GameEngine
from src.llm.brain import LLMBrain

def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 创建 FastAPI 应用
app = FastAPI(title="Project Petri", description="AI Agent Simulation Platform")

# 全局引擎实例
engine = None

# 处理根路径，返回API信息
@app.get("/")
async def read_root():
    return {"message": "Project Petri API", "version": "0.1", "status": "running"}

# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global engine

    await websocket.accept()
    print("📡 WebSocket 连接已建立，等待客户端确认...")

    try:
        # 等待客户端发送"开始"消息
        init_message = await websocket.receive_json()
        print(f"收到客户端消息: {init_message}")

        if init_message.get("type") != "start":
            print("❌ 客户端未发送正确的开始消息")
            await websocket.close()
            return

        # 初始化世界和引擎
        print("🌍 初始化世界和引擎...")
        world = build_initial_world()
        engine = GameEngine(world)

        print("🧠 Agent 大脑已在引擎初始化时自动创建")

        # 通知客户端初始化完成，可以开始游戏
        await websocket.send_json({
            "type": "init_complete",
            "message": "初始化完成，开始游戏",
            "timestamp": get_timestamp()
        })
        print("✅ 已通知客户端初始化完成")

        # 开始游戏循环
        print("🎮 开始游戏循环...")
        tick_count = 0
        while True:
            tick_count += 1
            print(f"\n🔄 运行 Tick {tick_count}")

            # 运行一个 Tick
            await engine.run_tick_async()

            # 推送队列中的所有事件
            event_count = 0
            while not engine.is_event_queue_empty():
                event = await engine.get_event()
                await websocket.send_json(event)
                event_count += 1
            print(f"📤 推送了 {event_count} 个事件到前端")

            # 检查是否所有角色都已死亡
            all_dead = all(agent.status != "alive" for agent in engine.world.agents.values())
            if all_dead:
                # 推送游戏结束事件
                print("🎯 所有角色都已死亡，游戏结束")
                await websocket.send_json({
                    "type": "game_over",
                    "message": "所有角色都已死亡，游戏结束"
                })
                break

            # 等待一段时间再进行下一个 Tick
            print("⏱️ 等待 1 秒...")
            await asyncio.sleep(1)  # 1秒间隔

    except WebSocketDisconnect:
        print("🔌 客户端断开连接")
    except Exception as e:
        print(f"❌ 错误: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)