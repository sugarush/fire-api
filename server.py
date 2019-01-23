from sanic import Sanic
from sanic.response import json

from sugar_odm import MongoDB
from sugar_api import WebToken

from models import AccountType, User


WebToken.set_secret('secret')


class Authentication(WebToken):

    @classmethod
    async def payload(cls, username, password):
        user = await User.find_one({
            'username': username,
            'password': password
        })

        if not user:
            raise Exception('Invalid username or password.')

        account_type = await AccountType.find_by_id(user.type)

        if not account_type:
            raise Exception('Account type not found.')

        return {
            'data': {
                'id': user.id,
                'type': account_type.name,
                'attributes': account_type.attributes
            }
        }


app = Sanic()

app.blueprint(Authentication.resource(url_prefix='/v1'))

app.blueprint(User.resource(url_prefix='/v1'))

@app.middleware('response')
async def cross_origin_resource_sharing(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.listener('before_server_start')
async def before_server_start(app, loop):
    MongoDB.set_event_loop(loop)

    await AccountType.drop()
    await User.drop()

    administrator = await AccountType.add({
        'name': 'administrator',
        'attributes': { }
    })

    await User.add({
        'username': 'lucifer',
        'password': 'password',
        'type': administrator.id
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1)
