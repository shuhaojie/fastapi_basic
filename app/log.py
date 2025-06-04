import logging
import os
from logging import handlers

# 服务被访问的日志记录
logger = logging.getLogger('api_log')

# 访问其他服务的日志记录
request_log = logging.getLogger('request_log')

log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_init():
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        '进程ID:%(process)d - '
        '线程ID:%(thread)d- '
        '日志时间:%(asctime)s - '
        '代码路径:%(pathname)s:%(lineno)d - '
        '日志等级:%(levelname)s - '
        '日志信息:%(message)s'
    )
    logger.handlers.clear()
    # 设置api log存储
    api_handler = handlers.TimedRotatingFileHandler(os.path.join(log_dir, "logs/api.log"), encoding='utf-8', when='W6')
    api_handler.setLevel(level=logging.INFO)
    api_handler.setFormatter(formatter)
    logger.addHandler(api_handler)