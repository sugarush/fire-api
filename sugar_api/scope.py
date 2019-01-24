from sanic.response import json

from sugar_document import Document

from . error import Error


def scope(method, scope):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            token = kargs.get('token')
            try:
                id = args[0]
            except:
                id = None
                response = _check_scope(method, scope, token, id, request)
                if response:
                    return response
            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def _check_actions(action, actions):
    if action in actions:
        return True
    if 'all' in actions:
        return True
    return False

def _check_scope(action, scope, token, id, request):

    if scope:

        token_id = token.get('id')

        copy = scope.copy()

        copy.pop('unauthorized')
        copy.pop('self')
        copy.pop('other')

        group = copy.get(token.type)

        # 1. Check for unauthorized attributes.
        if not token:
            if not _check_action(action, scope.get('unauthorized', { })):
                message = 'Scope unauthorized:{action} not allowed.'.format(
                    action = action
                )
                error = Error(
                    title = 'Scope Error',
                    detail = message,
                    status = 401
                )
                return json({ 'errors': [ error.serialize() ] }, status=401)

        # 2. Check for self attributes.
        elif id == token_id:
            if not _check_action(action, scope.get('self', { })):
                message = 'Scope self:{action} not allowed.'.format(
                    action = action
                )
                error = Error(
                    title = 'Scope Error',
                    detail = message,
                    status = 401
                )
                return json({ 'errors': [ error.serialize() ] }, status=401)

        # 3. Check for group attributes.
        elif group:
            if not _check_action(action, group):
                message = 'Scope {group}:{action} not allowed.'.format(
                    group = group,
                    action = action
                )
                error = Error(
                    title = 'Scope Error',
                    detail = message,
                    status = 401
                )
                return json({ 'errors': [ error.serialize() ] }, status=401)

        # 4. Check for other attributes.
        elif not _check_action(action, scope.get('other', { })):
                message = 'Scope other:{action} not allowed.'.format(
                    action = action
                )
                error = Error(
                    title = 'Scope Error',
                    detail = message,
                    status = 401
                )
                return json({ 'errors': [ error.serialize() ] }, status=401)
