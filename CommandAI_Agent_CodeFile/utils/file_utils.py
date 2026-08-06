"""
文件路径工具函数
"""
import os

def check_file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return os.path.isfile(file_path)

def resolve_path(path: str, base_dir: str = None) -> str:
    """将相对路径转为绝对路径，若 base_dir 未指定则使用当前工作目录"""
    if base_dir is None:
        base_dir = os.getcwd()
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    return os.path.normpath(path)