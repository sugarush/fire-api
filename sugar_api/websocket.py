from . acl import _check_acl

async def authenticate(state, doc):
    try:
        state.token = jwt.decode(doc.data.attributes.token, WebToken.get_secret(),
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

def exists(Model):
    def wrapper(handler):
        async def decorator(*args, **kargs):
            id = kargs.get('id')
            if not id or not await Model.exists(id):
                await state.socket.send(json.dumps({
                    'action': 'document-not-found',
                    'type': Model._table,
                    'id': id
                }))
            else:
                await handler(*args, **kargs)
        return decorator
    return wrapper
