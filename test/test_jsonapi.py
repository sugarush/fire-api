import json

from sugar_asynctest import AsyncTestCase
from sugar_document import Document

from sugar_api import JSONAPIMixin


def decode(response):
    return Document(json.loads(response.body.decode()))


class Mixin(JSONAPIMixin):
    _table = 'test'


class JSONAPIMixinTest(AsyncTestCase):

    async def test_create_data_missing(self):

        test = Mixin()

        response = await test._create(Document({
            'json': { }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No data supplied.')

    async def test_create_data_not_a_dict(self):

        test = Mixin()

        response = await test._create(Document({
            'json': {
                'data': 'invalid'
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Data is not a JSON object.')

    async def test_create_type_missing(self):

        test = Mixin()

        response = await test._create(Document({
            'json': {
                'data': {
                    'test': 'ing'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Type is missing.')

    async def test_create_type_mismatch(self):

        test = Mixin()

        response = await test._create(Document({
            'json': {
                'data': {
                    'type': 'invalid'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Provided type does not match resource type.')

    async def test_create_attributes_missing(self):

        test = Mixin()

        response = await test._create(Document({
            'json': {
                'data': {
                    'type': 'test'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No attributes supplied.')
