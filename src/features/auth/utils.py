import random
import aiosmtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from src.common.utils.logger import logger
from src.core.conf.config import settings
from src.core.server.dependencies import get_redis


class EmailVerification:
    """邮箱验证工具类"""
    CACHE_PREFIX = "verification_code"

    @staticmethod
    def generate_code():
        """生成6位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    async def save_code(email, code):
        """保存验证码到缓存"""
        redis_client = await get_redis()  # 异步
        key = f"{EmailVerification.CACHE_PREFIX}:{email.lower()}"
        await redis_client.setex(key, settings.VERIFICATION_CODE_EXPIRE, code)

    @staticmethod
    async def verify_code(email: str, code: str) -> tuple[bool, str]:
        """验证验证码是否正确"""
        redis_client = await get_redis()
        key = f"{EmailVerification.CACHE_PREFIX}:{email.lower()}"
        cached_code = await redis_client.get(key)

        if cached_code is None:
            return False, "验证码已过期或不存在"

        if cached_code != code:
            return False, "验证码错误"

        # 验证成功后立即删除（防止重复使用）
        await redis_client.delete(key)
        return True, "验证成功"

    @staticmethod
    async def send_email(email, code):
        mail_text = f'''
        感谢您注册我们的服务！

        您的验证码是：{code}

        验证码有效期为5分钟，请尽快完成注册。

        如果这不是您的操作，请忽略此邮件。
        '''
        msg = MIMEText(mail_text, "plain", "utf-8")
        msg["From"] = formataddr(("Test", settings.EMAIL_HOST_USER))
        msg["To"] = email
        msg["Subject"] = "您的注册验证码"

        try:
            response = await aiosmtplib.send(
                msg,
                hostname=settings.EMAIL_HOST,
                port=587,
                start_tls=True,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
            )
            logger.info(f"邮件发送成功: {response}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False


email_verify = EmailVerification()
