from sanic import Sanic
from sanic.response import json

from sugar_odm import Model, Field
from sugar_api import JSONAPIMixin


class Name(Model):
    first = Field(required=True)
    last = Field(required=True)


class User(Model, JSONAPIMixin):
    id = Field(primary=True)
    name = Field(type=Name)


app = Sanic()

app.blueprint(User.blueprint())

@app.route('/')
async def test(request):
    return json({ 'hello': 'world' })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=1)
