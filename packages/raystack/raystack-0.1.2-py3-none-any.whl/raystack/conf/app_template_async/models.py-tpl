from sqlmodel import SQLModel, Field
from typing import Union

class User(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
