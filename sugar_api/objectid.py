from bson import ObjectId
from bson.objectid import InvalidId

from . error import Error


def objectid(handler):
    async def decorator(request, *args, **kargs):
        id = kargs.get('id')

        if not id:
            return await handler(request, *args, **kargs)

        try:
            ObjectId(id)
        except InvalidId:
            error = Error(
                title = 'Object ID Error',
                detail = 'Invalid object id.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        return await handler(request, *args, **kargs)
    return decorator
