import jwt
import json

from . acl import _check_acl
from . webtoken import WebToken

async def authenticate(state, doc):
    '''
    Authenticate a websocket connection.
    '''
    try:
        state.token = jwt.decode(doc.token, WebToken.get_secret(),
            algorithms=[WebToken.get_algolithm()],
            options=WebToken.get_options()
        )
    except jwt.ExpiredSignatureError:
        await state.socket.send(json.dumps({
            'action': 'token-expired'
        }))
    except jwt.ImmatureSignatureError:
        await state.socket.send(json.dumps({
            'action': 'token-immature'
        }))
    except Exception as e:
        await state.socket.send(json.dumps({
            'action': 'token-error'
        }))
    else:
        await state.socket.send(json.dumps({
            'action': 'authenticated'
        }))

async def deauthenticate(state, doc):
    '''
    Deauthenticate a websocket connection.
    '''
    ids = list(state.index.keys())
    for id in ids:
        del state.index[id]
    state.token = None
    await state.socket.send(json.dumps({
        'action': 'deauthenticated'
    }))

async def status(state, doc):
    '''
    Trigger an `authenticated` or `deauthenticated` event.
    '''
    await state.socket.send(json.dumps({
        'action': 'authenticated' if state.token else 'deauthenticated'
    }))

def exists(Model):
    '''
    Verify that a document exists for `Model` for the `id` in the request's path.
    '''
    def wrapper(handler):
        async def decorator(state, doc, *args, **kargs):
            id = kargs.get('id')
            if not id or not await Model.exists(id):
                await state.socket.send(json.dumps({
                    'action': 'document-not-found',
                    'type': Model._table,
                    'id': id
                }))
            else:
                return await handler(state, doc, *args, **kargs)
        return decorator
    return wrapper
