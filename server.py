from sanic import Sanic
from sanic.response import json

from sugar_odm import MongoDB

from models import User


app = Sanic()

app.blueprint(User.blueprint(url_prefix='/v1'))

@app.middleware('response')
async def cross_origin_resource_sharing(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.listener('before_server_start')
async def before_server_start(app, loop):
    MongoDB.set_event_loop(loop)

    await User.drop()

    await User.add([
        {
            'name': {
                'first': 'lucifer',
                'last': 'avada'
            }
        },
        {
            'name': {
                'first': 'mom',
                'last': 'johnson'
            }
        },
        {
            'name': {
                'first': 'god',
                'last': 'johnson'
            }
        }
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1)
