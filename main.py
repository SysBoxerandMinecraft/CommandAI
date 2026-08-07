#!/usr/bin/env python3
"""
CommandAI - 命令行 AI Agent 主入口
"""
import sys
import os
from config import load_config, save_config
from agent import Agent
from cli import CommandLineInterface
from utils.logger import setup_logger

def ensure_models_dir(config):
    """如果使用本地模型，检查并创建 models 目录，提示用户放入模型文件"""
    model_cfg = config.get('model', {})
    model_type = model_cfg.get('type', '')

    if model_type not in ('llama', 'transformers'):
        return

    # 创建 models 文件夹
    models_dir = os.path.join(os.getcwd(), 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"\n[提示] 已创建模型文件夹: {models_dir}")

    # 检查模型文件是否存在
    model_path = model_cfg.get('path', '')
    if not model_path:
        print(f"\n[提示] 当前使用 {model_type} 本地模型，但未配置模型路径。")
        print(f"  请将模型文件放入 models/ 文件夹，")
        print(f"  并在 userconfig.yaml 中设置 model.path")
        return

    # 处理相对路径
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.getcwd(), model_path)

    if not os.path.exists(model_path):
        print(f"\n[警告] 模型文件不存在: {model_path}")
        print(f"  请将模型文件放入 models/ 文件夹，")
        print(f"  并在 userconfig.yaml 中设置正确的 model.path")
    else:
        print(f"[信息] 模型文件已找到: {model_path}")


def main():
    # 设置日志
    logger = setup_logger()
    logger.info("Starting CommandAI")

    # 加载配置（若不存在则创建默认）
    config_path = "userconfig.yaml"
    if not os.path.exists(config_path):
        logger.info("配置文件不存在，创建默认配置")
        save_config(config_path, get_default_config())
        print(f"[信息] 已创建默认配置文件: {os.path.abspath(config_path)}")
        print(f"[信息] 请编辑此文件填入你的 API Key 后重新运行。\n")
    config = load_config(config_path)

    # 检查本地模型文件
    ensure_models_dir(config)

    # 创建 Agent 并加载模型
    try:
        agent = Agent(config)
    except Exception as e:
        logger.error(f"初始化 Agent 失败: {e}")
        model_type = config.get('model', {}).get('type', 'unknown')
        print(f"\n[错误] 初始化 Agent 失败: {e}")
        print(f"\n当前模型类型: {model_type}")
        if model_type in ('llama', 'transformers'):
            print("\n检测到使用本地模型后端，常见原因:")
            print("  1. 缺少模型文件 (GGUF)，请将文件放入 models/ 文件夹")
            print("  2. llama-cpp-python 的 DLL 依赖缺失 (需安装 Visual C++ Redistributable)")
            print("\n建议: 在 userconfig.yaml 中将 type 改为 'deepseek' 等使用 API 调用")
        elif model_type in ('openai', 'kimi', 'deepseek', 'glm', 'qwen'):
            print(f"\n请检查 userconfig.yaml 中的 api_key 是否正确设置。")
        print(f"\n配置文件路径: {os.path.abspath(config_path)}")
        sys.exit(1)

    # 启动 CLI
    cli = CommandLineInterface(agent, config_path)
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
    finally:
        # 清理资源
        if agent.backend:
            agent.backend.unload()
        logger.info("CommandAI 已退出")

def get_default_config():
    """返回默认配置字典"""
    return {
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

if __name__ == "__main__":
    main()