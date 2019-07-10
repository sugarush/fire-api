from copy import copy

from . header import jsonapi
from . error import Error

def set(restrictions):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            if not restrictions:
                return await handler(request, *args, **kargs)

            id = kargs.get('id')

            token = kargs.get('token')

            if not token:

                token = {
                    'data': {
                        'id': 'unauthorized',
                        'groups': ['unauthorized']
                    }
                }

            token_data = token.get('data')

            if not token_data:
                error = Error(
                    title = 'Restriction Error',
                    detail = 'Token does not contain a data attribute.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            token_id = token_data.get('id')

            if not token_id:
                error = Error(
                    title = 'Restriction Error',
                    detail = 'Token data does not contain an ID attribute.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            token_groups = token_data.get('groups')

            if not token_groups:
                error = Error(
                    title = 'Restriction Error',
                    detail = 'Token data does not contain a groups attribute.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            if not isinstance(token_groups, list):
                error = Error(
                    title = 'Restriction Error',
                    detail = 'Token data groups attribute is not a list.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)

            data = request.json.get('data')
            attributes = data.get('attributes')

            groups = copy(token_groups)

            if id == token_id:
                groups.append('self')

            errors = kargs['errors'] = [ ]

            _apply_restrictions(attributes, restrictions, groups, errors, [ ])

            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def _apply_restrictions(attributes, restrictions, groups, errors, path):
    for (key, allowed_groups) in restrictions.items():
        if isinstance(allowed_groups, dict):
            if attributes.get(key):
                _path = copy(path)
                _path.append(key)
                _apply_restrictions(attributes[key], restrictions[key], groups, errors, _path)
        else:
            if not _contains_any(groups, allowed_groups):
                if attributes.get(key):
                    del attributes[key]
                    attribute = f'{key}'
                    if path:
                        attribute = f'{".".join(path)}.{attribute}'
                    error = Error(
                        title = 'Restriction Error',
                        detail = f'Cannot set attribute: {attribute}',
                        status = 403
                    )
                    errors.append(error)
        if isinstance(attributes.get(key), dict):
            if not attributes.get(key):
                del attributes[key]

def _contains_any(groups, allowed_groups):
    for group in allowed_groups:
        if group in groups:
            return True
    return False
