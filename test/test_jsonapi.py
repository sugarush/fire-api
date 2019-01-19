import asyncio

from sanic import Sanic

from sugar_asynctest import AsyncTestCase
from sugar_odm import Model

from sugar_api import JSONAPIMixin


class JSONAPIMixinTest(AsyncTestCase):

    async def test_create_no_data(self):

        app = Sanic()

        print(app)
