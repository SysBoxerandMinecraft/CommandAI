"""
基于 Ollama 本地服务的后端（需预先安装 Ollama 并运行）
"""
from typing import List, Dict, Any
from .base import ModelBackend
import requests
import json

class OllamaBackend(ModelBackend):
    def __init__(self):
        self.base_url = None
        self.model_name = None
        self._name = "unknown"

    def load(self, config: Dict[str, Any]) -> None:
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model_name = config.get('model', 'llama2')
        if not self.model_name:
            raise ValueError("未指定 Ollama 模型名称 (model)")

        # 测试连接
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model_name, "prompt": "ping", "stream": False},
                timeout=5
            )
            if response.status_code != 200:
                raise ConnectionError(f"Ollama 服务返回错误: {response.text}")
        except Exception as e:
            raise ConnectionError(f"无法连接到 Ollama 服务: {e}")

        self._name = self.model_name

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if not self.base_url:
            raise RuntimeError("Ollama 未加载")

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9),
                "repeat_penalty": kwargs.get('repeat_penalty', 1.1),
            }
        }
        # 添加 max_tokens
        if 'max_tokens' in kwargs:
            payload['options']['num_predict'] = kwargs['max_tokens']

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=60
        )
        if response.status_code != 200:
            raise RuntimeError(f"Ollama 请求失败: {response.text}")

        data = response.json()
        return data.get('message', {}).get('content', '').strip()

    def unload(self):
        # 无需特殊操作
        pass

    @property
    def model_name(self):
        return self._name