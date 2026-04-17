import logging
import os
from logging.handlers import RotatingFileHandler

# 配置日志格式
# 使用更简洁的日期时间格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_DIR = 'logs'

# 创建日志目录
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 配置根日志
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 文件日志处理器
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'petri.log'),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 添加处理器到根日志
if not root_logger.handlers:
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

# 创建模块专用日志器
def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)