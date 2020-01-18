from uuid import UUID

from bson import ObjectId
from bson.objectid import InvalidId

from . header import jsonapi
from . error import Error


def objectid(key):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            id = kargs.get(key)

            if not id:
                return await handler(request, *args, **kargs)

            valid_uuid = True
            valid_oid = True

            try:
                UUID(id)
            except ValueError:
                valid_uuid = False

            try:
                ObjectId(id)
            except InvalidId:
                valid_oid = False

            if not (valid_uuid or valid_oid):
                error = Error(
                    title = 'Object ID Error',
                    detail = 'Invalid object ID.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            return await handler(request, *args, **kargs)
        return decorator
    return wrapper
