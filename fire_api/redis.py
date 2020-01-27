import json
import aioredis


def serialize(dict):
    return json.dumps(dict, separators=(',', ':'), sort_keys=True)


class Redis(object):

    connections = { }
    loop = None

    default_host = None
    default_minsize = None
    default_maxsize = None

    @classmethod
    def default_connection(cls, **kargs):
        cls.default_host = kargs.get('host', 'redis://localhost')
        cls.default_minsize = kargs.get('minsize', 5)
        cls.default_maxsize = kargs.get('maxsize', 10)

    @classmethod
    async def set_event_loop(cls, loop):
        cls.loop = loop
        await cls.close()
        cls.connections = { }

    @classmethod
    async def connect(cls, **kargs):
        key = serialize(kargs)

        try:
            host = kargs.pop('host')
        except KeyError:
            if not cls.default_host:
                raise Exception('Redis.connect: No host key provided.')
            host = cls.default_host

        if not kargs.get('minsize'):
            if not cls.default_minsize:
                raise Exception('Redis.connect: No minsize key provided.')
            kargs['minsize'] = cls.default_minsize

        if not kargs.get('maxsize'):
            if not cls.default_maxsize:
                raise Exception('Redis.connect: No maxsize key provided.')
            kargs['maxsize'] = cls.default_maxsize

        if not cls.loop:
            raise Exception('Redis.connect: Event loop not yet set.')

        kargs['loop'] = cls.loop

        connection = cls.connections.get(key)
        if connection:
            return connection

        if kargs.get('lowlevel'):
            del kargs['lowlevel']
            cls.connections[key] = await aioredis.create_pool(host, **kargs)
            return cls.connections[key]
        else:
            cls.connections[key] = await aioredis.create_redis_pool(host, **kargs)
            return cls.connections[key]

    @classmethod
    async def close(cls):
        for connection in cls.connections:
            cls.connections[connection].close()
            await cls.connections[connection].wait_closed()
