from sanic.response import json

from . error import Error


def acl(action, acl):
    def wrapper(handler):
        async def decorator(request, *args, **kargs):
            token = kargs.get('token')
            try:
                id = args[0]
            except:
                id = None
                if not _check_acl(action, acl, token, id):
                    error = Error(
                        title = 'ACL Error',
                        detail = 'Insufficient priviliges.',
                        status = 403
                    )
                    return json({ 'errors': [ error.serialize() ] }, status=403)
            return await handler(request, *args, **kargs)
        return decorator
    return wrapper

def _check_action(action, actions):
    if action in actions:
        return True
    if 'all' in actions:
        return True
    return False

def _check_acl(action, acl, token, id):

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

        skip_user_group = False
        skip_other = False

        data = (token or { }).get('data')

        token_id = (data or { }).get('id')
        token_type = (data or { }).get('type')

        # Check for unauthorized attributes.
        if not isinstance(data, dict):
            skip_user_group = True
            skip_other = True
            if _check_action(action, acl.get('unauthorized', { })):
                valid = True

        if not skip_user_group and (token_id or token_type):
            skip_other = True
            # Check for self attributes.
            if id == token_id:
                if _check_action(action, acl.get('self', { })):
                    valid = True

            # Check for group attributes.
            if token_type:
                if _check_action(action, acl_copy.get(token_type, { })):
                    valid = True

        # Check for other attributes.
        if not skip_other:
            if _check_action(action, acl.get('other', { })):
                    valid = True

    return valid
