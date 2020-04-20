from json import loads

from . redis import Redis

def publish(action, channel):
    '''
    Publish `action` to `channel` if the final response is a
    `sanic.response.json` object with an JSONAPI datastructure
    containing an ID.

    :param action: The action to publish.
    :param channel: The channel to publish `action` to.
    '''
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            response = await handler(request, *args, **kargs)

            redis = await Redis.connect()

            json = loads(response.body)

            if json.get('errors'):
                return response

            data = json.get('data')
            if data:
                id = data.get('id')
                if id:
                    await redis.publish(channel, f'{action}:{id}')

            return response
        return decorator
    return wrapper
