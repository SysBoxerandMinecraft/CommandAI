"""
基于 OpenAI API 的后端（需联网和 API Key）
"""
from typing import List, Dict, Any
from .base import ModelBackend

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("请安装 openai: pip install openai")

class OpenAIBackend(ModelBackend):
    def __init__(self):
        self.client = None
        self.model_name = None
        self._name = "unknown"

    def load(self, config: Dict[str, Any]) -> None:
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("未指定 OpenAI API Key (api_key)")
        base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.model_name = config.get('model', 'gpt-3.5-turbo')
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self._name = self.model_name

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.client is None:
            raise RuntimeError("OpenAI 客户端未初始化")

        params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 512),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
        }
        # 可选参数
        if 'frequency_penalty' in kwargs:
            params['frequency_penalty'] = kwargs['frequency_penalty']
        if 'presence_penalty' in kwargs:
            params['presence_penalty'] = kwargs['presence_penalty']

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content.strip()

    def unload(self):
        self.client = None

    @property
    def model_name(self):
        return self._name