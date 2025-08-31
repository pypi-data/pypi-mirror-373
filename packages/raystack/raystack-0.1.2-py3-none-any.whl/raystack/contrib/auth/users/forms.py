from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None


class User(BaseModel):
    name: str
    age: int
    email: str

    class Config:
        orm_mode = True


class UserCreateForm(BaseModel):
    name: str
    age: int
    email: str
    password: str


class UserUpdateForm(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

