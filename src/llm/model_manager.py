import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.core.logger import get_logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

load_dotenv()

logger = get_logger("ModelManager")

class ModelType:
    OPENAI = "openai"
    VOLCANO = "volcano"
    SILICONFLOW = "siliconflow"
    OLLAMA = "ollama"
    QWEN = "qwen"
    OTHER = "other"
    OMLX = "omlx"

class ModelInstance:
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_base: Optional[str] = None, model_type: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.api_base = api_base if api_base is not None else os.getenv("OPENAI_API_BASE", "")
        self.client = None
        
        # 如果显式指定了模型类型，使用指定的类型
        if model_type and model_type in [ModelType.OPENAI, ModelType.VOLCANO, ModelType.SILICONFLOW, ModelType.OLLAMA, ModelType.QWEN, ModelType.OTHER, ModelType.OMLX]:
            self.model_type = model_type
            logger.info(f"使用显式指定的模型类型: {self.model_type}")
        else:
            # 否则自动检测模型类型
            self.model_type = self._detect_model_type()

        logger.info(f"初始化模型: {self.model_name}, 类型: {self.model_type}, API端点: {self.api_base}")

        self._initialize_client()

    def _detect_model_type(self) -> str:
        """检测模型类型"""
        if "volces.com" in (self.api_base or ""):
            return ModelType.VOLCANO
        elif "siliconflow" in (self.api_base or ""):
            return ModelType.SILICONFLOW
        elif self.model_name.startswith("ollama/") or "ollama" in (self.api_base or "") or ":11434" in (self.api_base or ""):
            return ModelType.OLLAMA
        elif "qwen" in (self.model_name or "").lower() or ("localhost" in (self.api_base or "") and ":11434" not in (self.api_base or "")):
            return ModelType.QWEN
        elif self.api_base:
            return ModelType.OTHER
        else:
            return ModelType.OPENAI

    def _initialize_client(self):
        """初始化模型客户端"""
        if self.model_type in [ModelType.OPENAI, ModelType.OTHER] and OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base if self.api_base else None
                )
                logger.info(f"OpenAI 客户端初始化完成")
            except Exception as e:
                logger.error(f"OpenAI 客户端初始化失败: {e}")
        else:
            logger.info(f"使用 HTTP 请求处理 {self.model_type} 模型")

    def _build_request(self, messages: list, params: dict) -> tuple:
        """构建请求参数"""
        if self.model_type in [ModelType.VOLCANO, ModelType.SILICONFLOW, ModelType.OTHER, ModelType.QWEN, ModelType.OMLX]:
            url = f"{self.api_base}/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": params.get("max_tokens", 2000),
                "temperature": params.get("temperature", 0.7)
            }

            if self.model_type in [ModelType.QWEN, ModelType.OMLX]:
                payload["extra_body"] = {"enable_thinking": False}
                payload["think"] = False

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            return url, payload, headers
        else:
            base_url = self.api_base.replace("/v1", "") if self.api_base else "http://localhost:11434"
            url = f"{base_url}/api/chat"
            payload = {
                "model": self.model_name.replace("ollama/", ""),
                "messages": messages,
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            return url, payload, headers

    def _parse_response(self, response_json: dict) -> str:
        """解析响应"""
        if "choices" in response_json:
            message = response_json.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "").strip()
            
            # 处理 Ollama 的 reasoning 字段
            if not content and "reasoning" in message:
                content = message.get("reasoning", "").strip()
                logger.info(f"从 Ollama reasoning 字段提取内容: {content[:100]}...")
            
            return content
        else:
            message = response_json.get("message", {})
            content = message.get("content", "").strip()
            
            # 处理 Ollama 格式的响应
            if not content and "reasoning" in message:
                content = message.get("reasoning", "").strip()
                logger.info(f"从 Ollama reasoning 字段提取内容: {content[:100]}...")
            
            return content

    def generate(self, messages: list, **kwargs) -> Optional[str]:
        """
        调用大模型生成文本
        """
        try:
            logger.debug(f"调用模型 {self.model_name} 生成文本")

            default_params = {
                "temperature": 0.7,
                "max_tokens": 2000
            }

            params = {**default_params, **kwargs}

            if self.client and self.model_type not in [ModelType.QWEN, ModelType.OMLX]:
                create_params = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": params.get("temperature", 0.7),
                    "max_tokens": params.get("max_tokens", 2000)
                }

                response = self.client.chat.completions.create(**create_params)
                content = response.choices[0].message.content.strip()
                logger.debug(f"模型响应: {content[:100]}...")
                return content
            else:
                import requests

                url, payload, headers = self._build_request(messages, params)
                logger.info(f"正在调用 {self.model_type} API: {url}")

                response = requests.post(url, json=payload, headers=headers, timeout=120)
                response.raise_for_status()

                result = response.json()
                content = self._parse_response(result)
                logger.debug(f"{self.model_type} 模型响应: {content[:100]}...")
                return content

        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            return None

class ModelManager:
    def __init__(self):
        self.model_instances: Dict[str, ModelInstance] = {}
        default_model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.get_or_create_model_instance(default_model_name)

    def get_or_create_model_instance(self, model_name: str, api_key: Optional[str] = None, api_base: Optional[str] = None, model_type: Optional[str] = None) -> ModelInstance:
        instance_key = f"{model_name}:{api_base or 'default'}:{model_type or 'auto'}"

        if instance_key not in self.model_instances:
            self.model_instances[instance_key] = ModelInstance(model_name, api_key, api_base, model_type)
        return self.model_instances[instance_key]

    def generate(self, messages: list, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, api_base: Optional[str] = None, model_type: Optional[str] = None, **kwargs) -> Optional[str]:
        model_instance = self.get_or_create_model_instance(model_name, api_key, api_base, model_type)
        return model_instance.generate(messages, **kwargs)

_model_manager_instance = None

def get_model_manager() -> 'ModelManager':
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance

class _ModelManagerProxy:
    def __getattr__(self, name):
        return getattr(get_model_manager(), name)

model_manager = _ModelManagerProxy()
