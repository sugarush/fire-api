__origins__ = ''


class CORS(object):

    @classmethod
    def set_origins(cls, origins):
        global __origins__
        __origins__ = origins

    @classmethod
    def get_origins(cls):
        return __origins__
