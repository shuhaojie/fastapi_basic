# test/test_protected_route.py
from fastapi.testclient import TestClient
from run import app
from api.utils.logger import logger

client = TestClient(app)


def test_protected_route_without_token():
    response = client.get("/auth/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_route_with_valid_token():
    # 假设 payload 中包含用户名 'testuser'
    response = client.post(url="/auth/login",
                           json={"username": "haojie",
                                 "password": "123456"})
    res_json = response.json()
    logger.info(res_json)
    access_token = response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/auth/protected", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello testuser!"}
