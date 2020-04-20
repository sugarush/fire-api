from sanic.response import json

from . cors import CORS
from . error import Error


__content_type__ = 'application/vnd.api+json'

def jsonapi(*args, **kargs):
    '''
    Returns a Sanic JSON response with the Access-Control-Allow-Origin
    and Content-Type headers set.

    :return: Returns a Sanic JSON response.
    '''
    headers = kargs.get('headers', { })
    headers.update({
        'Access-Control-Allow-Origin': CORS.get_origins(),
        'Content-Type': __content_type__
    })
    kargs['headers'] = headers
    kargs['default'] = lambda date: date.isoformat()
    kargs['separators'] = (',', ':')
    return json(*args, **kargs)

def content_type(handler):
    '''
    Verify that the client's request has a Content-Type header
    of `applicantion/vnd.api+json`.
    '''
    async def decorator(request, *args, **kargs):
        content_type = request.headers.get('Content-Type')
        if not content_type or not content_type == __content_type__:
            error = Error(
                title = 'Invalid Content-Type Header',
                detail = 'The Content-Type header provided is of an invalid type: {content_type}.'.format(content_type=content_type),
                links = {
                    'about': 'http://jsonapi.org/format/#content-negotiation'
                },
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
        return await handler(request, *args, **kargs)
    return decorator

def accept(handler):
    '''
    Verify that the client's request has a Accept header
    of `applicantion/vnd.api+json`.
    '''
    async def decorator(request, *args, **kargs):
        accept = request.headers.get('Accept')
        if not accept or not accept == __content_type__:
            error = Error(
                title = 'Invalid Accept Header',
                detail = 'The Accept header provided is of an invalid type: {accept}.'.format(accept=accept),
                links = {
                    'about': 'http://jsonapi.org/format/#content-negotiation'
                },
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
        return await handler(request, *args, **kargs)
    return decorator
