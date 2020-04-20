__origins__ = ''


class CORS(object):

    '''
    CORS management object.
    '''

    @classmethod
    def set_origins(cls, origins):
        '''
        Set the shared CORS origins.
        '''
        global __origins__
        __origins__ = origins

    @classmethod
    def get_origins(cls):
        '''
        Get the shared CORS origins.
        '''
        return __origins__
