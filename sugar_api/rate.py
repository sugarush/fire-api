from . header import jsonapi
from . error import Error
from . redis import Redis


__intervals__ = {
    'none': 0,
    'secondly': 1,
    'minutely': 60,
    'hourly': 3600,
    'daily': 86400,
    'weekly': 604800,
    'monthly': 2419200,
    'yearly': 31449600
}


def rate(limit, interval, namespace=None):
    if not interval in __intervals__:
        raise Exception(
            f'ratelimit: {interval} not in {list(__intervals__.keys())}'
        )
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            if interval is 'none':
                return await handler(request, *args, **kargs)

            token = kargs.get('token')

            data = (token or { }).get('data', { })
            id = data.get('id')

            redis = await Redis.connect()

            key = f'{id or request.ip}:{namespace or request.path}'

            count = await redis.get(key) or 0

            if int(count) >= limit:
                error = Error(
                    title = 'Rate Limit Error',
                    detail = f'Rate limit exceeded: {limit} {interval}',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if await redis.exists(key):
                await redis.incr(key)
            else:
                await redis.set(key, 1, expire=__intervals__[interval])

            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def socketrate(limit, interval, namespace=None):
    if not interval in __intervals__:
        raise Exception(
            f'ratelimit: {interval} not in {list(__intervals__.keys())}'
        )
    def wrapper(handler):
        async def decorator(state, doc, *args, **kargs):
            if interval is 'none':
                return await handler(request, *args, **kargs)

            data = (state.token or { }).get('data', { })
            id = data.get('id')

            redis = await Redis.connect()

            key = f'{id or state.request.ip}:{namespace or state.request.path}'

            count = await redis.get(key) or 0

            if int(count) >= limit:
                await state.socket.send(json.dumps({
                    'action': 'rate-limit',
                    'interval': interval,
                    'limit': limit
                }))
                return None

            if await redis.exists(key):
                await redis.incr(key)
            else:
                await redis.set(key, 1, expire=__intervals__[interval])

            return await handler(state, doc, *args, **kargs)
        return decorator
    return wrapper
