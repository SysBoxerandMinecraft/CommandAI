"""
基于 llama-cpp-python 的 GGUF 模型后端
"""
import os
from typing import List, Dict, Any
from .base import ModelBackend
from utils.file_utils import resolve_path

try:
    from llama_cpp import Llama
except ImportError:
    raise ImportError("请安装 llama-cpp-python: pip install llama-cpp-python")

class LlamaCppBackend(ModelBackend):
    def __init__(self):
        self.model = None
        self._name = "unknown"

    def load(self, config: Dict[str, Any]) -> None:
        model_path = config.get('path')
        if not model_path:
            raise ValueError("未指定模型路径 (path)")
        # 解析路径（相对路径转为绝对）
        model_path = resolve_path(model_path)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 从配置中提取 llama 特定参数
        llama_kwargs = config.get('llama_kwargs', {})
        # 默认参数
        default_kwargs = {
            'n_ctx': 2048,
            'n_threads': 4,  # 根据 CPU 核心调整
            'verbose': False
        }
        default_kwargs.update(llama_kwargs)

        self.model = Llama(model_path=model_path, **default_kwargs)
        self._name = os.path.basename(model_path)

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.model is None:
            raise RuntimeError("模型未加载")

        # 构造 prompt（采用 ChatML 格式，适用于 TinyLlama 等）
        # 可根据模型类型调整，此处使用简单格式
        prompt = self._build_prompt(messages)

        # 准备生成参数
        gen_params = {
            'max_tokens': kwargs.get('max_tokens', 512),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'repeat_penalty': kwargs.get('repeat_penalty', 1.1),
            'echo': False
        }

        output = self.model.create_completion(prompt, **gen_params)
        return output['choices'][0]['text'].strip()

    def unload(self):
        if self.model:
            del self.model
            self.model = None

    @property
    def model_name(self):
        return self._name

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表转为模型所需的 prompt 字符串"""
        # 使用 ChatML 格式（适用于 TinyLlama, Phi-3 等）
        prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == "system":
                prompt += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"
            else:
                prompt += f"{content}\n"
        # 添加助手开始标记
        prompt += "<|im_start|>assistant\n"
        return prompt