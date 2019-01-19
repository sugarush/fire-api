from sugar_odm import Model, Field


class Links(Model):
    about = Field()


class Source(Model):
    pointer = Field()
    parameter = Field()


class Error(Model, Exception):
    id = Field()
    links = Field(type=Links)
    status = Field(type=int)
    code = Field()
    title = Field()
    detail = Field()
    source = Field(type=Source)
    meta = Field(type=dict)
