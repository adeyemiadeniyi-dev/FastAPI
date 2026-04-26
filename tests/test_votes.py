from typing import Any
from app import models
import pytest

@pytest.fixture()
def test_vote(authorized_client: Any, test_posts: Any, session: Any, test_user: Any) -> Any:
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()
    
def test_vote_on_post(authorized_client: Any, test_posts: Any):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert response.status_code == 201
    
def test_vote_on_post_twice(authorized_client: Any, test_posts: Any, test_vote: Any):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert response.status_code == 409

def test_remove_vote(authorized_client: Any, test_posts: Any, test_vote: Any):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert response.status_code == 201
    
def test_remove_nonexistent_vote(authorized_client: Any, test_posts: Any):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert response.status_code == 404
    
def test_vote_on_nonexistent_post(authorized_client: Any):
    response = authorized_client.post("/vote/", json={"post_id": 9999, "dir": 1})
    assert response.status_code == 404
    
def test_unauthorized_vote(client: Any, test_posts: Any):
    response = client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert response.status_code == 401

