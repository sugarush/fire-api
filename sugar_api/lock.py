import asyncio

from . redis import Redis


async def acquire(id, uuid, Model, expire=5, delay=1, attempts=5):
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
            await redis.publish(Model._table, f'acquired:{Model._table}:{id}:{uuid}')
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
    if not await Model.exists(id):
        return False
    redis = await Redis.connect()
    holder = await redis.get(f'lock:{id}')
    if holder and holder.decode() == uuid:
        await redis.delete(f'lock:{id}')
        await redis.publish(Model._table, f'released:{Model._table}:{id}:{uuid}')
        return True
    return False
