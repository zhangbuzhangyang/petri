import requests

# 测试 OMLX 模型
url = "http://127.0.0.1:56788/v1/chat/completions"
payload = {
    "model": "Qwen3.5-9B-MLX-4bit",
    "messages": [
        {"role": "user", "content": "输出一个JSON: {\"action\": \"idle\"}"}
    ],
    "think": False,  # 禁用思考
    "max_tokens": 200
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers, timeout=60)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
