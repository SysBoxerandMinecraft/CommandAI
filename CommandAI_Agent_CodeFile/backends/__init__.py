"""
模型后端工厂：根据类型创建对应的后端实例
"""
from .base import ModelBackend
from importlib import import_module

# 使用字符串路径，避免提前导入
BACKEND_MAP = {
    'llama': 'llama_backend.LlamaCppBackend',
    'transformers': 'transformers_backend.TransformersBackend',
    'ollama': 'ollama_backend.OllamaBackend',
    'openai': 'openai_backend.OpenAIBackend',
}


def create_backend(model_type: str) -> ModelBackend:
    """工厂函数，动态导入后端类，仅在需要时加载依赖"""
    model_type = model_type.lower()
    if model_type not in BACKEND_MAP:
        raise ValueError(f"不支持的模型类型: {model_type}，可选: {list(BACKEND_MAP.keys())}")

    module_path, class_name = BACKEND_MAP[model_type].rsplit('.', 1)
    try:
        # 使用 importlib 动态导入模块
        module = import_module(f'backends.{module_path}')
        backend_class = getattr(module, class_name)
        return backend_class()
    except ImportError as e:
        raise ImportError(
            f"加载 '{model_type}' 后端失败，请安装所需依赖: {e}\n"
            f"对于 llama 后端，请安装: pip install llama-cpp-python\n"
            f"对于 transformers 后端，请安装: pip install transformers torch bitsandbytes\n"
            f"对于 ollama 后端，请安装: pip install requests\n"
            f"对于 openai 后端，请安装: pip install openai"
        )