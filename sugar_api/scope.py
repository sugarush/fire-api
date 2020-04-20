from . error import Error
from . header import jsonapi

def scope(scope):
    '''
    Verify that the user's token contains the requested scope.

    .. code-block:: python

        @server.get('/v1/endpoint/<id>')
        @webtoken
        @scope({ 'endpoint': '$id' })
        async def handler(request, id):
            ...
    '''
    def wrapper(handler):
        async def decorator(*args, **kargs):

            token = kargs.get('token')

            if not token:
                error = Error(
                    title = 'Scope Error',
                    detail = 'No token provided.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            data = token.get('data')

            if not data:
                error = Error(
                    title = 'Scope Error',
                    detail = 'No data provided.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            token_scope = data.get('scope')

            if not token_scope:
                error = Error(
                    title = 'Scope Error',
                    detail = 'No scope provided.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if not _check_scope(scope, token_scope, kargs):
                error = Error(
                    title = 'Scope Error',
                    detail = 'Invalid scope.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            return await handler(*args, **kargs)
        return decorator
    return wrapper

def _check_scope(scope, token_scope, kargs):
    for (key, value) in scope.items():
        if isinstance(value, str) and value.startswith('$'):
            _key = value.lstrip('$')
            token_value = token_scope.get(key)
            karg_value = kargs.get(_key)
            if not token_value or not karg_value:
                continue
            if token_value == karg_value:
                return True
        elif isinstance(value, str) and value.startswith('#'):
            _key = value.lstrip('#')
            token_value = token_scope.get(key)
            karg_value = kargs.get(_key)
            if not token_value or not karg_value:
                continue
            if karg_value in token_value:
                return True
        else:
            _value = token_scope.get(key)
            if not _value:
                continue
            if _value == value:
                return True
    return False
