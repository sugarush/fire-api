import json

from unittest import skip

from fire_asynctest import AsyncTestCase
from fire_document import Document
from fire_odm import MemoryModel, Field

from fire_api import WebToken


def decode(response):
    return Document(json.loads(response.body.decode()))


class WebTokenTest(AsyncTestCase):

    default_loop = True

    @skip('')
    async def test_no_data(self):

        response = await WebToken._post(Document({
            'json': { }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No data provided.')

    @skip('')
    async def test_data_not_a_dict(self):

        response = await WebToken._post(Document({
            'json': {
                'data': 'invalid'
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Data is not a JSON object.')

    @skip('')
    async def test_no_username(self):

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'attributes': {
                        'non-existent': 'value'
                    }
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Missing username.')

    @skip('')
    async def test_no_password(self):

        response = await WebToken._post(Document({
            'json': {
                'data': {
                    'attributes': {
                        'username': 'test'
                    }
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Missing password.')

    @skip('')
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
                    'attributes': {
                        'username': 'test',
                        'password': 'ing'
                    }
                }
            }
        }))

        response = decode(response)

        self.assertTrue(response.data.attributes.token)
