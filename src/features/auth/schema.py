from pydantic import BaseModel, Field, field_validator
from src.config import settings
from src.core.base.schema import BaseSchema


class EmailSchema(BaseModel):
    email: str


class RegisterInputSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=5, description="密码")
    password_confirm: str = Field(..., description="确认密码")
    code: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        # 通过info.data获取已经验证的字段
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("两次密码不一致")
        return v

    # 移除 password_confirm，create 时不需要
    def get_cleaned_data(self):
        data = self.dict()
        data.pop("password_confirm")
        data.pop("password")
        data.pop("code")
        # 超级用户自动提升
        if data["username"] in settings.SUPER_USER_LIST:
            data["is_superuser"] = True
        return data


class LoginInputSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, description="用户名")
    password: str = Field(..., min_length=5, description="密码")


class LoginData(BaseModel):
    refresh: str = Field(..., description="刷新令牌")
    access: str = Field(..., description="访问令牌")
    is_admin: bool = Field(..., description="是否为管理员")


class LoginOutputSchema(BaseSchema):
    data: LoginData
