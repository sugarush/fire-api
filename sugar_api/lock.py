import asyncio

from . redis import Redis


async def acquire(id, uuid, Model, expire=5, delay=1, attempts=5):
    '''
    Attempt to acquire a document's lock.

    :param id: The document id to attempt to lock.
    :param uuid: The uuid to place in the lock to verify ownership.
    :param Model: Used to verify that a document with `id` exists.
    :param expire: Specifies how long the lock will be held by the server if not released.
    :param delay: How long to wait between lock acquisition attempts.
    :param attempts: The number of times to attempt to acquire the lock, can be negative.
    :return: A boolean value.
    '''
    if not await Model.exists(id):
        return False
    conn = await Redis.connect(lowlevel=True)
    redis = await Redis.connect()
    _attempts = attempts
    while _attempts:
        holder = await redis.get(f'lock:{id}')
        if holder:
            holder = holder.decode()
        if holder == uuid:
            await redis.publish(Model._table, f'acquired:{Model._table}:{id}:{uuid}:{expire}')
            return True
        if holder != uuid:
            # NX means only set the key if it doesn't already exist
            await conn.execute('SET', f'lock:{id}', uuid, 'NX', 'PX', expire * 1000)
        if not _attempts == attempts:
            # do not delay the first attempt, only subsequent attempts
            await asyncio.sleep(delay)
        _attempts -= 1
    return False

async def release(id, uuid, Model):
    '''
    Attempt to release a document's lock.

    :param id: The document id to attempt to lock.
    :param uuid: The uuid to place in the lock to verify ownership.
    :param Model: Used to verify that a document with `id` exists.
    :return: A boolean value.
    '''
    if not await Model.exists(id):
        return False
    redis = await Redis.connect()
    holder = await redis.get(f'lock:{id}')
    if holder and holder.decode() == uuid:
        await redis.delete(f'lock:{id}')
        await redis.publish(Model._table, f'released:{Model._table}:{id}:{uuid}')
        return True
    return False
