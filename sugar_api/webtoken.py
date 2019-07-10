from uuid import uuid4

import jwt
from sanic import Blueprint

from sugar_odm import Model

from . error import Error
from . header import content_type, accept, jsonapi
from . preflight import preflight
from . validate import validate


__secret__ = str(uuid4())
__algorithm__ = 'HS256'
__options__ = {
    'verify_exp': True,
    'verify_nbf': True
}


def webtoken(handler):
    async def decorator(request, *args, **kargs):
        authorization = request.headers.get('Authorization')
        if authorization:
            authorization = authorization.split(' ')
            if not len(authorization) == 2:
                error = Error(
                    title = 'Invalid Authorization Header',
                    detail = 'The authorization header is invalid.',
                    status = 403
                )
                return json({ 'errors': [ error.serialize() ] }, status=403)
            if authorization[0].lower() == 'bearer':
                token = authorization[1]
                try:
                    kargs['token'] = jwt.decode(token, __secret__,
                        algorithms=[__algorithm__],
                        options=__options__
                    )
                except Exception as e:
                    error = Error(
                        title = 'Invalid Authorization Header',
                        detail = 'Failed to decode the token.',
                        status = 403
                    )
                    return json({ 'errors': [ error.serialize() ] }, status=403)
            else:
                error = Error(
                    title = 'Invalid Authorization Header',
                    detail = 'The authorization header is invalid.',
                    status = 403
                )
                return json({ 'errors': [ error.serialize() ] }, status=403)
        else:
            kargs['token'] = None
        return await handler(request, *args, **kargs)
    return decorator


class WebToken(object):

    @classmethod
    async def create(cls, attributes):
        raise NotImplementedError('WebToken.payload not implemented.')

    @classmethod
    async def refresh(cls, token):
        raise NotImplementedError('WebToken.refresh not implemented.')

    @classmethod
    def set_secret(cls, secret):
        global __secret__
        __secret__ = secret

    @classmethod
    def set_algorithm(cls, algorithm):
        global __algorithm__
        __algorithm__ = algorithm

    @classmethod
    def set_signature(cls, value):
        global __options__
        if not isinstance(value, bool):
            raise ValueError('Value is not bool.')
        __options__['verify_signature'] = value

    @classmethod
    def set_expiration(cls, value):
        global __options__
        if not isinstance(value, bool):
            raise ValueError('Value is not bool.')
        __options__['verify_exp'] = value

    @classmethod
    def resource(cls, *args, **kargs):

        url = kargs.get('url', 'authentication').strip('/')
        url = '/{url}'.format(url=url)

        if 'url' in kargs:
            del kargs['url']

        if not len(args) > 0:
            args = [ url ]

        bp = Blueprint(*args, **kargs)

        @bp.options(url)
        async def options(*args, **kargs):
            return preflight(methods=[ 'POST', 'PATCH' ])

        @bp.post(url)
        @content_type
        @accept
        @validate
        async def post(*args, **kargs):
            return await cls._post(*args, **kargs)

        @bp.patch(url)
        @accept
        @webtoken
        async def patch(*args, **kargs):
            return await cls._patch(*args, **kargs)

        return bp

    @classmethod
    async def _post(cls, request):

        data = request.json.get('data')
        attributes = data.get('attributes')

        try:
            payload = await cls.create(attributes)
        except Exception as e:
            error = Error(
                title = 'Create Token Error',
                detail = str(e),
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        token = jwt.encode(payload, __secret__, algorithm=__algorithm__)

        return jsonapi({
            'data': {
                'token': token
            }
        }, status=200)

    @classmethod
    async def _patch(cls, request, token=None):

        if not token:
            error = Error(
                title = 'Refresh Token Error',
                detail = 'No token provided.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            payload = await cls.refresh(token)
        except Exception as e:
            error = Error(
                title = 'Refresh Token Error',
                detail = str(e),
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        token = jwt.encode(payload, __secret__, algorithm=__algorithm__)

        return jsonapi({
            'data': {
                'token': token
            }
        }, status=200)
