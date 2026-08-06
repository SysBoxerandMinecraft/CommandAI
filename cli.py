"""
命令行交互界面
支持普通对话、搜索增强和多模型切换
"""
import sys
import shlex
from agent import Agent
from config import load_config, save_config
from utils.logger import get_logger

logger = get_logger()

# 支持的 API 提供商
API_PROVIDERS = ['openai', 'kimi', 'deepseek', 'glm', 'qwen']
# 所有支持的模型类型
ALL_MODEL_TYPES = API_PROVIDERS + ['llama', 'ollama', 'transformers']


class CommandLineInterface:
    def __init__(self, agent: Agent, config_path: str):
        self.agent = agent
        self.config_path = config_path
        self.running = True

    def run(self):
        print("\n" + "="*50)
        print("CommandAI - 命令行 AI Agent")
        provider = getattr(self.agent.backend, 'provider', None)
        if provider:
            print(f"当前模型: {self.agent.backend.model_name} ({provider})")
        else:
            print(f"当前模型: {self.agent.backend.model_name}")
        print("输入 /help 查看内置命令")
        print("="*50 + "\n")

        while self.running:
            try:
                user_input = input(">> ").strip()
                if not user_input:
                    continue

                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    try:
                        response = self.agent.chat(user_input)
                        print(f"\n{response}\n")
                    except Exception as e:
                        logger.error(f"生成回复失败: {e}")
                        print(f"[错误] {e}")
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n按 Ctrl+C 退出，或输入 /exit")
                continue

    def _handle_command(self, raw: str):
        parts = shlex.split(raw)
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "/exit" or cmd == "/quit":
            self.running = False
            print("再见！")
            return
        elif cmd == "/help":
            self._show_help()
            return
        elif cmd == "/clear":
            self.agent.clear_history()
            print("对话历史已清空。")
            return
        elif cmd == "/config":
            self._show_config()
            return
        elif cmd == "/reload":
            self._reload_model()
            return
        elif cmd == "/set":
            if len(args) < 2:
                print("用法: /set <key> <value>  例如: /set generation.temperature 0.8")
                return
            self._set_config_value(args[0], args[1])
            return
        elif cmd == "/search":
            if not args:
                print("请提供要查询的问题。")
                return
            query = ' '.join(args)
            self._handle_search(query)
            return
        elif cmd == "/model":
            self._switch_model(args)
            return
        else:
            print(f"未知命令: {cmd}，输入 /help 查看可用命令")

    def _show_help(self):
        print("""可用命令:
  /exit, /quit        退出程序
  /clear              清空对话历史
  /reload             重新加载模型（从配置文件）
  /config             显示当前配置
  /set key value      修改配置项（例如 /set generation.temperature 0.8）
  /search <问题>      联网搜索并回答 (qwen/glm/kimi 用原生搜索)
  /model [类型]       切换或显示当前模型类型
  /help               显示此帮助信息

支持的模型类型:
  API 调用: openai, kimi, deepseek, glm, qwen
  本地模型: llama, ollama, transformers
        """)

    def _reload_model(self):
        try:
            config = load_config(self.config_path)
            self.agent.reload_model(config['model'])
            provider = getattr(self.agent.backend, 'provider', None)
            if provider:
                print(f"模型已重新加载: {self.agent.backend.model_name} ({provider})")
            else:
                print(f"模型已重新加载: {self.agent.backend.model_name}")
        except Exception as e:
            logger.error(f"重新加载模型失败: {e}")
            print(f"[错误] {e}")

    def _show_config(self):
        import yaml
        config = load_config(self.config_path)
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True))

    def _set_config_value(self, key: str, value: str):
        config = load_config(self.config_path)
        keys = key.split('.')
        d = config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        try:
            if value.isdigit():
                d[keys[-1]] = int(value)
            else:
                d[keys[-1]] = float(value)
        except ValueError:
            d[keys[-1]] = value
        save_config(self.config_path, config)
        print(f"已更新配置项 {key} = {d[keys[-1]]}")
        if key.startswith('model.') or key.startswith('generation.'):
            print("注意: 修改了模型或生成参数，请执行 /reload 使更改生效。")

    def _handle_search(self, query: str):
        provider = getattr(self.agent.backend, 'provider', None)
        if hasattr(self.agent.backend, 'supports_native_search') and self.agent.backend.supports_native_search:
            print(f"正在使用 {provider} 原生联网搜索: {query} ...")
        else:
            print(f"正在使用本地搜索: {query} ...")
        try:
            answer = self.agent.search_and_answer(query)
            print(f"\n{answer}\n")
        except Exception as e:
            print(f"搜索或生成回复失败: {e}")

    def _switch_model(self, args):
        """切换或显示当前模型类型"""
        if not args:
            model_type = self.agent.config.get('model', {}).get('type', 'unknown')
            provider = getattr(self.agent.backend, 'provider', None)
            print(f"当前模型类型: {model_type}")
            print(f"当前模型名称: {self.agent.backend.model_name}")
            if provider:
                print(f"当前提供商: {provider}")
            print(f"\n所有支持的类型: {', '.join(ALL_MODEL_TYPES)}")
            print("\nAPI 提供商: openai, kimi, deepseek, glm, qwen")
            print("本地模型: llama, ollama, transformers")
            print("\n使用方法: /model <类型>  例如: /model deepseek")
            print("设置 API Key: /set model.api_key your-key-here")
            return

        new_type = args[0].lower()

        if new_type not in ALL_MODEL_TYPES:
            print(f"无效的模型类型: {new_type}")
            print(f"支持的类型: {', '.join(ALL_MODEL_TYPES)}")
            return

        try:
            config = load_config(self.config_path)
            old_type = config['model'].get('type', 'unknown')
            config['model']['type'] = new_type
            save_config(self.config_path, config)

            print(f"模型类型已从 {old_type} 切换到 {new_type}")
            print("正在重新加载模型...")

            self.agent.reload_model(config['model'])
            provider = getattr(self.agent.backend, 'provider', None)
            if provider:
                print(f"模型已成功加载: {self.agent.backend.model_name} ({provider})")
            else:
                print(f"模型已成功加载: {self.agent.backend.model_name}")

        except Exception as e:
            logger.error(f"切换模型失败: {e}")
            print(f"[错误] 切换模型失败: {e}")
            if new_type in API_PROVIDERS:
                print(f"请确保已设置 {new_type} 的 api_key:")
                print(f"  /set model.api_key your-actual-key")
            print("或检查 userconfig.yaml 中的配置")
