import jwt
from sanic import Blueprint
from sanic.response import json

from sugar_odm import Model

from sugar_api import Error


class WebToken(object):

    __content_type__ = 'application/json'

    @classmethod
    def blueprint(cls, *args, **kargs):

        cls.Model = kargs.get('model')

        if not cls.Model:
            raise Exception('Model not provided.')

        if not issubclass(cls.Model, Model):
            raise Exception('Model is not of the proper type.')

        del kargs['model']

        cls.secret = kargs.get('secret')

        if not cls.secret:
            raise Exception('Secret not provided.')

        if 'secret' in kargs:
            del kargs['secret']

        cls.url = kargs.get('url', 'authorization')

        if 'url' in kargs:
            del kargs['url']

        cls.username_field = kargs.get('username_field', 'username')

        if 'username_field' in kargs:
            del kargs['username_field']

        cls.password_field = kargs.get('password_field', 'password')

        if 'password_field' in kargs:
            del kargs['password_field']

        if kargs.get('password_algorithm'):
            cls.password_algorithm = kargs['password_algorithm']
            del kargs['password_algorithm']
        else:
            cls.password_algorithm = lambda password: \
                hashlib.sha512(password.encode('utf-8')).hexdigest()

        cls.token_algorithm = kargs.get('token_algorithm', 'HS256')

        if 'token_algorithm' in kargs:
            del kargs['token_algorithm']

        if not len(args) > 0:
            args = [ cls.url ]

        bp = Blueprint(*args, **kargs)

        @bp.post(cls.url)
        @cls._content_type
        @cls._accept
        async def post(*args, **kargs):
            return await cls._post(*args, **kargs)

        return bp

    @classmethod
    def _content_type(cls, handler):
        async def decorator(request, *args, **kargs):
            content_type = request.headers.get('Content-Type')
            if not content_type or not content_type == cls.__content_type__:
                error = Error(
                    title = 'Invalid Content-Type Header',
                    detail = 'The Content-Type header provided is of an invalid type.',
                    status = 415
                )
                return json({ 'errors': [ error.serialize() ] }, status=415)
            return await handler(request, *args, **kargs)
        return decorator

    @classmethod
    def _accept(cls, handler):
        async def decorator(request, *args, **kargs):
            accept = request.headers.get('Accept')
            if not accept or not accept == cls.__content_type__:
                error = Error(
                    title = 'Invalid Accept Header',
                    detail = 'The Accept header provided is of an invalid type.',
                    status = 415
                )
                return json({ 'errors': [ error.serialize() ] }, status=415)
            return await handler(request, *args, **kargs)
        return decorator

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

            return json({ 'errors': [ error.serialize() ] }, status=403)

        if not isinstance(data, dict):

            error = Error(
                title = 'Create Token Error',
                detail = 'Data is not a JSON object.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        username = data.get(cls.username_field)

        if not username:
            message = 'Field missing: {username}.'.format(
                username = cls.username_field
            )

            error = Error(
                title = 'Create Token Error',
                detail = message,
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        password = data.get('password')

        if not password:
            message = 'Field missing: {password}.'.format(
                password = cls.password_field
            )

            error = Error(
                title = 'Create Token Error',
                detail = message,
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        password = cls.password_algorithm(password)

        model = await cls.Model.find_one({
            cls.username_field: username,
            cls.password_field: password
        })

        if not model:

            error = Error(
                title = 'Create Token Error',
                detail = 'Incorrect username or password.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        token = jwt.encode(model.serialize(computed=True, controllers=True), cls.secret, algorithm=cls.token_algorithm)

        return json({ 'data': { 'token': token } }, 200)
