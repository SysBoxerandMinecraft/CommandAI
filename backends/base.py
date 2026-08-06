"""
模型后端抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ModelBackend(ABC):
    """所有模型后端必须实现的方法"""

    @abstractmethod
    def load(self, config: Dict[str, Any]) -> None:
        """根据配置加载模型（或建立连接）"""
        pass

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        根据对话历史生成回复
        messages: [{"role": "user", "content": "..."}, ...]
        kwargs: 生成参数
        返回生成的文本
        """
        pass

    @abstractmethod
    def unload(self) -> None:
        """释放资源（可选）"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """返回当前加载的模型名称（用于显示）"""
        pass
