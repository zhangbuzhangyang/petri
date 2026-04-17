import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.core.logger import get_logger

# 尝试导入 OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 加载环境变量
load_dotenv()

# 获取日志器
logger = get_logger("ModelManager")

class ModelInstance:
    """
    单个模型实例，包含模型配置和客户端
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.model_name = model_name
        # 如果传入了参数，使用传入的参数；否则使用环境变量
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.api_base = api_base if api_base is not None else os.getenv("OPENAI_API_BASE", "")
        self.client = None
        self.is_local = False

        # 检查是否是本地模型
        if model_name.startswith("ollama/") or "localhost" in (self.api_base or "") or "ollama" in (self.api_base or ""):
            self.is_local = True
            logger.info(f"初始化本地模型: {self.model_name}, API端点: {self.api_base}")
        else:
            # 初始化 OpenAI 客户端
            if OPENAI_AVAILABLE and self.api_key:
                try:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.api_base if self.api_base else None
                    )
                    logger.info(f"OpenAI 客户端初始化完成，使用模型: {self.model_name}")
                except Exception as e:
                    logger.error(f"OpenAI 客户端初始化失败: {e}")
            else:
                logger.warning("OpenAI SDK 不可用或 API 密钥未配置")

    def generate(self, messages: list, **kwargs) -> Optional[str]:
        """
        调用大模型生成文本

        Args:
            messages: 消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            **kwargs: 额外的参数，如 temperature, max_tokens 等

        Returns:
            生成的文本内容，如果失败则返回 None
        """
        try:
            logger.debug(f"调用模型 {self.model_name} 生成文本")

            # 默认参数
            default_params = {
                "temperature": 0.7,
                "max_tokens": 200
            }

            # 合并参数
            params = {**default_params, **kwargs}

            # 处理本地模型
            if self.is_local:
                # 对于本地模型，使用与 OpenAI 兼容的 API
                if self.client:
                    # 本地模型可能需要调整模型名称
                    local_model_name = self.model_name.replace("ollama/", "")
                    response = self.client.chat.completions.create(
                        model=local_model_name,
                        messages=messages,
                        **params
                    )

                    # 提取内容
                    content = response.choices[0].message.content.strip()
                    logger.debug(f"本地模型响应: {content[:100]}...")
                    return content
                else:
                    # 如果没有客户端，尝试使用 HTTP 请求调用本地模型
                    try:
                        import requests

                        # 构建请求 - Ollama 原生 API
                        base_url = self.api_base.replace("/v1", "") if self.api_base else "http://localhost:11434"
                        url = f"{base_url}/api/chat"
                        payload = {
                            "model": self.model_name.replace("ollama/", ""),
                            "messages": messages,
                            "stream": False
                        }

                        logger.info(f"正在调用本地模型: {url}")

                        # 发送请求
                        response = requests.post(url, json=payload, timeout=60)
                        response.raise_for_status()

                        # 解析响应
                        result = response.json()
                        content = result.get("message", {}).get("content", "").strip()
                        logger.debug(f"本地模型响应: {content[:100]}...")
                        return content
                    except Exception as e:
                        logger.error(f"本地模型调用失败: {e}")
                        return None
            else:
                # 使用 OpenAI SDK 调用模型
                if self.client:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        **params
                    )

                    # 提取内容
                    content = response.choices[0].message.content.strip()
                    logger.debug(f"模型响应: {content[:100]}...")
                    return content
                else:
                    logger.error("OpenAI 客户端未初始化，无法调用模型")
                    return None

        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            return None

class ModelManager:
    """
    模型管理器，负责管理多个模型实例
    """
    def __init__(self):
        # 存储模型实例
        self.model_instances: Dict[str, ModelInstance] = {}

        # 创建默认模型实例
        default_model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.get_or_create_model_instance(default_model_name)

    def get_or_create_model_instance(self, model_name: str, api_key: Optional[str] = None, api_base: Optional[str] = None) -> ModelInstance:
        """
        获取或创建模型实例

        Args:
            model_name: 模型名称
            api_key: API 密钥（可选）
            api_base: API 基础 URL（可选）

        Returns:
            模型实例
        """
        # 创建唯一的 key，包含模型名称和 API 端点
        instance_key = f"{model_name}:{api_base or 'default'}"

        if instance_key not in self.model_instances:
            self.model_instances[instance_key] = ModelInstance(model_name, api_key, api_base)
        return self.model_instances[instance_key]

    def generate(self, messages: list, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, api_base: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        调用指定模型生成文本

        Args:
            messages: 消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            model_name: 模型名称
            api_key: API 密钥（可选）
            api_base: API 基础 URL（可选）
            **kwargs: 额外的参数，如 temperature, max_tokens 等

        Returns:
            生成的文本内容，如果失败则返回 None
        """
        model_instance = self.get_or_create_model_instance(model_name, api_key, api_base)
        return model_instance.generate(messages, **kwargs)

# 创建全局模型管理器实例
model_manager = ModelManager()
