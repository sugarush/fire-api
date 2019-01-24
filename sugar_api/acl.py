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

        copy = acl.copy()

        try:
            del copy['unauthorized']
        except:
            pass

        try:
            del copy['self']
        except:
            pass

        try:
            del copy['other']
        except:
            pass

        token_id = (token or { }).get('id')
        token_group = copy.get((token or { }).get('type'))

        skip_user_group = False
        skip_other = False

        # Check for unauthorized attributes.
        if not isinstance(token, dict):
            skip_user_group = True
            skip_other = True
            if _check_action(action, acl.get('unauthorized', { })):
                valid = True

        if not skip_user_group and (token_id or isinstance(token_group, list)):
            skip_other = True
            # Check for self attributes.
            if id == token_id:
                if _check_action(action, acl.get('self', { })):
                    valid = True

            # Check for group attributes.
            if isinstance(token_group, list):
                if _check_action(action, token_group):
                    valid = True

        # Check for other attributes.
        if not skip_other:
            if _check_action(action, acl.get('other', { })):
                    valid = True

    return valid
