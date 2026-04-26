from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str        

class User(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: User
    
    model_config = ConfigDict(from_attributes=True)
    
class PostOut(BaseModel):
    Post: Post
    votes: int
    
    model_config = ConfigDict(from_attributes=True)
    
    
class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
    