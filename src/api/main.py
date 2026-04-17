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
# 时间控制状态
tick_interval = 1.0  # 秒
is_paused = False

# 处理根路径，返回API信息
@app.get("/")
async def read_root():
    return {"message": "Project Petri API", "version": "0.1", "status": "running"}

# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global engine, tick_interval, is_paused

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

        # 重置时间控制状态
        tick_interval = 1.0
        is_paused = False

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
            # 处理控制消息（暂停、加速等）
            try:
                control_message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.1
                )
                msg_type = control_message.get("type")
                if msg_type == "pause":
                    is_paused = True
                    print("⏸️ 游戏已暂停")
                    await websocket.send_json({
                        "type": "control",
                        "action": "pause",
                        "timestamp": get_timestamp()
                    })
                elif msg_type == "resume":
                    is_paused = False
                    print("▶️ 游戏已恢复")
                    await websocket.send_json({
                        "type": "control",
                        "action": "resume",
                        "timestamp": get_timestamp()
                    })
                elif msg_type == "speed":
                    speed = control_message.get("speed", 1)
                    tick_interval = 1.0 / speed
                    print(f"⏩ 游戏速度: x{speed}")
                    await websocket.send_json({
                        "type": "control",
                        "action": "speed",
                        "speed": speed,
                        "timestamp": get_timestamp()
                    })
            except asyncio.TimeoutError:
                pass

            # 如果暂停则继续等待
            if is_paused:
                await asyncio.sleep(0.1)
                continue

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
            print(f"⏱️ 等待 {tick_interval} 秒...")
            await asyncio.sleep(tick_interval)

    except WebSocketDisconnect:
        print("🔌 客户端断开连接")
    except Exception as e:
        print(f"❌ 错误: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    
    # 配置 Uvicorn 支持优雅停机
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=9000,
        graceful_shutdown_timeout=5,  # 最多等待5秒让现有请求完成
        handle_signals=True  # 自动处理 SIGINT (Ctrl+C) 和 SIGTERM
    )
    server = uvicorn.Server(config)
    
    # 捕获键盘中断，强制退出
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n🛑 收到停止信号，正在关闭服务...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server.run()