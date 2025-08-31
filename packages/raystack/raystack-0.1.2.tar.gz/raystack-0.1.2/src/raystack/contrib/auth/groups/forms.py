from pydantic import BaseModel
from typing import Optional


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Group(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class GroupCreateForm(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None 