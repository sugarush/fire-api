from . error import Error

def _check_scope(scope, token_scope, kargs):
    for (key, value) in scope.items():
        if isinstance(value, str):
            if value.startswith('$'):
                _key = value.lstrip('$')
                token_value = token_scope.get(_key)
                karg_value = kargs.get(_key)
                if not token_value or not karg_value:
                    return False
                if not token_value == karg_value:
                    return False
            elif value.startswith('#'):
                _key = value.lstrip('#')
                token_value = token_scope.get(_key)
                karg_value = kargs.get(_key)
                if not token_value or not karg_value:
                    return False
                if not karg_value in token_value:
                    return False
        else:
            _value = token_scope.get(key)
            if not _value:
                return False
            if not _value == value:
                return False
    return True

def scope(scope):
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

            token_scope = token.get('scope')

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
