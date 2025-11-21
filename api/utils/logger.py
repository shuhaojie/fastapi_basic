import os
import logging
from env import BASE_DIR


def setup_logger():
    _logger = logging.getLogger("fastapi")
    _logger.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 避免重复添加 handler
    if not _logger.handlers:
        _logger.addHandler(console_handler)

    # === 文件输出 ===
    log_dir = os.path.join(BASE_DIR, "app/logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, "app.log")

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


logger = setup_logger()
