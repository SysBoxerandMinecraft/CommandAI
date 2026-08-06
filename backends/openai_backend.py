"""
基于 OpenAI API 的后端（需联网和 API Key）
支持 OpenAI 及兼容其格式的国内模型: Kimi, DeepSeek, GLM, Qwen
"""
from typing import List, Dict, Any
from .base import ModelBackend

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("请安装 openai: pip install openai")

# 各提供商预设配置
PROVIDER_PRESETS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-3.5-turbo",
        "env_key": "OPENAI_API_KEY",
    },
    "kimi": {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k3",
        "env_key": "MOONSHOT_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "default_model": "glm-4-flash",
        "env_key": "ZAI_API_KEY",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
    },
}

# 各提供商的模型列表（用于参考）
PROVIDER_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "kimi": ["kimi-k3", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "glm": ["glm-4", "glm-4-flash", "glm-4-air", "glm-4-airx"],
    "qwen": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"],
}


class OpenAIBackend(ModelBackend):
    def __init__(self):
        self.client = None
        self._model_name = None
        self._name = "unknown"
        self._provider = None

    def load(self, config: Dict[str, Any]) -> None:
        # 支持 provider 字段或从 type 字段推断提供商
        provider = config.get('provider', '').lower()
        if not provider:
            # 从 type 字段推断 (kimi/deepseek/glm/qwen/openai)
            model_type = config.get('type', '').lower()
            if model_type in PROVIDER_PRESETS:
                provider = model_type

        if provider and provider in PROVIDER_PRESETS:
            preset = PROVIDER_PRESETS[provider]
            base_url = config.get('base_url', preset['base_url'])
            self._model_name = config.get('model', preset['default_model'])
            self._provider = provider
        else:
            # 直接使用显式配置
            base_url = config.get('base_url', 'https://api.openai.com/v1')
            self._model_name = config.get('model', 'gpt-3.5-turbo')
            self._provider = "custom"

        # 获取 API Key: 优先配置文件，其次环境变量
        api_key = config.get('api_key')
        if not api_key and self._provider in PROVIDER_PRESETS:
            import os
            env_key = PROVIDER_PRESETS[self._provider]['env_key']
            api_key = os.environ.get(env_key)

        if not api_key:
            raise ValueError(
                f"未指定 API Key。请在配置文件中设置 api_key，"
                f"或设置环境变量 {PROVIDER_PRESETS.get(self._provider, {}).get('env_key', 'API_KEY')}"
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self._name = self._model_name

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.client is None:
            raise RuntimeError("客户端未初始化，请先调用 load()")

        params = {
            "model": self._model_name,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 1024),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
        }

        # 可选参数（仅当提供商支持时传入）
        if 'frequency_penalty' in kwargs and self._provider not in ('qwen',):
            params['frequency_penalty'] = kwargs['frequency_penalty']
        if 'presence_penalty' in kwargs:
            params['presence_penalty'] = kwargs['presence_penalty']

        # Qwen 扩展参数通过 extra_body 传入
        if self._provider == 'qwen':
            extra_body = {}
            if kwargs.get('enable_thinking') is not None:
                extra_body['enable_thinking'] = kwargs['enable_thinking']
            if kwargs.get('thinking_budget') is not None:
                extra_body['thinking_budget'] = kwargs['thinking_budget']
            if kwargs.get('enable_search') is not None:
                extra_body['enable_search'] = kwargs['enable_search']
            if extra_body:
                params['extra_body'] = extra_body

        # 移除值为 None 的参数
        params = {k: v for k, v in params.items() if v is not None}

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content.strip()

    def generate_with_search(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        启用模型原生联网搜索来生成回复。
        仅对支持原生搜索的提供商有效（qwen, glm）。
        """
        if self.client is None:
            raise RuntimeError("客户端未初始化，请先调用 load()")

        params = {
            "model": self._model_name,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 1024),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
        }

        # 根据提供商启用原生搜索
        extra_body = {}
        if self._provider == 'qwen':
            extra_body['enable_search'] = True
        elif self._provider == 'glm':
            # GLM 通过 extra_body 传 enable_search
            extra_body['enable_search'] = True
        elif self._provider == 'kimi':
            # Kimi 通过 tools 传 web_search
            params['tools'] = [{"type": "builtin", "name": "web_search"}]

        if extra_body:
            params['extra_body'] = extra_body

        params = {k: v for k, v in params.items() if v is not None}

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content.strip()

    def unload(self):
        self.client = None

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def supports_native_search(self) -> bool:
        """是否支持模型原生联网搜索"""
        return self._provider in ('qwen', 'glm', 'kimi')
