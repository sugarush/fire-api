from sanic import Sanic
from sanic.response import json

#from sugar_odm import MongoDB
from sugar_api import WebToken

from models import User, Group


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

        group = await Group.find_by_id(user.group)

        if not group:
            raise Exception('Account type not found.')

        return {
            'data': {
                'id': user.id,
                'type': group.name
            }
        }


app = Sanic()

app.blueprint(Authentication.resource(url_prefix='/v1'))

app.blueprint(User.resource(url_prefix='/v1'))
app.blueprint(Group.resource(url_prefix='/v1'))

@app.middleware('response')
async def cross_origin_resource_sharing(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.listener('before_server_start')
async def before_server_start(app, loop):
    #MongoDB.set_event_loop(loop)

    #await User.drop()
    #await Group.drop()

    administrator = await Group.add({
        'name': 'administrator'
    })

    user = await User.add({
        'username': 'administrator',
        'password': 'administrator',
        'group': administrator.id
    })

    print('Administrator ID: ' + user.id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, workers=1)
