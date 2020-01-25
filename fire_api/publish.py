def publish(handler):
    async def decorator(request, *args, **kargs):
        response = await handler(request, *args, **kargs)
        print(dir(response))
        return response
    return decorator
