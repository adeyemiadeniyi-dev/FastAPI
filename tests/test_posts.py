from typing import Any
from app import schemas
import pytest

def test_get_all_posts(authorized_client: Any, test_posts: Any):
    response = authorized_client.get("/posts/")
    assert response.status_code == 200
    assert len(response.json()) == len(test_posts)
    
def test_unauthorized_user_get_all_posts(client: Any, test_posts: Any):
    response = client.get("/posts/")
    assert response.status_code == 401
    
def test_unauthorized_user_get_one_post(client: Any, test_posts: Any):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401
    
def test_get_one_post_not_exist(authorized_client: Any):
    response = authorized_client.get("/posts/9999")
    assert response.status_code == 404
    
def test_get_one_post(authorized_client: Any, test_posts: Any):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    print(response.json())
    post = schemas.PostOut(**response.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title
    
@pytest.mark.parametrize("title, content, published", [
    ("Test Title", "Test Content", True),
    ("Another Title", "Another Content", False),
    ("Pizza Hunt", "Looking for the best pizza in town!", True)
])
def test_create_post(authorized_client: Any, test_user: Any, test_posts: Any, title: str, content: str, published: bool):
    response = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})
    assert response.status_code == 201
    new_post = schemas.Post(**response.json())
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published
    assert new_post.owner_id == test_user['id']

def test_create_post_default_published_true(authorized_client: Any, test_user: Any, test_posts: Any):
    response = authorized_client.post("/posts/", json={"title": "Default Published", "content": "This post should be published by default."})
    assert response.status_code == 201
    new_post = schemas.Post(**response.json())
    assert new_post.title == "Default Published"
    assert new_post.content == "This post should be published by default."
    assert new_post.published == True
    assert new_post.owner_id == test_user['id']
    
def test_unauthorized_user_create_post(client: Any, test_user: Any, test_posts: Any):
    response = client.post("/posts/", json={"title": "Unauthorized Post", "content": "This should not be created."})
    assert response.status_code == 401
    
def test_unauthorized_user_delete_post(client: Any, test_posts: Any):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401
    
def test_delete_post_success(authorized_client: Any, test_posts: Any, test_user: Any):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204
    
def test_delete_post_not_exist(authorized_client: Any, test_posts: Any):
    response = authorized_client.delete("/posts/9999")
    assert response.status_code == 404
    
def test_delete_post_not_owner(authorized_client: Any, test_posts: Any, test_user: Any):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403
    
def test_update_post(authorized_client: Any, test_posts: Any, test_user: Any):
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json={"title": "Updated Title", "content": "Updated Content", "published": False})
    assert response.status_code == 200
    updated_post = schemas.Post(**response.json())
    assert updated_post.title == "Updated Title"
    assert updated_post.content == "Updated Content"
    assert updated_post.published == False
    assert updated_post.owner_id == test_user['id']
    
def test_update_other_user_post(authorized_client: Any, test_posts: Any, test_user: Any, test_user2: Any):
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json={"title": "Hacked Title", "content": "Hacked Content", "published": False})
    assert response.status_code == 403
    
def test_unauthorized_user_update_post(client: Any, test_posts: Any):
    response = client.put(f"/posts/{test_posts[0].id}", json={"title": "Unauthorized Update", "content": "This should not be updated.", "published": False})
    assert response.status_code == 401
    
def test_update_post_not_exist(authorized_client: Any, test_posts: Any, test_user: Any):
    response = authorized_client.put("/posts/9999", json={"title": "Nonexistent Post", "content": "Trying to update a post that doesn't exist.", "published": False})
    assert response.status_code == 404
    