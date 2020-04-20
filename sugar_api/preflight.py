from sanic.response import text

from . cors import CORS

def preflight(**kargs):
    '''
    A function built for the OPTIONS HTTP method. It returns an empty
    HTTP response with the Access-Control-Allow-{Origin,Methods,Headers} headers set.
    '''
    methods = kargs.get('methods', [ ])
    headers = kargs.get('headers', ['Accept', 'Authorization', 'Content-Type'])
    headers = {
        'Access-Control-Allow-Origin': CORS.get_origins(),
        'Access-Control-Allow-Methods': ', '.join(methods),
        'Access-Control-Allow-Headers': ', '.join(headers)
    }
    return text('', headers=headers)
