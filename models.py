from sugar_odm import MongoDBModel, Model, Field
from sugar_api import JSONAPIMixin


class AccountType(MongoDBModel, JSONAPIMixin):
    name = Field(required=True)
    attributes = Field(type=dict, required=True)


class User(MongoDBModel, JSONAPIMixin):
    username = Field(required=True)
    password = Field(required=True)

    type = Field(required=True)
