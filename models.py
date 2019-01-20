from sugar_odm import MongoDBModel, Model, Field
from sugar_api import JSONAPIMixin


class Name(Model):
    first = Field(required=True)
    last = Field(required=True)


class User(MongoDBModel, JSONAPIMixin):
    name = Field(type=Name)
