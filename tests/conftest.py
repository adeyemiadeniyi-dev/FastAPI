from fastapi.testclient import TestClient
from app.database import get_db
from app.main import app
from app.models import Base
from app.oauth import create_access_token
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from typing import List, Dict
import pytest



engine = create_engine(settings.test_database_url, echo=True)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
    

@pytest.fixture
def test_user(client: TestClient) -> Dict[str, str]:
    user_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_user2(client: TestClient) -> Dict[str, str]:
    user_data = {"email": "test2@example.com", "password": "password1234"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user: Dict[str, str]) -> str:
    return create_access_token(data={"user_id": test_user["id"]})

@pytest.fixture
def authorized_client(client: TestClient, token: str) -> TestClient:
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user: Dict[str, str], session, test_user2: Dict[str, str]) -> List[models.Post]:
    posts_data = [
        {"title": "First Post", "content": "Content of the first post", "owner_id": test_user["id"]},
        {"title": "Second Post", "content": "Content of the second post", "owner_id": test_user["id"]},
        {"title": "Third Post", "content": "Content of the third post", "owner_id": test_user["id"]},
        {"title": "Fourth Post", "content": "Content of the fourth post", "owner_id": test_user2["id"]},
    ]

    def create_post_model(post: Dict[str, str]) -> models.Post:
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts