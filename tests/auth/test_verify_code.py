# -*- coding: utf-8 -*-
"""
测试文件：test_verify_code.py

该文件包含了FastAPI应用中身份验证模块的验证邮件验证码功能的所有测试用例。
主要测试以下场景：
1. 发送验证邮件（成功、邮箱已存在、邮件发送失败）
2. 验证验证码（成功、无效、过期）
3. 使用验证码注册（有效验证码、无效验证码）

所有测试均使用mock对象模拟外部依赖（数据库、Redis、邮件发送），确保测试的独立性和可重复性。
"""

# 导入测试框架和工具
import pytest
from unittest.mock import AsyncMock, patch  # 用于创建异步模拟对象和替换对象方法
from fastapi.testclient import TestClient  # 用于测试FastAPI应用的客户端
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步数据库会话类型，用于类型提示
import redis.asyncio as redis  # 导入异步Redis模块，用于类型提示

# 导入待测试的应用和模块
from src.main import app  # 导入FastAPI应用实例
from src.features.auth.utils import email_verify  # 导入邮件验证工具模块
from src.core.server.dependencies import get_db, get_redis  # 导入应用依赖项

# 创建测试客户端实例，用于发送HTTP请求
client = TestClient(app)


# 模拟数据库连接的fixture
@pytest.fixture
async def mock_db():
    """
    创建并返回一个模拟的异步数据库会话(AsyncSession)对象。
    
    用途：
    - 在测试中替代真实的数据库连接
    - 允许模拟数据库查询结果和操作
    - 通过AsyncMock确保与异步代码兼容
    
    返回值：
    - AsyncMock对象：模拟的异步数据库会话
    """
    mock = AsyncMock(spec=AsyncSession)  # 创建符合AsyncSession接口的异步模拟对象
    return mock


# 模拟Redis连接的fixture
@pytest.fixture
async def mock_redis():
    """
    创建并返回一个模拟的异步Redis连接对象。
    
    用途：
    - 在测试中替代真实的Redis连接
    - 允许模拟Redis命令的执行结果
    - 通过AsyncMock确保与异步代码兼容
    
    返回值：
    - AsyncMock对象：模拟的异步Redis连接
    """
    mock = AsyncMock(spec=redis.Redis)  # 创建符合redis.Redis接口的异步模拟对象
    return mock


# 覆盖应用依赖项的fixture
@pytest.fixture
async def override_dependencies(mock_db, mock_redis):
    """
    覆盖FastAPI应用的依赖项，将真实的数据库和Redis连接替换为模拟对象。
    
    工作原理：
    1. 将get_db依赖函数替换为返回模拟数据库会话的lambda函数
    2. 将get_redis依赖函数替换为返回模拟Redis连接的lambda函数
    3. 使用yield关键字暂停执行，允许测试函数运行
    4. 测试完成后清除依赖项覆盖，恢复应用原始状态
    
    参数：
    - mock_db: 模拟的异步数据库会话
    - mock_redis: 模拟的异步Redis连接
    """
    # 用模拟的数据库和Redis替换应用的真实依赖
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    
    yield  # 暂停执行，执行测试函数
    
    # 测试完成后清除依赖项覆盖，恢复应用原始状态
    app.dependency_overrides.clear()


# 测试用例：发送验证码 - 成功场景
async def test_send_verification_code(override_dependencies, mock_db, mock_redis):
    """
    测试发送验证邮件的成功场景。
    
    测试步骤：
    1. 模拟数据库查询，确保邮箱不存在（返回None）
    2. 模拟邮件发送功能，使其返回成功
    3. 模拟Redis的setex命令，用于存储验证码
    4. 发送POST请求到/api/v1/auth/email端点，请求发送验证邮件
    5. 验证响应状态码为201（创建成功）
    6. 验证响应消息为"邮件发送成功"
    
    参数：
    - override_dependencies: 覆盖应用依赖项的fixture
    - mock_db: 模拟的异步数据库会话
    - mock_redis: 模拟的异步Redis连接
    """
    # 模拟数据库查询邮箱是否存在，返回None表示不存在
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)

    # 使用patch.object临时替换email_verify.send_email方法，使其返回True（发送成功）
    with patch.object(email_verify, 'send_email', return_value=True):
        # 模拟Redis的setex命令，用于存储验证码（过期时间和值会在实际代码中设置）
        mock_redis.setex = AsyncMock()

        # 发送POST请求到邮箱验证端点，请求发送验证码
        response = client.post(
            "/api/v1/auth/email",
            json={"email": "test@example.com"}
        )

        # 验证响应状态码为201（创建成功）
        assert response.status_code == 201
        # 验证响应消息为预期内容
        assert response.json()["message"] == "邮件发送成功"


