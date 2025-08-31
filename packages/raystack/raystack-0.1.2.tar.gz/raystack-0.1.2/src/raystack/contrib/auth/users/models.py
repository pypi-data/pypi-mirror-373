from pydantic import BaseModel
from typing import Optional
from raystack.core.database.models import Model
from raystack.core.database.fields import CharField, IntegerField, AutoField
from raystack.core.database.fields.related import ForeignKeyField

from raystack.contrib.auth.groups.models import Group, GroupModel

# Pydantic model for user creation
class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str
    group_id: int  # ID of the group the user belongs to
    organization: str = "N/A organization"

# Pydantic model for user representation
class User(BaseModel):
    id: int
    name: str
    age: int
    email: str
    group: Optional[Group] = None
    organization: str = "N/A organization"

# Database model
class UserModel(Model):
    table = "users_usermodel"

    id = AutoField()  # Primary key
    name = CharField(max_length=50)
    age = IntegerField()
    email = CharField(max_length=100)
    password_hash = CharField(max_length=255)
    group = ForeignKeyField(to="GroupModel", related_name="users")  # Relationship with group
    organization = CharField(max_length=100)
    is_active = CharField(max_length=1, default="1", null=True)  # 1 for active, 0 for inactive
    is_superuser = CharField(max_length=1, default="0", null=True)  # 1 for superuser, 0 for regular user
