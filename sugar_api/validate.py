from . error import Error
from . header import jsonapi

def validate(handler):
    '''
    Validate the structure of a JSONAPI request.
    '''
    async def decorator(request, *args, **kargs):

        data = None

        if request.json:
            data = request.json.get('data')

        if not data:
            error = Error(
                title = 'JSON API Error',
                detail = 'No data supplied.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ]}, status=403)

        if not isinstance(data, dict):
            error = Error(
                title = 'JSON API Error',
                detail = 'Data is not a JSON object.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        attributes = data.get('attributes')

        if not attributes:
            error = Error(
                title = 'JSON API Error',
                detail = 'No attributes supplied.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        if not isinstance(attributes, dict):
            error = Error(
                title = 'JSON API Error',
                detail = 'Attributes is not a JSON object.',
                status = 403
            )
            return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

        return await handler(request, *args, **kargs)
    return decorator
