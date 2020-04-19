from aioredis_lock import RedisLock, LockTimeoutError

from . redis import Redis


async def acquire(id, uuid, Model, timeout=5, wait=None):
    if not await Model.exists(id):
        return False
    redis = await Redis.connect()
    try:
        async with RedisLock(redis, f'lock:{id}', timeout, wait, uuid) as lock:
            await redis.publish(Model._table, f'acquire:{id}:{uuid}')
            return True
    except LockTimeoutError as e:
        return False

async def release(id, uuid, Model, timeout=5, wait=None):
    if not await Model.exists(id):
        return False
    redis = await Redis.connect()
    holder = await redis.get(f'lock:{id}')
    if holder == uuid:
        await redis.publish(Model._table, f'release:{id}:{uuid}')
        return True
    return False
