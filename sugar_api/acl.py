import json

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

def socketacl(action, Model):
    def wrapper(handler):
        async def decorator(state, doc, *args, **kargs):
            id = kargs.get('id')
            if not await _check_acl(action, Model.__acl__, state.token, id, Model):
                await state.socket.send(json.dumps({
                    'action': 'acl-restricted'
                }))
            else:
                return await handler(state, doc, *args, **kargs)
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

        specific = list(filter(lambda field: \
            field.startswith('$'), acl.keys()))

        for field in specific:
            del acl_copy[field]

        grouped = list(filter(lambda field: \
            field.startswith('#'), acl.keys()))

        for field in grouped:
            del acl_copy[field]

        skip_user_group_field = False
        skip_other = False

        data = (token or { }).get('data')

        token_id = (data or { }).get('id')
        token_groups = (data or { }).get('groups', [ ])

        # Check for unauthorized actions.
        if not isinstance(data, dict):
            skip_user_group_field = True
            skip_other = True
            if _check_action(action, acl.get('unauthorized', { })):
                valid = True

        if not skip_user_group_field and (token_id or token_groups):
            # Check for self actions.
            if id == token_id:
                # Skip checking fields if the document is self.
                skip_user_group_field = True
                # Skip checking other if document is self.
                skip_other = True
                if _check_action(action, acl.get('self', { })):
                    valid = True

            # Check for group actions.
            for group in token_groups:
                if group in acl_copy:
                    skip_other = True
                    if _check_action(action, acl_copy.get(group, { })):
                        valid = True

        # Check for field actions.
        if not skip_user_group_field and token_id and id:

            if Model and await Model.exists(id):
                model = await Model.find_by_id(id)

                specific_fields = _get_fields(model, specific, '$')
                for name, value in specific_fields.items():
                    if token_id == value:
                        if _check_action(action, acl.get(name)):
                            valid = True

                grouped_fields = _get_fields(model, grouped, '#')
                for name, value in grouped_fields.items():
                    if token_id in value:
                        if _check_action(action, acl.get(name)):
                            valid = True

        # Check for other actions.
        if not skip_other:
            if _check_action(action, acl.get('other', { })):
                    valid = True

    return valid

def _get_field(model, field, prefix):
    data = model
    field = field.lstrip(prefix)
    for key in field.split('.'):
        data = data.get(key)
        if not data:
            return None
    return data

def _get_fields(model, fields, prefix):
    model_fields = { }
    for field in fields:
        model_fields[field] = _get_field(model, field, prefix)
    return model_fields
