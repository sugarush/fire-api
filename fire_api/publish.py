from ujson import loads

def publish(handler):
    async def decorator(request, *args, **kargs):
        response = await handler(request, *args, **kargs)

        json = loads(response.body)

        if json.get('errors'):
            return response

        print(json)

        return response
    return decorator
