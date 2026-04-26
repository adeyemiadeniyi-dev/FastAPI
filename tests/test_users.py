import pytest
from jose import jwt
from app import schemas
from fastapi.testclient import TestClient
from app.config import settings



def test_create_user(client: TestClient):
    response = client.post("/users", json={"email": "test@example.com", "password": "password123"})
    new_user = schemas.User(**response.json())
    assert response.status_code == 201
    assert new_user.email == "test@example.com"
    


def test_login_user(client: TestClient, test_user: dict[str, str]):
    response = client.post(
        "auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200 
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: int | None = payload.get("user_id")
    assert id == test_user["id"]
    
    
    
@pytest.mark.parametrize("email, password, expected_status",[
    ("", "password123", 422),
    ("test@example.com", "", 422),
    ("invalidemail", "password123", 403),
    ("test@example.com", "invalidpassword", 403)])
def test_incorrect_login(client: TestClient, test_user: dict[str, str], email: str, password: str, expected_status: int):
    response  = client.post("auth/login", data={"username": email, "password": password})
    assert response.status_code == expected_status

 