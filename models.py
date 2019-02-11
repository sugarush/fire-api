from sugar_odm import MemoryModel, Field
from sugar_api import JSONAPIMixin


class Post(MemoryModel, JSONAPIMixin):

    __acl__ = {
        '$owner': [ 'all' ]
    }

    owner = Field(required=True)


class User(MemoryModel, JSONAPIMixin):

    __acl__ = {
        'self': ['read', 'update'],
        'administrator': ['all'],
        'other': ['read'],
        'unauthorized': ['create', 'read', 'read_all']
    }

    username = Field(required=True)
    password = Field(required=True)

    group = Field(required=True)


class Group(MemoryModel, JSONAPIMixin):

    __acl__ = { 'administrator': ['all'] }

    name = Field(required=True)
