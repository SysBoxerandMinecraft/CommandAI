"""
基于 HuggingFace Transformers 的模型后端（支持 4-bit 量化）
"""
import os
from typing import List, Dict, Any
from .base import ModelBackend

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
except ImportError:
    raise ImportError("请安装 transformers 和 torch: pip install transformers torch")

class TransformersBackend(ModelBackend):
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._name = "unknown"

    def load(self, config: Dict[str, Any]) -> None:
        model_name = config.get('model_name_or_path')
        if not model_name:
            raise ValueError("未指定模型名称或路径 (model_name_or_path)")

        # 量化配置（默认 4-bit，节省内存）
        use_4bit = config.get('load_in_4bit', True)
        if use_4bit:
            quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        else:
            quantization_config = None

        # 设备
        device_map = config.get('device', 'auto')
        if device_map == 'auto' and not torch.cuda.is_available():
            device_map = 'cpu'

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map=device_map,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        self._name = model_name

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.model is None:
            raise RuntimeError("模型未加载")

        # 应用 chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt")
        # 将输入移到模型设备
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        gen_params = {
            'max_new_tokens': kwargs.get('max_tokens', 512),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'repetition_penalty': kwargs.get('repeat_penalty', 1.1),
            'do_sample': True,
        }

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **gen_params
            )
        # 解码生成的 tokens
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        return response

    def unload(self):
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @property
    def model_name(self):
        return self._name