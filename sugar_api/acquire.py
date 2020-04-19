def acquire(handler):
    async def decorator(*args, **kargs):
        return await handler(*args, **kargs)
    return decorator
