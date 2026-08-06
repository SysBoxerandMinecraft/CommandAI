"""
配置管理：加载/保存 YAML 配置文件
"""
import os
import yaml
from typing import Dict, Any

DEFAULT_CONFIG = {
    "model": {
        "type": "deepseek",
        "api_key": "your-api-key-here",
        "model": "deepseek-chat",
    },
    "generation": {
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9
    },
    "context": {
        "max_history_turns": 10,
        "system_prompt": "You are a helpful AI assistant."
    },
    "logging": {
        "level": "INFO"
    }
}

# OpenAI配置模板
OPENAI_CONFIG_TEMPLATE = {
    "model": {
        "type": "openai",
        "api_key": "your-api-key-here",  # 替换为你的OpenAI API Key
        "model": "gpt-3.5-turbo",         # 可选: gpt-4, gpt-4-turbo-preview等
        "base_url": "https://api.openai.com/v1"  # 可选: 用于兼容OpenAI格式的API
    },
    "generation": {
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9
    },
    "context": {
        "max_history_turns": 10,
        "system_prompt": "You are a helpful AI assistant."
    },
    "logging": {
        "level": "INFO"
    }
}

def load_config(config_path: str) -> Dict[str, Any]:
    """从 YAML 文件加载配置，若文件不存在则返回默认配置"""
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy()
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # 合并默认值（简单合并，可递归完善）
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    return merged

def save_config(config_path: str, config: Dict[str, Any]):
    """保存配置到 YAML 文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)