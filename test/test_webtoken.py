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

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'non-existent': 'value'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Missing username.')

    async def test_no_password(self):

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'username': 'test'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Missing password.')

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

        class Authentication(WebToken):

            @classmethod
            async def payload(cls, username, password):
                user = await Model.find_one({
                    'username': username,
                    'password': password
                })

                return user.serialize()

        await Model.add({
            'username': 'test',
            'password': 'ing'
        })

        response = await Authentication._post(Document({
            'json': {
                'data': {
                    'username': 'test',
                    'password': 'ing'
                }
            }
        }))

        response = decode(response)

        self.assertTrue(response.data.attributes.token)
