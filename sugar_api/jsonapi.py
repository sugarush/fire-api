from sanic import Blueprint
from sanic.response import json

from . error import Error


class JSONAPIMixin(object):

    @classmethod
    async def create(cls, request):

        data = None

        if request.json:

            data = request.json.get('data')

        if not data:

            error = Error(
                title = 'Create Error',
                detail = 'No data supplied.'
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
                    detail = message
                )

                return json({ 'errors': [ error.serialize() ] }, status=409)

            attributes = data.get('attributes')

            if not attributes:

                error = Error(
                    title = 'Create Error',
                    detail = 'Attributes field is missing or empty.'
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            try:

                model = cls.from_jsonapi(data)

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e)
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
                        detail = message
                    )

                    return json({ 'errors': [ error.serialize() ] }, status=409)

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e)
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            try:

                await model.save()

            except Exception as e:

                error = Error(
                    title = 'Create Error',
                    detail = str(e)
                )

                return json({ 'errors': [ error.serialize() ] }, status=401)

            return json({ 'data': model.serialize(controllers=True) }, status=201)

        else:

            error = Error(
                title = 'Create Error',
                detail = 'Invalid data type.',
                links = {
                    'about': 'https://jsonapi.org/format/#crud-creating'
                }
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
    def blueprint(cls, *args, **kargs):

        if not len(args) > 0:
            args = [ cls._table ]

        bp = Blueprint(*args, **kargs)

        route = '/{path}'.format(path=cls._table)

        @bp.post(route)
        async def create(*args, **kargs):
            return await cls.create(*args, **kargs)

        return bp

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
