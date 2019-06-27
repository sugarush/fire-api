from . header import jsonapi
from . error import Error
from . redis import Redis


__intervals__ = {
    'none': 0,
    'secondly': 1,
    'minutely': 60,
    'hourly': 3600,
    'daily': 86400,
    'weekly': 604800
}


def rate(limit, interval, namespace=None):
    if not interval in __intervals__:
        raise Exception(
            f'ratelimit: {interval} not in {", ".join(__intervals__.keys())}'
        )
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            if interval is 'none':
                return await handler(request, *args, **kargs)

            token = kargs.get('token', { })
            data = token.get('data', { })
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
