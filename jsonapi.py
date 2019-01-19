from typing import NamedTuple

from sanic import Blueprint, response


def jsonapi(status=None, data=None, included=None, errors=None, links=None, meta=None):
    return JSONAPIResponse(status, data or [ ], included or [ ], errors or [ ], links or { }, meta or { })


class JSONAPIResponse(NamedTuple):
    status:   int
    data:     list
    influded: list
    errors:   list
    links:    dict
    meta:     dict


class Empty(object):
    pass


class JSONAPIMixin(object):

    @classmethod
    async def create(cls, request):
        raise NotImplementedError()

    @classmethod
    async def read(cls, request, id=None):
        raise NotImplementedError()

    @classmethod
    async def update(cls, request, id):
        raise NotImplementedError()

    @classmethod
    async def delete(cls, request, id):
        raise NotImplementedError()

    @classmethod
    async def read_related(cls, request, id, RelatedModel):
        raise NotImplementedError()

    @classmethod
    async def set_related(cls, request, id, RelatedModel):
        raise NotImplementedError()

    @classmethod
    async def update_related(cls, request, id, RelatedModel):
        raise NotImplementedError()

    @classmethod
    async def delete_related(cls, request, id, RelatedModel):
        raise NotImplementedError()

    @classmethod
    def from_jsonapi(cls, json):
        id = json.get('id')
        type = json.get('type')
        attributes = json.get('attributes')
        relationships = json.get('relationships')

        if not type:
            pass

        if not type == cls._table:
            pass

        if not attributes:
            pass

        model = cls(attributes)

        if id:
            model.id = id

        return model

    def to_jsonapi(self, request=None):
        data = { }

        data['type'] = self._table
        data['id'] = self.id
        data['meta'] = { 'primary_key': self._primary }

        data['attributes'] = self.serialize(validate=True)

        return data

    @classmethod
    def blueprint(cls, **kargs):
        bp = Blueprint(cls._table, **kargs)

        accepted_type = 'application/vnd.api+json'

        def endpoint(handler):
            async def decorator(request, *args, **kargs):
                response = await handler(request, *args, **kargs)

                if not type(response) == JSONAPIResponse:
                    response = jsonapi(status=500, errors=[ Error(
                        status = 500,
                        title = 'Invalid Handler Response',
                        detail = 'Handler did not respond with a JSONAPIResponse object.'
                    ) ])

                data = { }

                if response.data is Empty:
                    data['data'] = None
                elif isinstance(response.data, Model):
                    data['data'] = response.data.to_jsonapi(request)
                elif isinstance(response.data, list):
                    if len(response.data) == 1 \
                        and response.data[0] is Empty:
                        data['data'] = [ ]
                    elif len(response.data) > 1:
                        data['data'] = list(map(lambda model: \
                            model.to_jsonapi(request), response.data))
                    #else the list is empty, ignore it
                else:
                    # XXX: this is an error
                    pass

                if response.errors:
                    data['errors'] = list(map(lambda error: \
                        error.serialize(), response.errors))

                return json(data, status=response.status, content_type=accepted_type)
            return decorator

        def content_type(handler):
            async def decorator(request, *args, **kargs):
                content_type = request.headers.get('Content-Type')
                if not content_type or not content_type == accepted_type:
                    return jsonapi(status=415, errors=[ Error(
                        status = 415,
                        title = 'Invalid Content-Type Header',
                        links = {
                            'about': 'http://jsonapi.org/format/#content-negotiation'
                        }
                    ) ])
                return await handler(request, *args, **kargs)
            return decorator

        def accept(handler):
            async def decorator(request, *args, **kargs):
                accept = request.headers.get('Accept')
                if not accept or not accept == accepted_type:
                    return jsonapi(status=415, errors=[ Error(
                        status = 415,
                        title = 'Invalid Accept Header',
                        links = {
                            'about': 'http://jsonapi.org/format/#content-negotiation'
                        }
                    ) ])
                return await handler(request, *args, **kargs)
            return decorator

        def validate(handler):
            async def decorator(request, *args, **kargs):
                errors = [ ]
                json = request.json

            return decorator

        # collection routes

        @bp.get(cls._route)
        @endpoint
        @accept
        async def _(request):
            return await cls.read(request)

        @bp.post(cls._route)
        @endpoint
        @content_type
        @accept
        async def _(request):
            return await cls.create(request)

        # item routes

        @bp.get(cls._route + '/<id>')
        @endpoint
        @accept
        async def _(request, id):
            return await cls.read(request, id)

        @bp.patch(cls._route + '/<id>')
        @endpoint
        @content_type
        @accept
        async def _(request, id):
            return await cls.update(request, id)

        @bp.delete(cls._route + '/<id>')
        @endpoint
        @accept
        async def _(request, id):
            return await cls.delete(request, id)

        # relationship routes

        for field in cls._related:

            route = cls._route + '/<id>/reliationships/' + field.name

            @bp.get(route)
            @endpoint
            @accept
            async def _(request, id):
                return await cls.read_related(request, id, field.type)

            @bp.patch(route)
            @endpoint
            @content_type
            @accept
            async def _(request, id):
                return await cls.set_related(request, id, field.type)

            if field.related == 'many':

                @bp.post(route)
                @endpoint
                @content_type
                @accept
                async def _(request, id):
                    return await cls.update_related(request, id, field.type)

                @bp.delete(route)
                @endpoint
                @accept
                async def _(request, id):
                    return await cls.delete_related(request, id, field.type)

        return bp
