import json

from sugar_asynctest import AsyncTestCase
from sugar_document import Document
from sugar_odm import MemoryModel, Field

from sugar_api import WebToken


def decode(response):
    return Document(json.loads(response.body.decode()))


class WebTokenTest(AsyncTestCase):

    async def test_no_data(self):

        response = await WebToken._post(Document({
            'json': { }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No data provided.')

    async def test_data_not_a_dict(self):

        response = await WebToken._post(Document({
            'json': {
                'data': 'invalid'
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Data is not a JSON object.')

    async def test_no_username(self):

        WebToken.blueprint('test', model=MemoryModel, secret='secret')

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'non-existent': 'value'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Field missing: username.')

    async def test_no_password(self):

        WebToken.blueprint('test', model=MemoryModel, secret='secret')

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'username': 'test'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Field missing: password.')

    async def test_model_not_found(self):

        class Model(MemoryModel):
            username = Field()
            password = Field()

            @classmethod
            async def find_one(cls, query):
                for id in cls.db:
                    data = cls.db[id].copy()
                    del data['id']
                    if data == query:
                        return cls(cls.db[id])
                return None

        await Model.add({
            'username': 'test',
            'password': 'ing'
        })

        WebToken.blueprint('test',
            model = Model,
            secret = 'secret',
            password_algorithm = lambda password: password
        )

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'username': 'test',
                    'password': 'invalid'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Incorrect username or password.')

    async def test_web_token(self):

        class Model(MemoryModel):
            username = Field()
            password = Field()

            @classmethod
            async def find_one(cls, query):
                for id in cls.db:
                    data = cls.db[id].copy()
                    del data['id']
                    if data == query:
                        return cls(cls.db[id])
                return None

        await Model.add({
            'username': 'test',
            'password': 'ing'
        })

        WebToken.blueprint('test',
            model = Model,
            secret = 'secret',
            password_algorithm = lambda password: password
        )

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'username': 'test',
                    'password': 'ing'
                }
            }
        }))

        response = decode(response)

        self.assertTrue(response.data.token)
