from dotenv import load_dotenv
import os
from src.llm.model_manager import model_manager

# 加载环境变量
load_dotenv()

print("=== 测试火山引擎模型调用 ===")

# 测试消息
messages = [
    {"role": "user", "content": "你好，测试消息"}
]

# 调用火山引擎模型
try:
    response = model_manager.generate(
        messages=messages,
        model_name=os.getenv("VOLCANO_MODEL_NAME", "glm-4-7-251222"),
        api_key=os.getenv("VOLCANO_API_KEY", "ark-e56a0023-b874-4a94-ab46-c0bda288f4a7-eb629"),
        api_base=os.getenv("VOLCANO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
    )
    print(f"响应: {response}")
except Exception as e:
    print(f"错误: {e}")
