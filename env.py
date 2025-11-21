import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class ENV:
    # czt mysql信息
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWD = os.environ.get("MYSQL_PASSWD", "root")
    MYSQL_DB = os.environ.get("MYSQL_DB", "fastapi_basic")

    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

env = ENV()
