import random
import aiosmtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from src.core.utils.logger import logger
from src.config import settings


class EmailVerification:
    """邮箱验证工具类"""

    @staticmethod
    def generate_verification_code():
        """生成6位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    async def send_email(email, verification_code):
        mail_text = f'''
        感谢您注册我们的服务！

        您的验证码是：{verification_code}

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