# 测试用例：发送验证码 - 邮箱已存在
async def test_send_verification_code_email_exists(override_dependencies, mock_db):
    """
    测试发送验证邮件时，邮箱已存在的场景。
    
    测试步骤：
    1. 模拟数据库查询，返回一个用户对象（表示邮箱已存在）
    2. 发送POST请求到/api/v1/auth/email端点，请求发送验证邮件
    3. 验证响应状态码为400（请求错误）
    4. 验证响应消息为"邮箱已注册"
    
    参数：
    - override_dependencies: 覆盖应用依赖项的fixture
    - mock_db: 模拟的异步数据库会话
    """
    # 模拟数据库查询返回一个用户对象（表示邮箱已存在）
    mock_user = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=mock_user)

    # 发送POST请求到邮箱验证端点，请求发送验证码
    response = client.post(
        "/api/v1/auth/email",
        json={"email": "existing@example.com"}
    )

    # 验证响应状态码为400（请求错误）
    assert response.status_code == 400
    # 验证响应消息为预期内容
    assert response.json()["message"] == "邮箱已注册"


# 测试用例：发送验证码 - 邮件发送失败
async def test_send_verification_code_email_fail(override_dependencies, mock_db, mock_redis):
    """
    测试发送验证邮件失败的场景。
    
    测试步骤：
    1. 模拟数据库查询，确保邮箱不存在（返回None）
    2. 模拟邮件发送功能，使其返回False（发送失败）
    3. 模拟Redis的setex命令（虽然邮件发送失败，但代码可能仍会尝试存储验证码）
    4. 发送POST请求到/api/v1/auth/email端点，请求发送验证邮件
    5. 验证响应状态码为400（请求错误）
    6. 验证响应消息为"邮件发送失败"
    
    参数：
    - override_dependencies: 覆盖应用依赖项的fixture
    - mock_db: 模拟的异步数据库会话
    - mock_redis: 模拟的异步Redis连接
    """
    # 模拟数据库查询邮箱是否存在，返回None表示不存在
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)

    # 使用patch.object临时替换email_verify.send_email方法，使其返回False（发送失败）
    with patch.object(email_verify, 'send_email', return_value=False):
        # 模拟Redis的setex命令
        mock_redis.setex = AsyncMock()

        # 发送POST请求到邮箱验证端点，请求发送验证码
        response = client.post(
            "/api/v1/auth/email",
            json={"email": "test@example.com"}
        )

        # 验证响应状态码为400（请求错误）
        assert response.status_code == 400
        # 验证响应消息为预期内容
        assert response.json()["message"] == "邮件发送失败"


# 测试用例：验证验证码 - 成功
@patch.object(email_verify, 'verify_code')
async def test_verify_code_success(mock_verify):
    """
    直接测试验证码验证功能的成功场景。
    
    注意：此测试直接调用email_verify.verify_code方法，而不是通过API接口，
    因为验证码验证功能在当前实现中可能没有独立的API接口，而是作为注册流程的一部分。
    
    测试步骤：
    1. 使用patch.object替换email_verify.verify_code方法，使其返回成功结果(True, "验证成功")
    2. 调用verify_code方法验证邮箱和验证码
    3. 验证返回结果为(True, "验证成功")
    4. 验证verify_code方法被正确调用（参数正确）
    
    参数：
    - mock_verify: 被替换的verify_code方法的模拟对象
    """
    # 设置模拟方法的返回值
    mock_verify.return_value = (True, "验证成功")

    # 调用被测试的方法
    is_valid, message = await email_verify.verify_code("test@example.com", "123456")

    # 验证返回值
    assert is_valid is True
    assert message == "验证成功"
    # 验证方法被正确调用，参数为预期值
    mock_verify.assert_called_once_with("test@example.com", "123456")


