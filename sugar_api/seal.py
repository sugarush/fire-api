async def acquire(id, uuid, Model):
    if not await Model.exists(id):
        raise Exception('Document does not exist.')
    await redis.publish(Model._table, f'acquire:{id}:{uuid}')

async def release(id, uuid, Model):
    if not await Model.exists(id):
        raise Exception('Document does not exist.')
    await redis.publish(Model._table, f'release:{id}:{uuid}')

def seal(Model):
    def wrapper(handler):
        async def decorater(*args, **kargs):
            id = kargs.get('id')
            if id:
                await acquire(id, 'api-endpoint', Model)
            response = await handler(*args, **kargs)
            if id:
                await release(id, 'api-endpoint', Model)
            return response
        return decorator
    return wrapper
