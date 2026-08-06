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

def main():
    # 设置日志
    logger = setup_logger()
    logger.info("Starting CommandAI")

    # 加载配置（若不存在则创建默认）
    config_path = "userconfig.yaml"
    if not os.path.exists(config_path):
        logger.info("配置文件不存在，创建默认配置")
        save_config(config_path, get_default_config())
    config = load_config(config_path)

    # 创建 Agent 并加载模型
    try:
        agent = Agent(config)
    except Exception as e:
        logger.error(f"初始化 Agent 失败: {e}")
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
            "type": "llama",
            "path": "models/tinyllama-1.1b-chat-q4_k_m.gguf"
        },
        "generation": {
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1
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