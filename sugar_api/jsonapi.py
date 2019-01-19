from sanic import Blueprint
from sanic.response import json

from . error import Error


class JSONAPIMixin(object):

    __content_type__ = 'application/vnd.api+json'

    @classmethod
    def blueprint(cls, *args, **kargs):

        if not len(args) > 0:
            args = [ cls._table ]

        bp = Blueprint(*args, **kargs)

        route = '/{path}'.format(path=cls._table)

        @bp.post(route)
        @cls.content_type
        @cls.accept
        async def create(*args, **kargs):
            return await cls.create(*args, **kargs)

        return bp

    @classmethod
    def content_type(cls, handler):
        async def decorator(request, *args, **kargs):
            content_type = request.headers.get('Content-Type')
            if not content_type or not content_type == cls.__content_type__:
                error = Error(
                    title = 'Invalid Content-Type Header',
                    detail = 'The Content-Type header provided is of an invalid type.',
                    links = {
                        'about': 'http://jsonapi.org/format/#content-negotiation'
                    },
                    status = 415
                )
                return json({ 'errors': [ error.serialize() ] }, status=415)
            return await handler(request, *args, **kargs)
        return decorator

    @classmethod
    def accept(cls, handler):
        async def decorator(request, *args, **kargs):
            accept = request.headers.get('Accept')
            if not accept or not accept == cls.__content_type__:
                error = Error(
                    title = 'Invalid Accept Header',
                    detail = 'The Accept header provided is of an invalid type.',
                    links = {
                        'about': 'http://jsonapi.org/format/#content-negotiation'
                    },
                    status = 415
                )
                return json({ 'errors': [ error.serialize() ] }, status=415)
            return await handler(request, *args, **kargs)
        return decorator

    @classmethod
    async def create(cls, request):

        data = None

        if request.json:

            data = request.json.get('data')

        if not data:

            error = Error(
                title = 'Create Error',
                detail = 'No data supplied.',
                status = 401
            )

            return json({ 'errors': [ error.serialize() ] }, status=401)

        if isinstance(data, dict):

            type = data.get('type')

            if not type == cls._table:

                message = 'Type {type} does not match collection type.'.format(
                    type = type
                )

                error = Error(
                    title = 'Create Error',
                    detail = message,
                    status = 409
                )

                return json({ 'errors': [ error.serialize() ] }, status=409)

            attributes = data.get('attributes')

            if not attributes:

                error = Error(
                    title = 'Create Error',
                    detail = 'Attributes field is missing or empty.',
                    status = 401
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            try:

                model = cls.from_jsonapi(data)

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e),
                    status = 401
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            try:

                if model.id and await cls.exists(model.id):


                    message = '{model} {id} already exists.'.format(
                        model = cls.__name__,
                        id = model.id
                    )

                    error = Error(
                        title = 'Create Error',
                        detail = message,
                        status = 409
                    )

                    return json({ 'errors': [ error.serialize() ] }, status=409)

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e),
                    status = 401
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            try:

                await model.save()

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e),
                    status = 401
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            return json({ 'data': model.serialize(controllers=True) }, status=201)

        else:

            error = Error(
                title = 'Create Error',
                detail = 'Invalid data type.',
                links = {
                    'about': 'https://jsonapi.org/format/#crud-creating'
                },
                status = 401
            )

            return json({ 'errors': [ error.serialize() ] }, status=401)

    @classmethod
    async def read(cls, request):
        pass

    @classmethod
    async def update(cls, request):
        pass

    @classmethod
    async def delete(cls, request):
        pass

    @classmethod
    def from_jsonapi(cls, data):
        id = data.get('id')
        attributes = data.get('attributes')

        model = cls(attributes)

        if id:
            model.id = id

        return model

    def to_jsonapi(self):
        data = { }

        data['type'] = self._table
        data['id'] = self.id
        data['attributes'] = self.serialize()

        return data
