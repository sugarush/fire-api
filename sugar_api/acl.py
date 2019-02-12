from . header import jsonapi

from . error import Error


def acl(action, acl, Model=None):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            token = kargs.get('token')
            id = kargs.get('id')
            if not await _check_acl(action, acl, token, id, Model):
                error = Error(
                    title = 'ACL Error',
                    detail = 'Insufficient priviliges.',
                    status = 403
                )
                return jsonapi({ 'errors': [ error.serialize() ] }, status=403)
            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def _check_action(action, actions):
    if action in actions:
        return True
    if 'all' in actions:
        return True
    return False

async def _check_acl(action, acl, token, id, Model):

    valid = True

    if acl:

        valid = False

        acl_copy = acl.copy()

        try:
            del acl_copy['unauthorized']
        except:
            pass

        try:
            del acl_copy['self']
        except:
            pass

        try:
            del acl_copy['other']
        except:
            pass

        fields = list(filter(lambda field: \
            field.startswith('$'), acl.keys()))

        for field in fields:
            del acl_copy[field]

        skip_user_group_field = False
        skip_other = False

        data = (token or { }).get('data')

        token_id = (data or { }).get('id')
        token_type = (data or { }).get('type')

        # Check for unauthorized actions.
        if not isinstance(data, dict):
            skip_user_group_field = True
            skip_other = True
            if _check_action(action, acl.get('unauthorized', { })):
                valid = True

        if not skip_user_group_field and (token_id or token_type):
            skip_other = True
            # Check for self actions.
            if id == token_id:
                # Skip checking fields if the document is self.
                skip_user_group_field = True
                if _check_action(action, acl.get('self', { })):
                    valid = True

            # Check for group actions.
            if token_type:
                if _check_action(action, acl_copy.get(token_type, { })):
                    valid = True

        # Check for field actions.
        if not skip_user_group_field and token_id:
            if Model and await Model.exists(id):
                model = await Model.find_by_id(id)
                model_fields = _get_fields(model, fields)
                for name, value in model_fields.items():
                    if token_id == value:
                        if _check_action(action, acl.get(name)):
                            valid = True

        # Check for other actions.
        if not skip_other:
            if _check_action(action, acl.get('other', { })):
                    valid = True

    return valid

def _get_field(model, field):
    data = model
    field = field.lstrip('$')
    for key in field.split('.'):
        data = data.get(key)
        if not data:
            return None
    return data

def _get_fields(model, fields):
    model_fields = { }
    for field in fields:
        model_fields[field] = _get_field(model, field)
    return model_fields
