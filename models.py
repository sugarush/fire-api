from sugar_odm import MongoDBModel, Model, Field
from sugar_api import JSONAPIMixin


class AccountType(MongoDBModel, JSONAPIMixin):

    __acl__ = { 'administrator': ['all'] }

    name = Field(required=True)
    attributes = Field(type=dict)


class User(MongoDBModel, JSONAPIMixin):

    __acl__ = {
        'self': ['read', 'read_all', 'update'],
        'administrator': ['all'],
        'other': ['read', 'read_all'],
        'unauthorized': ['create']
    }

    username = Field(required=True)
    password = Field(required=True)

    type = Field(required=True)
