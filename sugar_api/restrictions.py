

def restrictions(restrictions):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            if not restrictions:
                return await handler(request, *args, **kargs)

            id = kargs.get('id')

            token = kargs.get('token')
            token_data = token.get('data')
            token_id = token_data.get('id')
            token_groups = token_data.get('groups')

            data = request.json.get('data')
            attributes = data.get('attributes')

            if id == token_id:
                token_groups.append('self')

            _apply_restrictions(attributes, restrictions, token_groups)

            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def _apply_restrictions(attributes, restrictions, token_groups, id):
    for (key, required_groups) in restrictions.items():
        if isinstance(required_groups, tuple):
            required_groups, _restrictions = required_groups
            if not _contains(groups, required_groups):
                if attributes.get(key):
                    del attributes[key]
            if attributes.get(key):
                _apply_restrictions(attributes[key], _restrictions, token_groups, id)
        else:
            if not _contains(groups, required_groups):
                if attributes.get(key):
                    del attributes[key]

def _contains(groups, required_groups, id):
    for group in required_groups:
        if group in groups:
            return True
    return False
