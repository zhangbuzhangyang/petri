# Project Petri - AI Agent 模拟平台

Project Petri 是一个 AI Agent 模拟平台，通过大语言模型驱动虚拟世界中的智能体，实现自主决策、社交互动和经济活动的仿真系统。

## 🎯 项目简介

Petri 是一个基于大语言模型的多智能体模拟系统，灵感来自"培养皿中的生命演化"。在这个虚拟世界中，AI 角色能够：

- **自主决策**：基于当前环境和记忆做出行动决策
- **社交互动**：与其他 Agent 进行对话和交易
- **经济活动**：买卖物品、积累财富
- **记忆系统**：基于 RAG 的长期记忆检索
- **物理法则**：遵循预定义的规则引擎

## ✨ 核心特性

### 🤖 智能 Agent 系统
- 基于 LLM 的决策引擎（支持 GPT-4o、Qwen、Ollama 等模型）
- 性格化的 System Prompt 配置
- 完整的感知-决策-执行循环
- 记忆整合与检索系统

### 🎮 上帝视角控制台
- **左侧空间拓扑图**：实时显示 Agent 位置，死亡角色红色高亮
- **中间事件流**：颜色高亮区分动作、对话、拦截事件
- **右侧状态面板**：显示血条、饥饿度、背包等详细状态
- **灵魂解剖台**：一键展开 Agent 的完整 Prompt 和记忆
- **时间控制台**：支持 x2/x5 加速、暂停功能

### 💰 经济系统
- 市场交易机制
- 物品生产与消费
- 金币流通系统
- 动态定价

### 📡 实时通信
- WebSocket 实时推送事件和状态
- 支持暂停/恢复/加速控制
- 游戏结束检测（所有 Agent 死亡）

## 🏗️ 技术架构

```
petri/
├── src/
│   ├── agents/           # Agent 认知系统
│   │   └── cognitive.py  # 感知器（环境、自我感知）
│   ├── api/              # FastAPI Web 服务
│   │   └── main.py       # WebSocket 端点
│   ├── core/             # 核心引擎
│   │   ├── engine/       # 游戏引擎
│   │   ├── initialization/  # 世界初始化
│   │   ├── rule_engine/  # 规则引擎
│   │   └── world_state/  # 世界状态管理
│   ├── llm/              # LLM 集成
│   │   ├── brain.py      # Agent 大脑（决策）
│   │   └── model_manager.py  # 模型管理器
│   └── memory/           # 记忆系统
│       └── memory_manager.py  # RAG 记忆管理
├── tests/                # 测试文件
├── petri-web/           # 前端项目（独立部署）
└── main.py              # 入口文件
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+（前端）
- 支持的 LLM API 或本地 Ollama

### 1. 安装依赖

```bash
# 安装后端依赖
cd petri
pip install -r requirements.txt
# 或使用 uv
uv sync

# 安装前端依赖
cd petri-web
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
```

### 3. 启动后端

```bash
cd petri
python main.py
# 或使用 uv
uv run python main.py
```

后端服务将在 `http://localhost:9000` 启动。

### 4. 启动前端

```bash
cd petri-web
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### 5. 开始模拟

1. 打开浏览器访问 `http://localhost:5173`
2. 等待 WebSocket 连接建立
3. 点击"开始"按钮启动模拟
4. 使用右上角的时间控制台调整速度或暂停

## ⚙️ 配置指南

### Agent 配置

在 `src/core/agent_config.py` 中配置 Agent：

```python
AgentConfig(
    name="角色名称",
    system_prompt_base="角色设定描述",
    model_name="gpt-4o-mini",      # 模型名称
    model_type="openai",           # 模型类型：openai/ollama/qwen/omlx
    api_key="your_api_key",        # API 密钥
    api_base="https://api.openai.com/v1",  # API 端点
    temperature=0.7,                # 生成温度
    max_tokens=200                  # 最大生成 token 数
)
```

### 模型类型支持

| 类型 | 说明 | API 端点示例 |
|------|------|-------------|
| `openai` | OpenAI 官方模型 | `https://api.openai.com/v1` |
| `ollama` | Ollama 本地模型 | `http://localhost:11434` |
| `qwen` | 本地 Qwen 模型 | `http://127.0.0.1:56788/v1` |
| `omlx` | oMLX 模型 | `http://127.0.0.1:56788/v1` |

### 空间节点配置

在 `src/core/initialization/spaces/__init__.py` 中配置地图节点。

### 市场配置

在 `src/core/initialization/markets/config.py` 中配置商店物品和价格。

## 📡 WebSocket API

### 连接端点

```
ws://localhost:9000/ws
```

### 客户端发送消息

#### 开始游戏
```json
{
  "type": "start"
}
```

#### 暂停游戏
```json
{
  "type": "pause"
}
```

#### 恢复游戏
```json
{
  "type": "resume"
}
```

#### 调整速度
```json
{
  "type": "speed",
  "speed": 2
}
```

### 服务端推送消息

#### 初始化完成
```json
{
  "type": "init_complete",
  "message": "初始化完成，开始游戏",
  "timestamp": "2024-01-01 12:00:00"
}
```

#### Tick 头
```json
{
  "type": "tick_header",
  "tick": 1
}
```

#### 状态快照
```json
{
  "type": "state_snapshot",
  "agents": { ... },
  "nodes": { ... },
  "markets": { ... }
}
```

#### Agent 思考
```json
{
  "type": "agent_thinking",
  "agent_id": "agent_1",
  "agent_name": "铁匠",
  "thinking": { ... },
  "timestamp": "2024-01-01 12:00:00"
}
```

#### 事件
```json
{
  "type": "event",
  "event_type": "move",
  "agent_name": "铁匠",
  "content": "铁匠 从 酒馆 移动到 广场",
  "success": true
}
```

#### 游戏结束
```json
{
  "type": "game_over",
  "message": "所有角色都已死亡，游戏结束"
}
```

## 🎮 操作指南

### 观察模式
- 左侧面板：查看各节点位置和角色
- 中间面板：实时事件流
- 右侧面板：角色详细状态

### 时间控制
- **暂停**：停止模拟进程
- **恢复**：继续模拟
- **加速**：x1 / x2 / x5 倍速

### 灵魂解剖台
点击右下角按钮展开，可查看：
- Agent 的完整 System Prompt
- 当前上下文
- 相关记忆
- 模型输出

## 🔧 开发指南

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_model_manager.py

# 查看测试覆盖率
pytest --cov=src tests/
```

### 代码规范

项目使用 Ruff 进行代码检查：

```bash
# 检查代码
ruff check src/

# 自动修复
ruff check --fix src/
```

### 添加新动作

1. 在 `src/core/world_state/actions.py` 中定义动作枚举
2. 在 `src/core/rule_engine/actions/` 中实现动作逻辑
3. 在 `src/agents/cognitive.py` 中添加感知逻辑

### 添加新 Agent

1. 在 `src/core/initialization/agents/__init__.py` 中添加配置
2. 配置 System Prompt、初始状态和位置

## 📝 项目阶段

### V0.1 验证期 ✅
- 核心引擎和规则引擎
- LLM 集成和 JSON 输出解析
- 基础空间和物品系统
- WebSocket 通信

### V0.5 沉浸期（全视之眼）✅
- 增强前端 UI（空间拓扑图、事件流高亮）
- 异步 Tick 调度器
- 简单经济闭环
- ChromaDB 记忆系统

### V1.0 觉醒期（培养皿的主宰）🎯
- 长期记忆系统
- 性格动态漂移
- 上帝干预面板
- 派系与自发规则

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
