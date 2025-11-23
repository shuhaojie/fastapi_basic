from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DEBUG: bool = False
    PORT: int = 8000
    LOG_LEVEL: str = "info"

    # 数据库连接信息
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWD: str = "root"
    MYSQL_DB: str = "fastapi_basic"
    # 数据库连接池配置
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 40

    # 邮箱信息
    EMAIL_HOST: str = "smtp.qq.com"  # 或者你的邮件服务商
    EMAIL_PORT: int = 465
    EMAIL_USE_SSL: bool = True
    EMAIL_HOST_USER: str = "2386677465@qq.com"
    EMAIL_HOST_PASSWORD: str = "gdmaomlmoxohdjci"  # 邮箱授权码，不是密码
    VERIFICATION_CODE_EXPIRE: int = 300  # 验证码有效期

    # REDIS连接信息
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWD: str = "foobared"
    REDIS_DB: int = 1

    # 超管信息
    SUPER_USER_LIST: list = ["haojie"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    使用缓存获取配置，避免重复读取环境变量
    """
    return Settings()


# 创建全局配置实例
settings = get_settings()