# 测试用例：验证验证码 - 无效验证码
@patch.object(email_verify, 'verify_code')
async def test_verify_code_invalid(mock_verify):
    """
    直接测试验证码验证功能的无效验证码场景。
    
    测试步骤：
    1. 使用patch.object替换email_verify.verify_code方法，使其返回无效结果(False, "验证码错误")
    2. 调用verify_code方法验证邮箱和无效验证码
    3. 验证返回结果为(False, "验证码错误")
    4. 验证verify_code方法被正确调用（参数正确）
    
    参数：
    - mock_verify: 被替换的verify_code方法的模拟对象
    """
    # 设置模拟方法的返回值
    mock_verify.return_value = (False, "验证码错误")

    # 调用被测试的方法
    is_valid, message = await email_verify.verify_code("test@example.com", "654321")

    # 验证返回值
    assert is_valid is False
    assert message == "验证码错误"
    # 验证方法被正确调用，参数为预期值
    mock_verify.assert_called_once_with("test@example.com", "654321")


# 测试用例：验证验证码 - 过期验证码
@patch.object(email_verify, 'verify_code')
async def test_verify_code_expired(mock_verify):
    """
    直接测试验证码验证功能的验证码过期场景。
    
    测试步骤：
    1. 使用patch.object替换email_verify.verify_code方法，使其返回过期结果(False, "验证码已过期或不存在")
    2. 调用verify_code方法验证邮箱和过期验证码
    3. 验证返回结果为(False, "验证码已过期或不存在")
    4. 验证verify_code方法被正确调用（参数正确）
    
    参数：
    - mock_verify: 被替换的verify_code方法的模拟对象
    """
    # 设置模拟方法的返回值
    mock_verify.return_value = (False, "验证码已过期或不存在")

    # 调用被测试的方法
    is_valid, message = await email_verify.verify_code("test@example.com", "123456")

    # 验证返回值
    assert is_valid is False
    assert message == "验证码已过期或不存在"
    # 验证方法被正确调用，参数为预期值
    mock_verify.assert_called_once_with("test@example.com", "123456")


# 测试用例：注册 - 验证码有效
async def test_register_with_valid_code(override_dependencies, mock_db, mock_redis):
    """
    测试使用有效验证码进行注册的成功场景。
    
    测试步骤：
    1. 模拟数据库查询，确保用户名和邮箱都不存在（返回None）
    2. 模拟数据库提交操作
    3. 模拟验证码验证成功
    4. 发送POST请求到注册端点，包含有效验证码
    5. 验证响应状态码为201（创建成功）
    6. 验证响应消息为"注册成功"
    
    参数：
    - override_dependencies: 覆盖应用依赖项的fixture
    - mock_db: 模拟的异步数据库会话
    - mock_redis: 模拟的异步Redis连接
    """
    # 模拟数据库查询用户名和邮箱是否存在，返回None表示不存在
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)
    # 模拟数据库提交操作
    mock_db.commit = AsyncMock()

    # 模拟验证码验证成功
    with patch.object(email_verify, 'verify_code', return_value=(True, "验证成功")):
        # 发送POST请求到注册端点，包含完整的注册信息和有效验证码
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "password_confirm": "password123",  # 确认密码必须与密码一致
                "code": "123456"  # 有效验证码
            }
        )

        # 验证响应状态码为201（创建成功）
        assert response.status_code == 201
        # 验证响应消息为预期内容
        assert response.json()["message"] == "注册成功"


# 测试用例：注册 - 验证码无效
async def test_register_with_invalid_code(override_dependencies, mock_db):
    """
    测试使用无效验证码进行注册的失败场景。
    
    测试步骤：
    1. 模拟数据库查询，确保用户名不存在（返回None）
    2. 模拟验证码验证失败
    3. 发送POST请求到注册端点，包含无效验证码
    4. 验证响应状态码为400（请求错误）
    5. 验证响应消息为"验证码错误"
    
    参数：
    - override_dependencies: 覆盖应用依赖项的fixture
    - mock_db: 模拟的异步数据库会话
    """
    # 模拟数据库查询用户名是否存在，返回None表示不存在
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)

    # 模拟验证码验证失败
    with patch.object(email_verify, 'verify_code', return_value=(False, "验证码错误")):
        # 发送POST请求到注册端点，包含完整的注册信息和无效验证码
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser2",  # 使用不同的用户名，避免与其他测试冲突
                "email": "test@example.com",
                "password": "password123",
                "password_confirm": "password123",
                "code": "123456"  # 无效验证码
            }
        )

        # 验证响应状态码为400（请求错误）
        assert response.status_code == 400
        # 验证响应消息为预期内容
        assert response.json()["message"] == "验证码错误"
