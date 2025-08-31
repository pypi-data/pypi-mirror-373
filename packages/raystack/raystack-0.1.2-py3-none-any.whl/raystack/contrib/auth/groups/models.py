from pydantic import BaseModel
from raystack.core.database.models import Model
from raystack.core.database.fields import CharField, AutoField

# Pydantic model for creating a group
class GroupCreate(BaseModel):
    name: str  # Group name
    description: str = "N/A"
    
# Pydantic model for representing a group
class Group(BaseModel):
    id: int
    name: str
    description: str = "N/A"

    # class Config:
    #     from_attributes = True

# # Database model for groups
# class GroupModel(Model):
#     id = AutoField()  # Primary key
#     name = CharField(max_length=100, unique=True)  # Group name (unique)

#     def __str__(self):
#         return self.name

class GroupModel(Model):
    table = "groups_groupmodel"

    id = AutoField()  # Primary key
    name = CharField(max_length=100, unique=True)  # Group name (unique)
    description = CharField(max_length=100)

    @property
    def users(self):
        """
        Loads all users associated with this group.
        """
        return UserModel.objects.filter(group=self.id)
