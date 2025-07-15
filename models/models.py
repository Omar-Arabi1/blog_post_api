from pydantic import BaseModel
from sqlalchemy import Column, String, LargeBinary
from typing import Optional

from databases.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, unique=True)

class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, primary_key=True)
    creator_id = Column(String)
    post_data = Column(String)
    title = Column(String, unique=True)

class CreatePost(BaseModel):
    post_data: str
    title: str

class ShowPosts(BaseModel):
    id: str
    title: str
    creator_username: str

class ShowPostData(BaseModel):
    id: str
    creator_id: str
    post_data: str
    title: str

class ShowUser(BaseModel):
    id: str
    username: str
    hashed_password: str

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(String, primary_key=True)
    body = Column(String)
    creator_id = Column(String)
    mother_post_id = Column(String)

class ShowComment(BaseModel):
    id: str
    body: str
    creator_id: str
    mother_post_id: str