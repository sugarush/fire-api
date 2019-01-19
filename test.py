from sanic import Sanic
from sanic.response import json

from sugar_odm import MongoDB, MongoDBModel, Field
from sugar_api import JSONAPIMixin


class Name(MongoDBModel):
    first = Field(required=True)
    last = Field(required=True)


class User(MongoDBModel, JSONAPIMixin):
    name = Field(type=Name)


app = Sanic()

app.blueprint(User.blueprint(url_prefix='/v1'))

@app.route('/')
async def test(request):
    return json({ 'hello': 'world' })

@app.listener('before_server_start')
async def before_server_start(app, loop):
    MongoDB.set_event_loop(loop)

    await User.drop()

    await User.add({
        'name': {
            'first': 'lucifer',
            'last': 'avada'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1)
