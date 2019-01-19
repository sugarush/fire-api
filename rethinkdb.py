import json

import rethinkdb as r

from .. util import serialize
from .. model import Model, Field, Error
from .. jsonapi import jsonapi, JSONAPIMixin, Empty


r.set_loop_type('asyncio')


class RethinkDB(object):

    connections = { }

    @classmethod
    async def connect(cls, **kargs):
        key = serialize(kargs)

        connection = cls.connections.get(key)
        if connection and connection.is_open():
            return connection

        cls.connections[key] = await r.connect(**kargs)
        return cls.connections[key]

    @classmethod
    async def close(cls):
        for key in cls.connections:
            connection = cls.connections[key]
            if connection.is_open():
                await connection.close()


class RethinkDBModel(Model, JSONAPIMixin):

    db_options = { }
    table_options = { }

    connection = None

    r = None
    _db = None

    _ensure = True

    @classmethod
    def default_primary(self):
        field = Field()
        field.name = 'id'
        field.primary = True
        return field

    @classmethod
    def check_primary(cls, field):
        if not field.type in (bool, int, float, str):
            raise AttributeError('The primary key for a field must be of type: (bool, int, float, str).')

    @classmethod
    async def connect(cls):
        if not cls.connection or not cls.connection.is_open():
            cls.connection = await RethinkDB.connect(**cls.db_options)

        if cls._ensure:
            await cls._ensure_database()
            await cls._ensure_table()
            await cls._ensure_indexes()
            cls._ensure = False

    @classmethod
    async def close(cls):
        if cls.connection and cls.connection.is_open():
            await cls.connection.close()

    @classmethod
    async def _ensure_database(cls):
        databases = await r.db_list().run(cls.connection)
        db = cls.db_options.get('db', 'test')
        if not db in databases:
            await r.db_create(db).run(cls.connection)
        cls._db = r.db(db)

    @classmethod
    async def _ensure_table(cls):
        tables = await cls._db.table_list().run(cls.connection)
        cls.table_options['primary_key'] = cls._primary
        if not cls._table in tables:
            await cls._db.table_create(cls._table, **cls.table_options).run(cls.connection)
        cls.r = cls._db.table(cls._table)

    @classmethod
    async def _ensure_indexes(cls):
        pass

    @classmethod
    async def create(cls, request):
        await cls.connect()

        data = request.json.get('data')

        models = [ ]
        errors = [ ]

        if not data:

            error = Error(
                title = 'Model Create Error',
                detail = 'No data supplied.'
            )

            return jsonapi(status=401, errors=[ error ])

        elif isinstance(data, list):

            for json in data:

                try:
                    model = cls.from_jsonapi(json)
                except Error as error:
                    error.meta = { 'data': json }
                    errors.append(error)
                    continue

                if model.id and cls.exists(model.id):
                    error = Error(
                        title = 'Model Create Error',
                        detail = '{model} {id} already exists.'.format(
                            model = cls.__name__,
                            id = model.id
                        ),
                        meta = {
                            'data': json
                        }
                    )
                    errors.append(error)
                    continue

                error = await model.save()

                if error:
                    error.meta = { 'data': json }
                    errors.append(error)
                    continue

                models.append(model)

            if errors:

                if not models:
                    models.append(Empty)

                return jsonapi(status=401, data=models, errors=errors)

            if not models:
                models.append(Empty)

            return jsonapi(status=201, data=models)

        elif isinstance(data, dict):

            try:
                model = cls.from_jsonapi(data)
            except Error as error:
                error.meta = { 'data': data }
                return jsonapi(status=401, errors=[ error ])

            if model.id and await cls.exists(model.id):
                error = Error(
                    title = 'Model Create Error',
                    detail = '{model} {id} already exists.'.format(
                        model = cls.__name__,
                        id = model.id
                    ),
                    meta = {
                        'data': data
                    }
                )
                return jsonapi(status=409, data=Empty, errors=[ error ])

            error = await model.save()

            if error:
                error.meta = { 'data': data }
                return jsonapi(status=401, errors=[ error ])

            return jsonapi(status=201, data=model)

        else:

            error = Error(
                title = 'Model Create Error',
                detail = 'Invalid data type: must be a list of objects or an object.'
            )

            return jsonapi(status=401, errors=[ error ])

    @classmethod
    async def read(cls, request, id=None):
        await cls.connect()

        if id:
            model = await cls.find_one(id)
            if not model:
                return jsonapi(status=404, data=Empty)
            return jsonapi(status=200, data=model)
        else:
            models = [ ]
            async for model in cls.find(query=request.args):
                models.append(model)
            if not models:
                jsonapi(status=404, data=[ Empty ])
            return jsonapi(status=200, data=models)

    @classmethod
    async def update(cls, request, id):
        await cls.connect()

    @classmethod
    async def delete(cls, request, id):
        await cls.connect()

    @classmethod
    async def read_related(cls, request, id, RelatedModel):
        pass

    @classmethod
    async def set_related(cls, request, id, RelatedModel):
        pass

    @classmethod
    async def update_related(cls, request, id, RelatedModel):
        pass

    @classmethod
    async def delete_related(cls, request, id, RelatedModel):
        pass

    @classmethod
    async def exists(cls, id):
        await cls.connect()

        return await cls.r.get_all(id).contains().run(cls.connection)

    @classmethod
    async def find_one(cls, id):
        await cls.connect()

        data = await cls.r.get(id).run(cls.connection)
        if data:
            return cls(data)

        return None

    @classmethod
    async def find(cls, query={ }):
        await cls.connect()

        q = cls.r

        cursor = await q.run(cls.connection)

        async for data in cursor:
            yield cls(data)

    @classmethod
    async def add_one(cls, data):

            model = None
            id = data.get(cls._primary)

            if id and await cls.exists(id):
                error = Error(
                    title = 'Model Add Error',
                    detail = '{model} {id} already exists.'.format(
                        model = cls.__name__,
                        id = id
                    ),
                    meta = {
                        'id': id,
                        'type': cls._table,
                        'data': data
                    }
                )
                return (None, error)
            else:
                model = cls(data)

            error = await model.save()

            if error:
                return (None, error)

            return (model, None)

    @classmethod
    async def add(cls, args):
        await cls.connect()

        if isinstance(args, (list, tuple)):

            models = [ ]
            errors = [ ]

            for data in args:

                model, error = await cls.add_one(data)

                if error:
                    errors.append(error)
                    continue

                models.append(model)

            return (models, errors)

        elif isinstance(args, dict):

            data = args
            return await cls.add_one(data)

        else:
            raise Error(
                title = 'Model Add Error',
                detail = 'Model.add must be supplied with a list, tuple or dict.'
            )

    async def load(self):
        await self.connect()

        if not self.id:
            return Error(
                title = 'Model Load Error',
                detail = '{model} is missing it\'s primary key, cannot load data.'.format(
                    model = self.__class__.__name__
                )
            )

        data = await self.r.get(self.id).run(self.connection)

        if not data:
            return Error(
                title = 'Model Load Error',
                detail = '{model} could not be found for id {id}'.format(
                    model = self.__class__.__name__,
                    id = self._primary
                )
            )

        self.set(data)

        return None

    async def save(self):
        await self.connect()

        if self.id and await self.exists(self.id):

            data = self.serialize(computed=True)
            operations = self.operations(reset=True)

            result = await self.r.get(self.id)\
                .update(data, return_changes=True)\
                .run(self.connection)

            #print(result)
            # XXX: check for errors in result
            changes = result['changes'][0]['new_val']

            self.update_direct(changes)

        else:

            try:
                self.validate()
            except Error as error:
                return error

            data = self.serialize(computed=True, controllers=True, reset=True)

            result = await self.r\
                .insert(data, return_changes=True)\
                .run(self.connection)

            changes = result['changes'][0]['new_val']

            self.update_direct(changes)

        return None

    async def delete(self):
        await self.connect()

        if not self.id:
            return Error(
                title = 'Model Delete Error',
                detail = '{model} is missing it\'s primary key, cannot delete'\
                    .format(
                        model = self.__class__.__name__
                    )
            )

        if not await self.exists(self.id):
            return Error(
                title = 'Model Delete Error',
                detail = '{model} {id} does not exist, cannot delete.'.format(
                    model = self.__class__.__name__,
                    id = self.id
                )
            )

        await self.r.get(self.id).delete().run(self.connection)

        return None

    @classmethod
    async def drop(cls):
        await cls.connect()
        tables = await cls._db.table_list().run(cls.connection)
        if cls._table in tables:
            await cls._db.table_drop(cls._table).run(cls.connection)
            cls._ensure = True
