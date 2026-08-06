"""
AI Agent 核心逻辑：管理对话历史、调用后端模型
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
        """根据配置加载后端模型"""
        model_config = self.config.get('model', {})
        model_type = model_config.get('type', 'llama')
        self.backend = create_backend(model_type)
        self.backend.load(model_config)
        logger.info(f"Agent 已加载模型: {self.backend.model_name}")

    def reload_model(self, new_model_config: Optional[Dict] = None):
        """重新加载模型（切换配置）"""
        if self.backend:
            self.backend.unload()
            self.backend = None
        if new_model_config:
            self.config['model'].update(new_model_config)
        self._load_model()
        self.clear_history()  # 切换模型建议清空历史

    def chat(self, user_input: str) -> str:
        """
        处理用户输入，返回 AI 回复
        """
        # 构建消息列表：系统提示 + 历史 + 当前用户消息
        messages = [{"role": "system", "content": self.system_prompt}]
        # 只保留最近 max_history 轮（每轮含 user + assistant）
        history_trim = self.history[-(self.max_history * 2):]
        messages.extend(history_trim)
        messages.append({"role": "user", "content": user_input})

        # 获取生成参数
        gen_kwargs = self.config.get('generation', {}).copy()
        # 移除可能不需要的参数
        gen_kwargs.pop('model', None)  # 避免冲突

        # 调用后端生成
        response = self.backend.generate(messages, **gen_kwargs)

        # 更新历史
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})

        # 限制历史长度
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

        return response

    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
        logger.info("对话历史已清空")

    def answer_with_context(self, user_question: str, context: str) -> str:
        """
        基于提供的上下文（如搜索结果）生成回答，并更新对话历史。
        context 是字符串，将被插入到用户问题中作为额外信息。
        """
        # 构建完整的消息列表（包含系统提示、历史、当前问题+上下文）
        messages = [{"role": "system", "content": self.system_prompt}]
        # 注意：此处加上历史，但历史中可能已有其他对话
        messages.extend(self.history)
        # 将上下文嵌入到用户消息中
        enhanced_user_msg = f"根据以下搜索结果回答问题：{user_question}\n\n搜索结果：\n{context}"
        messages.append({"role": "user", "content": enhanced_user_msg})

        # 生成参数
        gen_kwargs = self.config.get('generation', {}).copy()
        gen_kwargs.pop('model', None)

        # 调用后端生成
        response = self.backend.generate(messages, **gen_kwargs)

        # 更新历史（只记录原始问题与回答，不保存冗长上下文）
        self.history.append({"role": "user", "content": user_question})
        self.history.append({"role": "assistant", "content": response})

        return response