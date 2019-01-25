from sanic.response import json

from . error import Error


__content_type__ = 'application/vnd.api+json'

def jsonapi(*args, **kargs):
    kargs['headers'] = {
        'Content-Type': __content_type__
    }
    return json(*args, **kargs)


def content_type(handler):
    async def decorator(request, *args, **kargs):
        content_type = request.headers.get('Content-Type')
        if not content_type or not content_type == __content_type__:
            error = Error(
                title = 'Invalid Content-Type Header',
                detail = 'The Content-Type header provided is of an invalid type.',
                links = {
                    'about': 'http://jsonapi.org/format/#content-negotiation'
                },
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
        return await handler(request, *args, **kargs)
    return decorator

def accept(handler):
    async def decorator(request, *args, **kargs):
        accept = request.headers.get('Accept')
        if not accept or not accept == __content_type__:
            error = Error(
                title = 'Invalid Accept Header',
                detail = 'The Accept header provided is of an invalid type.',
                links = {
                    'about': 'http://jsonapi.org/format/#content-negotiation'
                },
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
        return await handler(request, *args, **kargs)
    return decorator
