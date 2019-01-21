from sugar_odm import MemoryModel, Model, Field
from sugar_api import JSONAPIMixin


class Name(Model):
    first = Field(required=True)
    last = Field(required=True)


class User(MemoryModel, JSONAPIMixin):
    name = Field(type=Name)
