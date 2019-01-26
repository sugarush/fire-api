from uuid import uuid4

import jwt
from sanic import Blueprint
from sanic.response import text

from sugar_odm import Model

from . cors import CORS
from . error import Error
from . header import content_type, accept, jsonapi


__secret__ = str(uuid4())
__algorithm__ = 'HS256'
__options__ = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}


def webtoken(handler):
    async def decorator(request, *args, **kargs):
        authorization = request.headers.get('Authorization')
        if authorization:
            authorization = authorization.split(' ')
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
                    detail = 'The Authorization header is invalid.',
                    status = 403
                )
                return json({ 'errors': [ error.serialize() ] }, status=403)
        else:
            kargs['token'] = None
        return await handler(request, *args, **kargs)
    return decorator


class WebToken(object):

    @classmethod
    async def payload(cls, username, password):
        raise NotImplementedError('WebToken.payload not implemented.')

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
            return await cls._preflight(*args, **kargs)

        @bp.post(url)
        @content_type
        @accept
        async def post(*args, **kargs):
            return await cls._post(*args, **kargs)

        return bp

    @classmethod
    async def _preflight(request, *args, **kargs):
        headers = {
            'Access-Control-Allow-Origin': CORS.get_origins(),
            'Access-Control-Allow-Methods': 'POST, PATCH',
            'Access-Control-Allow-Headers': 'Content-Type, Accept'
        }
        return text('', headers=headers)

    @classmethod
    async def _post(cls, request):
        data = None

        if request.json:
            data = request.json.get('data')

        if not data:
            error = Error(
                title = 'Create Token Error',
                detail = 'No data provided.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        if not isinstance(data, dict):
            error = Error(
                title = 'Create Token Error',
                detail = 'Data is not a JSON object.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        username = data.get('username')

        if not username:
            message = 'Missing username.'.format(
                username = username
            )
            error = Error(
                title = 'Create Token Error',
                detail = message,
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        password = data.get('password')

        if not password:
            message = 'Missing password.'.format(
                password = password
            )
            error = Error(
                title = 'Create Token Error',
                detail = message,
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            payload = await cls.payload(username, password)
        except Exception as e:
            error = Error(
                title = 'Create Token Error',
                detail = str(e),
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        token = jwt.encode(payload, __secret__, algorithm=__algorithm__)
        return jsonapi({ 'data': { 'attributes': { 'token': token } } }, 200)
