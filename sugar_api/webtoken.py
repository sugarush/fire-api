from uuid import uuid4

import jwt
from sanic import Blueprint

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
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
            if authorization[0].lower() == 'bearer':
                token = authorization[1]
                try:
                    kargs['token'] = jwt.decode(token, __secret__,
                        algorithms=[__algorithm__],
                        options=__options__
                    )
                except jwt.ExpiredSignatureError:
                    error = Error(
                        title = 'Invalid Token Error',
                        detail = 'The token has expired.',
                        status = 403
                    )
                    return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
                except jwt.ImmatureSignatureError:
                    error = Error(
                        title = 'Invalid Token Error',
                        detail = 'The token is not yet valid.',
                        status = 403
                    )
                    return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
                except Exception as e:
                    error = Error(
                        title = 'Invalid Authorization Header',
                        detail = str(e),
                        status = 403
                    )
                    return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
            else:
                error = Error(
                    title = 'Invalid Authorization Header',
                    detail = 'The authorization header is invalid.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
        else:
            kargs['token'] = None
        return await handler(request, *args, **kargs)
    return decorator


class WebToken(object):

    @classmethod
    async def create(cls, attributes):
        raise NotImplementedError('WebToken.payload not implemented.')

    @classmethod
    async def refresh(cls, attributes, token):
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
    def get_secret(cls):
        return __secret__

    @classmethod
    def get_algolithm(cls):
        return __algorithm__

    @classmethod
    def get_options(cls):
        return __options__

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
        @content_type
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
                'token': token.decode('utf-8')
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

        attributes = None
        if request.json and request.json.get('data'):
            attributes = request.json.get('data').get('attributes')
            if not attributes:
                if not token:
                    error = Error(
                        title = 'Refresh Token Error',
                        detail = 'No attributes provided.',
                        status = 403
                    )
                    return jsonapi({
                        'errors': [ error.serialize() ]
                    }, status=403)

        try:
            payload = await cls.refresh(attributes, token)
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
                'token': token.decode('utf-8')
            }
        }, status=200)
