"""
命令行交互界面，处理用户输入和内置命令
"""
import sys
import shlex
from typing import Optional
from agent import Agent
from config import load_config, save_config
from utils.logger import get_logger

logger = get_logger()

class CommandLineInterface:
    def __init__(self, agent: Agent, config_path: str):
        self.agent = agent
        self.config_path = config_path
        self.running = True

    def run(self):
        print("\n" + "="*50)
        print("CommandAI - 命令行 AI Agent")
        print(f"当前模型: {self.agent.backend.model_name}")
        print("输入 /help 查看内置命令")
        print("="*50 + "\n")

        while self.running:
            try:
                user_input = input(">> ").strip()
                if not user_input:
                    continue

                # 处理内置命令（以 / 开头）
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # 普通对话
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
        """解析并执行内置命令"""
        parts = shlex.split(raw)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "/exit" or cmd == "/quit":
            self.running = False
            print("再见！")
        elif cmd == "/clear":
            self.agent.clear_history()
            print("对话历史已清空。")
        elif cmd == "/help":
            self._show_help()
        elif cmd == "/reload":
            self._reload_model()
        elif cmd == "/config":
            self._show_config()
        elif cmd == "/set":
            if len(args) < 2:
                print("用法: /set <key> <value>  例如: /set generation.temperature 0.8")
                return
            self._set_config_value(args[0], args[1])
        elif cmd == "/search":
            if not args:
                print("用法: /search <搜索关键词>")
                return
            query = ' '.join(args)
            self._handle_search(query)
        else:
            print(f"未知命令: {cmd}，输入 /help 查看可用命令")

    def _show_help(self):
        print("""可用命令:
  /exit, /quit    退出程序
  /clear          清空对话历史
  /reload         重新加载模型（从配置文件）
  /config         显示当前配置
  /set key value  修改配置项（例如 /set generation.temperature 0.8）
  /search <词>    联网搜索并让 AI 基于搜索结果回答
  /help           显示此帮助信息
        """)

    def _reload_model(self):
        try:
            config = load_config(self.config_path)
            self.agent.reload_model(config['model'])
            print(f"模型已重新加载: {self.agent.backend.model_name}")
        except Exception as e:
            logger.error(f"重新加载模型失败: {e}")
            print(f"[错误] {e}")

    def _show_config(self):
        import yaml
        config = load_config(self.config_path)
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True))

    def _set_config_value(self, key: str, value: str):
        """修改配置并保存，简单处理嵌套key，仅支持字符串值"""
        config = load_config(self.config_path)
        keys = key.split('.')
        d = config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        # 尝试转换类型
        try:
            # 尝试整数
            if value.isdigit():
                d[keys[-1]] = int(value)
            else:
                # 尝试浮点
                d[keys[-1]] = float(value)
        except ValueError:
            d[keys[-1]] = value
        save_config(self.config_path, config)
        print(f"已更新配置项 {key} = {d[keys[-1]]}")
        # 提示需要重新加载模型才生效（若影响模型参数）
        if key.startswith('model.') or key.startswith('generation.'):
            print("注意: 修改了模型或生成参数，请执行 /reload 使更改生效。")

    def _handle_search(self, query: str):
        """执行搜索，并让 AI 基于搜索结果回答"""
        print(f"正在搜索: {query} ...")
        try:
            from utils.search import search_web, format_search_results
            results = search_web(query, max_results=5)
            if not results:
                print("未找到相关结果。")
                return
            context = format_search_results(results)
            # 调用 agent 的新方法 answer_with_context
            answer = self.agent.answer_with_context(query, context)
            print(f"\n{answer}\n")
        except Exception as e:
            print(f"搜索或生成回复失败: {e}")