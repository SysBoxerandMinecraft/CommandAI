"""
日志设置和获取
"""
import logging
import sys

_logger = None

def setup_logger(level: str = "INFO", log_file: str = "commandai.log"):
    """设置全局日志配置"""
    global _logger
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)

    logger = logging.getLogger("CommandAI")
    logger.setLevel(log_level)

    # 控制台处理器
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _logger = logger
    return logger

def get_logger():
    """获取全局 logger 实例"""
    global _logger
    if _logger is None:
        # 若未初始化，则使用默认设置
        setup_logger()
    return _logger