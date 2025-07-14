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