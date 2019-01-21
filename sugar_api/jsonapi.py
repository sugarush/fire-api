from sanic import Blueprint
from sanic.response import json

from . error import Error


class JSONAPIMixin(object):

    __content_type__ = 'application/vnd.api+json'

    def _to_jsonapi(self):
        data = { }

        data['type'] = self._table
        data['id'] = self.id
        data['attributes'] = self.serialize(controllers=True)

        return data

    @classmethod
    def _from_jsonapi(cls, data):
        id = data.get('id')
        attributes = data.get('attributes')

        model = cls(attributes)

        if id:
            model.id = id

        return model

    @classmethod
    def blueprint(cls, *args, **kargs):

        if not len(args) > 0:
            args = [ cls._table ]

        bp = Blueprint(*args, **kargs)

        route = '/{path}'.format(path=cls._table)

        @bp.get(route)
        @cls._accept
        async def read(*args, **kargs):
            return await cls._read(*args, **kargs)

        @bp.post(route)
        @cls._content_type
        @cls._accept
        async def create(*args, **kargs):
            return await cls._create(*args, **kargs)

        @bp.get(route + '/<id>')
        @cls._accept
        async def read(*args, **kargs):
            return await cls._read(*args, **kargs)

        @bp.patch(route + '/<id>')
        @cls._content_type
        @cls._accept
        async def update(*args, **kargs):
            return await cls._update(*args, **kargs)

        @bp.delete(route + '/<id>')
        @cls._accept
        async def delete(*args, **kargs):
            return await cls._delete(*args, **kargs)

        return bp

    @classmethod
    def _content_type(cls, handler):
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
    def _accept(cls, handler):
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
    async def _create(cls, request):

        data = None

        if request.json:

            data = request.json.get('data')

        if not data:

            error = Error(
                title = 'Create Error',
                detail = 'No data supplied.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        if not isinstance(data, dict):

            error = Error(
                title = 'Create Error',
                detail = 'Data is not a JSON object.',
                links = {
                    'about': 'https://jsonapi.org/format/#crud-creating'
                },
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        type = data.get('type')

        if not type:

            error = Error(
                title = 'Create Error',
                detail = 'Type is missing.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        if not type == cls._table:

            error = Error(
                title = 'Create Error',
                detail = 'Provided type does not match resource type.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        attributes = data.get('attributes')

        if not attributes:

            error = Error(
                title = 'Create Error',
                detail = 'No attributes supplied.',
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

        try:

            model = cls._from_jsonapi(data)

        except Exception as e:

            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 403
            )

            return json({ 'errors': [ error.serialize() ] }, status=403)

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
                status = 500
            )

            return json({ 'errors': [ error.serialize() ] }, status=500)

        try:

            await model.save()

        except Exception as e:

            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 500
            )

            return json({ 'errors': [ error.serialize() ] }, status=500)

        try:

            result = model._to_jsonapi()

        except Exception as e:

            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 500
            )

            return json({ 'errors': [ error.serialize() ] }, status=500)

        return json({ 'data': result }, status=201)

    @classmethod
    async def _read(cls, request, id=None):
        if id:

            model = None

            try:

                model = await cls.find_by_id(id)

            except Exception as e:

                error = Error(
                    title = 'Read Error',
                    detail = str(e),
                    status = 500
                )

                return json({ 'errors': [ error.serialize() ] }, status=500)

            if not model:

                error = Error(
                    title = 'Read Error',
                    detail = 'Model not found.',
                    status = 404
                )

                return json({
                    'data': None,
                    'errors': [ error.serialize() ]
                }, status=404)

            try:

                result = model._to_jsonapi()

            except Exception as e:

                error = Error(
                    title = 'Read Error',
                    detail = str(e),
                    status = 500
                )

                return json({ 'errors': [ error.serialize() ] }, status=500)

            return json({ 'data': result }, status=200)

        else:

            models = [ ]

            try:

                async for model in cls.find(request.args):

                    models.append(model)

            except Exception as e:

                error = Error(
                    title = 'Read Error',
                    detail = str(e),
                    status = 404
                )

                return json({ 'errors': [ error.serialize() ] }, status=404)

            if not models:

                error = Error(
                    title = 'Read Error',
                    detail = 'No models found.',
                    status = '404'
                )

                return json({
                    'data': [ ],
                    'errors': [ error.serialize() ]
                }, status=404)

            return json({
                'data': list(map(lambda model: model._to_jsonapi(), models))
            }, status=200)

    @classmethod
    async def _update(cls, request, id):

        data = None

        if request.json:

            data = request.json.get('data')

        if not data:

            error = Error(
                title = 'Update Error',
                detail = 'No data provided.',
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        if not isinstance(data, dict):

            error = Error(
                title = 'Update Error',
                detail = 'Invalid data attribute.',
                links = {
                    'about': 'https://jsonapi.org/format/#crud-creating'
                },
                status = 401
            )

            return json({ 'errors': [ error.serialize() ] }, status=401)

        type = data.get('type')

        if not type == cls._table:

            error = Error(
                title = 'Update Error',
                detail = 'Type in payload does not match collection type.',
                status = 409
            )

            return json({ 'errors': [ error.serialize() ] }, status=409)

        _id = data.get('id')

        if not id == _id:

            error = Error(
                title = 'Update Error',
                detail = 'ID provided does not match ID in the URL.',
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        attributes = data.get('attributes')

        if not attributes:

            error = Error(
                title = 'Update Error',
                detail = 'No attributes provided.',
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        model = None

        try:

            model = await cls.find_by_id(id)

        except Exception as e:

            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        try:

            model.update(attributes)

        except Exception as e:

            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        try:

            await model.save()

        except Exception as e:

            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        return json({ 'data': model._to_jsonapi() }, status=200)

    @classmethod
    async def _delete(cls, request, id):

        try:

            model = await cls.find_by_id(id)

        except Exception as e:

            error = Error(
                title = 'Delete Error',
                detail = str(e),
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        try:

            await model.delete()

        except Exception as e:

            error = Error(
                title = 'Delete Error',
                detail = str(e),
                status = 400
            )

            return json({ 'errors': [ error.serialize() ] }, status=404)

        return json({ }, status=200)
