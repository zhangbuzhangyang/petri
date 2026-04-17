#!/bin/bash

# 项目启动脚本
echo "🚀 启动 Project Petri 项目..."

# 检查并创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "🔧 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
echo "🔗 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 安装项目依赖..."
uv add fastapi uvicorn pydantic python-dotenv openai websockets

# 启动 FastAPI 服务器
echo "🌍 启动 FastAPI 服务器..."
echo "服务器将在 http://localhost:9000 运行"
echo "按 Ctrl+C 停止服务器"

.venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 9000