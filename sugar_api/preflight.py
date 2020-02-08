from sanic.response import text

from . cors import CORS

def preflight(**kargs):
    methods = kargs.get('methods', [ ])
    headers = kargs.get('headers', ['Accept', 'Authorization', 'Content-Type'])
    headers = {
        'Access-Control-Allow-Origin': CORS.get_origins(),
        'Access-Control-Allow-Methods': ', '.join(methods),
        'Access-Control-Allow-Headers': ', '.join(headers)
    }
    return text('', headers=headers)
