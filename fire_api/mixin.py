import json, asyncio
from copy import copy
from datetime import datetime
from uuid import uuid4

import jwt
import aioredis

from sanic import Blueprint
from sanic.log import logger
from websockets.exceptions import ConnectionClosedError

from fire_document import Document
from fire_router import Router

from . acl import acl
from . error import Error
from . header import content_type, accept, jsonapi
from . objectid import objectid
from . preflight import preflight
from . publish import publish
from . rate import rate
from . redis import Redis
from . restrictions import set, _apply_restrictions
from . validate import validate
from . webtoken import WebToken, webtoken


class TimestampMixin(object):

    def timestamp(self, value):
        if isinstance(value, str):
            if value.endswith('Z'):
                value = value[:-1] # Remove the Z from the javascript timestamp
            return datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            return value
        else:
            return value


class JSONAPIMixin(object):

    __rate__ = (0, 'none')
    __acl__ = None
    __get__ = None
    __set__ = None

    def to_jsonapi(self):
        data = { }

        data['type'] = self._table
        data['id'] = self.id
        data['attributes'] = self.serialize()

        del data['attributes']['_id']

        return data

    def render(self, token):
        data = self.to_jsonapi()

        if hasattr(self, 'on_render'):
            self.on_render(data, token)

        if self.__get__:

            if not token:

                token = {
                    'data': {
                        'id': 'unauthorized',
                        'groups': ['unauthorized']
                    }
                }

            token_data = token.get('data', { })
            token_id = token_data.get('id')
            token_groups = token_data.get('groups', [ ])

            attributes = data.get('attributes')

            groups = copy(token_groups)

            if self.id == token_id:
                groups.append('self')

            model_data = self.serialize()

            _apply_restrictions(attributes, self.__get__, groups, [ ], [ ], model_data, token_id)

        return data

    @classmethod
    def from_jsonapi(cls, data):
        id = data.get('id')
        attributes = data.get('attributes')

        model = cls(attributes)

        if id:
            model.id = id

        return model

    @classmethod
    def resource(cls, *args, realtime=False, **kargs):

        if not len(args) > 0:
            args = [ cls._table ]

        bp = Blueprint(*args, **kargs)

        url = '/{path}'.format(path=cls._table)

        if realtime:
            @bp.websocket(f'{url}/realtime')
            async def realtime(request, socket):
                return await cls._realtime(request, socket)

        @bp.options(url)
        async def options(*args, **kargs):
            return preflight(methods=[ 'GET', 'POST' ])

        @bp.options(url + '/<id>')
        async def options(*args, **kargs):
            return preflight(methods=[ 'GET', 'PATCH', 'DELETE' ])

        @bp.get(url)
        @accept
        @webtoken
        @rate(*(cls.__rate__ or [ 0, 'none' ]), namespace=cls._table)
        @acl('read_all', cls.__acl__, cls)
        async def read(*args, **kargs):
            return await cls._read(*args, **kargs)

        @bp.post(url)
        @content_type
        @accept
        @validate
        @cls._check_create
        @webtoken
        @rate(*(cls.__rate__ or [ 0, 'none' ]), namespace=cls._table)
        @acl('create', cls.__acl__, cls)
        @set(cls.__set__, cls)
        @publish('create', cls._table)
        async def create(*args, **kargs):
            return await cls._create(*args, **kargs)

        @bp.get(url + '/<id>')
        @objectid('id')
        @accept
        @webtoken
        @rate(*(cls.__rate__ or [ 0, 'none' ]), namespace=cls._table)
        @acl('read', cls.__acl__, cls)
        async def read(*args, **kargs):
            return await cls._read(*args, **kargs)

        @bp.patch(url + '/<id>')
        @objectid('id')
        @content_type
        @accept
        @validate
        @cls._check_update
        @webtoken
        @rate(*(cls.__rate__ or [ 0, 'none' ]), namespace=cls._table)
        @acl('update', cls.__acl__, cls)
        @set(cls.__set__, cls)
        @publish('update', cls._table)
        async def update(*args, **kargs):
            return await cls._update(*args, **kargs)

        @bp.delete(url + '/<id>')
        @objectid('id')
        @accept
        @webtoken
        @rate(*(cls.__rate__ or [ 0, 'none' ]), namespace=cls._table)
        @acl('delete', cls.__acl__, cls)
        @publish('delete', cls._table)
        async def delete(*args, **kargs):
            return await cls._delete(*args, **kargs)

        return bp

    @classmethod
    def _check_create(cls, handler):
        async def decorator(request, *args, **kargs):

            # XXX: The request data has already been validated
            # XXX: with the @validate decorator.

            data = request.json.get('data')

            type = data.get('type')

            if not type:
                error = Error(
                    title = 'Create Error',
                    detail = 'Type is missing.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if not type == cls._table:
                error = Error(
                    title = 'Create Error',
                    detail = 'Provided type does not match resource type.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            return await handler(request, *args, **kargs)

        return decorator

    @classmethod
    def _check_update(cls, handler):
        async def decorator(request, *args, **kargs):

            # XXX: The request data has already been validated
            # XXX: with the @validate decorator.

            data = request.json.get('data')

            type = data.get('type')

            if not type:
                error = Error(
                    title = 'Update Error',
                    detail = 'Type is missing.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if not type == cls._table:
                error = Error(
                    title = 'Update Error',
                    detail = 'Type in payload does not match collection type.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            id = kargs.get('id')
            _id = data.get('id')

            if not _id:
                error = Error(
                    title = 'Update Error',
                    detail = 'ID is missing.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if not id == _id:
                error = Error(
                    title = 'Update Error',
                    detail = 'ID provided does not match ID in the URL.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            return await handler(request, *args, **kargs)

        return decorator

    @classmethod
    async def _create(cls, request, token=None, errors=[ ]):

        # XXX: The request data has already been validated
        # XXX: with the @validate decorator.

        # XXX: The request has already been verified
        # XXX: in the decorator cls._check_create.

        data = request.json.get('data')

        try:
            model = cls.from_jsonapi(data)
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

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
                return jsonapi({ 'errors': [ error.serialize() ] }, status=409)
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        if hasattr(model, 'on_create'):
            try:
                await model.on_create(token)
            except Exception as e:
                logger.info(str(e), exc_info=True)
                error = Error(
                    title = 'Create Error',
                    detail = str(e),
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            await model.save()
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Create Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        response = {
            'data': model.render(token)
        }

        if errors:
            response['errors'] = list(map(lambda error: \
                error.serialize(), errors))

        return jsonapi(response, status=201)

    @classmethod
    async def _read(cls, request, id=None, token=None, errors=[ ]):

        fields = None
        fields_json = request.args.get('fields', None)

        try:
            if fields_json:
                fields = json.loads(fields_json)
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Read Error',
                detail = str(e),
                status = 403
            )
            return jsonapi({
                'errors': [ error.serialize() ]
            }, status=403)

        if id:

            try:
                model = await cls.find_by_id(id, projection=fields)
            except Exception as e:
                logger.info(str(e), exc_info=True)
                error = Error(
                    title = 'Read Error',
                    detail = str(e),
                    status = 500
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

            if not model:
                error = Error(
                    title = 'Read Error',
                    detail = 'No data found.',
                    status = 404
                )
                return jsonapi({
                    'data': None,
                    'errors': [ error.serialize() ]
                }, status=404)

            if hasattr(model, 'on_read'):
                try:
                    await model.on_read(token)
                except Exception as e:
                    logger.info(str(e), exc_info=True)
                    error = Error(
                        title = 'Read Error',
                        detail = str(e),
                        status = 403
                    )
                    return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            response = {
                'data': model.render(token)
            }

            if errors:
                response['errors'] = list(map(lambda error: \
                    error.serialize(), errors))

            return jsonapi(response, status=200)

        else:

            try:

                models = [ ]

                query_json = request.args.get('query', '{ }')

                try:
                    query = json.loads(query_json)
                except Exception as e:
                    logger.info(str(e), exc_info=True)
                    error = Error(
                        title = 'Read Error',
                        detail = str(e),
                        status = 403
                    )
                    return jsonapi({
                        'errors': [ error.serialize() ]
                    }, status=403)

                sort = request.args.get('sort')

                if sort:

                    try:
                        sort = filter(lambda item: item != '', sort.split(','))
                    except Exception as e:
                        logger.info(str(e), exc_info=True)
                        error = Error(
                            title = 'Read Error',
                            detail = str(e),
                            status = 403
                        )
                        return jsonapi({
                            'errors': [ error.serialize() ]
                        }, status=403)

                    def prepare(item):
                        result = [ ]

                        if item.startswith('-'):
                            result.append(-1)
                        else:
                            result.append(1)

                        item = item.strip('-')
                        result.insert(0, item)

                        return result

                    sort = list(map(prepare, sort))

                offset = int(request.args.get('page[offset]', 0))
                limit = int(request.args.get('page[limit]', 100))

                if limit > 1000:
                    limit = 1000
                count = 0

                async for model in cls.find(query):
                    count += 1

                async for model in cls.find(query,
                    sort=sort,
                    skip=offset,
                    limit=limit,
                    projection=fields
                ):
                    if hasattr(model, 'on_read'):
                        try:
                            await model.on_read(token)
                        except Exception as e:
                            logger.info(str(e), exc_info=True)
                            error = Error(
                                title = 'Read Error',
                                detail = str(e),
                                status = 403
                            )
                            errors.append(error)
                            continue
                    models.append(model)

            except Exception as e:
                logger.info(str(e), exc_info=True)
                error = Error(
                    title = 'Read Error',
                    detail = str(e),
                    status = 500
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

            if not models and not errors:
                error = Error(
                    title = 'Read Error',
                    detail = 'No data found.',
                    status = 404
                )
                return jsonapi({
                    'data': [ ],
                    'errors': [ error.serialize() ]
                }, status=404)

            response = {
                'data': list(map(lambda model: model.render(token), models)),
                'meta': {
                    'offset': offset,
                    'limit': limit,
                    'total': count
                }
            }

            if errors:
                response['errors'] = list(map(lambda error: \
                    error.serialize(), errors))

            return jsonapi(response, status=200)

    @classmethod
    async def _update(cls, request, id=None, token=None, errors=[ ]):

        # XXX: The request data has already been validated
        # XXX: with the @validate decorator.

        # XXX: The request has already been verified
        # XXX: with the decorator @cls._check_update.

        data = request.json.get('data')

        attributes = data.get('attributes')

        try:
            model = await cls.find_by_id(id)
        except Exception as e:
            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        if not model:
            error = Error(
                title = 'Update Error',
                detail = 'Model not found.',
                status = 404
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=404)

        if hasattr(model, 'on_update'):
            try:
                await model.on_update(token, attributes)
            except Exception as e:
                logger.info(str(e), exc_info=True)
                error = Error(
                    title = 'Update Error',
                    detail = str(e),
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            model.update(attributes)
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        if not model.id == id:
            error = Error(
                title = 'Update Error',
                detail = 'The Model\'s ID does not match the ID in the URL.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            await model.save()
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Update Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        response = {
            'data': model.render(token)
        }

        if errors:
            response['errors'] = list(map(lambda error: \
                error.serialize(), errors))

        return jsonapi(response, status=200)

    @classmethod
    async def _delete(cls, request, id, token=None, errors=[ ]):

        try:
            model = await cls.find_by_id(id)
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Delete Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        if not model:
            error = Error(
                title = 'Delete Error',
                detail = 'Model not found.',
                status = 404
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=404)

        if hasattr(model, 'on_delete'):
            try:
                await model.on_delete(token)
            except Exception as e:
                logger.info(str(e), exc_info=True)
                error = Error(
                    title = 'Delete Error',
                    detail = str(e),
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        try:
            await model.delete()
        except Exception as e:
            logger.info(str(e), exc_info=True)
            error = Error(
                title = 'Delete Error',
                detail = str(e),
                status = 500
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=500)

        response = {
            'data': {
                'id': id
            }
        }

        if errors:
            response['errors'] = list(map(lambda error: \
                error.serialize(), errors))

        return jsonapi(response, status=200)

    @classmethod
    async def _realtime(cls, request, socket):

        state = type('', (), {})()

        #state.conn = await Redis.connect(lowlevel=True)
        #state.channel = aioredis.Channel(cls._table, is_pattern=False)
        #await state.conn.execute_pubsub('SUBSCRIBE', state.channel)

        state.socket = socket
        state.uuid = str(uuid4())
        state.index = { }

        router = Router(methods=[ 'subscribe', 'unsubscribe' ])

        @router.subscribe(f'/v1/{cls._table}/<id>')
        async def subscribe(state, doc, id):
            if await cls.exists(id):
                state.index[id] = True

        @router.unsubscribe(f'/v1/{cls._table}/<id>')
        async def unsubscribe(state, doc, id):
            if id in state.index:
                del state.index[id]

        async def socket_reader(state):
            while True:
                try:
                    data = json.loads(await socket.recv())
                except json.JSONDecodeError as e:
                    logger.info(str(e), exc_info=True)
                    continue
                except ConnectionClosedError as e:
                    logger.info(str(e))
                    break

                doc = Document(data)

                router.emit(doc.action, doc.path, state, doc)

        async def socket_writer(state):
            conn = await aioredis.create_connection(Redis.default_host)
            channel = aioredis.Channel(cls._table, is_pattern=False)
            await conn.execute_pubsub('SUBSCRIBE', channel)

            async for message in channel.iter():
                try:
                    action, id = message.decode().split(':')
                except ValueError as e:
                    continue

                if id in state.index:
                    await state.socket.send(json.dumps({
                        'action': action,
                        'id': id
                    }))

        await asyncio.gather(socket_reader(state), socket_writer(state))
