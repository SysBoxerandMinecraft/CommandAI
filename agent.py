"""
AI Agent 核心逻辑
仅支持普通对话 + 搜索增强
"""
from typing import List, Dict, Optional, Any
from backends import create_backend
from backends.base import ModelBackend
from utils.logger import get_logger

logger = get_logger()

class Agent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend: Optional[ModelBackend] = None
        self.history: List[Dict[str, str]] = []
        self.system_prompt = config.get('context', {}).get('system_prompt', 'You are a helpful assistant.')
        self.max_history = config.get('context', {}).get('max_history_turns', 10)
        self._load_model()

    def _load_model(self):
        model_config = self.config.get('model', {})
        model_type = model_config.get('type', 'openai')
        self.backend = create_backend(model_type)

        # 对于 OpenAI 兼容后端，自动注入 provider
        if model_type in ('kimi', 'deepseek', 'glm', 'qwen'):
            model_config.setdefault('provider', model_type)

        self.backend.load(model_config)
        provider_info = ""
        if hasattr(self.backend, 'provider') and self.backend.provider:
            provider_info = f" (提供商: {self.backend.provider})"
        logger.info(f"Agent 已加载模型: {self.backend.model_name}{provider_info}")

    def reload_model(self, new_model_config: Optional[Dict] = None):
        if self.backend:
            self.backend.unload()
            self.backend = None
        if new_model_config:
            self.config['model'].update(new_model_config)
        self._load_model()
        self.clear_history()

    def _build_messages(self, user_input: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        history_trim = self.history[-(self.max_history * 2):]
        messages.extend(history_trim)
        messages.append({"role": "user", "content": user_input})
        return messages

    def _generate(self, messages: List[Dict[str, str]]) -> str:
        gen_kwargs = self.config.get('generation', {}).copy()
        gen_kwargs.pop('model', None)
        return self.backend.generate(messages, **gen_kwargs)

    def _update_history(self, user_input: str, response: str):
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def chat(self, user_input: str) -> str:
        """普通对话"""
        messages = self._build_messages(user_input)
        response = self._generate(messages)
        self._update_history(user_input, response)
        return response

    def answer_with_context(self, user_question: str, context: str) -> str:
        """基于搜索结果回答（普通模式）"""
        enhanced_msg = f"根据以下搜索结果回答问题：{user_question}\n\n搜索结果：\n{context}"
        messages = self._build_messages(enhanced_msg)
        response = self._generate(messages)
        self._update_history(user_question, response)
        return response

    def search_and_answer(self, user_question: str) -> str:
        """
        联网搜索并回答。
        优先使用模型原生搜索（qwen/glm/kimi），不支持时回退到本地搜索。
        """
        # 检查后端是否支持原生搜索
        if hasattr(self.backend, 'supports_native_search') and self.backend.supports_native_search:
            logger.info(f"使用 {self.backend.provider} 原生联网搜索")
            messages = self._build_messages(user_question)
            gen_kwargs = self.config.get('generation', {}).copy()
            gen_kwargs.pop('model', None)
            response = self.backend.generate_with_search(messages, **gen_kwargs)
            self._update_history(user_question, response)
            return response

        # 回退：本地搜索 + 上下文注入
        logger.info("使用本地 DuckDuckGo 搜索")
        from utils.search import search_web, format_search_results
        results = search_web(user_question, max_results=5)
        if not results:
            return "搜索未找到相关结果。"
        context = format_search_results(results)
        return self.answer_with_context(user_question, context)

    def clear_history(self):
        self.history.clear()
        logger.info("对话历史已清空")