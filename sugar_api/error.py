from sugar_odm import Model, Field


class Links(Model):
    '''
    Sub-model of Error.
    '''

    about = Field()
    '''
    '''


class Source(Model):
    '''
    Sub-model of Error.
    '''

    pointer = Field()
    '''
    '''
    
    parameter = Field()
    '''
    '''


class Error(Model, Exception):

    '''
    An JSONAPI compliant error model which can be raised or serialized.
    It can be constructed from a `dictionary`, `**kargs` or a combination
    of both.
    '''

    id = Field()
    '''
    '''

    links = Field(type=Links)
    '''
    '''

    status = Field(type=int)
    '''
    '''

    code = Field()
    '''
    '''

    title = Field()
    '''
    '''

    detail = Field()
    '''
    '''

    source = Field(type=Source)
    '''
    '''

    meta = Field(type=dict)
    '''
    '''
