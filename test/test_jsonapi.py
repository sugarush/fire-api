import json

from sugar_asynctest import AsyncTestCase
from sugar_document import Document
from sugar_odm import MemoryModel, Field

from sugar_api import JSONAPIMixin


def decode(response):
    return Document(json.loads(response.body.decode()))


class Mixin(MemoryModel, JSONAPIMixin):
    field = Field()


class JSONAPIMixinTest(AsyncTestCase):

    async def test_create_data_missing(self):

        response = await Mixin._create(Document({
            'json': { }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No data supplied.')

        await Mixin.drop()

    async def test_create_data_not_a_dict(self):

        response = await Mixin._create(Document({
            'json': {
                'data': 'invalid'
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Data is not a JSON object.')

        await Mixin.drop()

    async def test_create_type_missing(self):

        response = await Mixin._create(Document({
            'json': {
                'data': {
                    'test': 'ing'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Type is missing.')

        await Mixin.drop()

    async def test_create_type_mismatch(self):

        response = await Mixin._create(Document({
            'json': {
                'data': {
                    'type': 'invalid'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Provided type does not match resource type.')

        await Mixin.drop()

    async def test_create_attributes_missing(self):

        response = await Mixin._create(Document({
            'json': {
                'data': {
                    'type': 'mixins'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No attributes supplied.')

        await Mixin.drop()

    async def test_create_from_json_exception(self):

        response = await Mixin._create(Document({
            'json': {
                'data': {
                    'type': 'mixins',
                    'attributes': {
                        'undefined_field': 'invalid'
                    }
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Mixin has undefined fields: undefined_field')

        await Mixin.drop()

    async def test_create_id_already_exists(self):

        test = Mixin()

        await test.save()

        response = await Mixin._create(Document({
            'json': {
                'data': {
                    'type': 'mixins',
                    'id': test.id,
                    'attributes': {
                        'field': 'value'
                    }
                }
            }
        }))

        response = decode(response)

        self.assertTrue(response.errors[0].detail.endswith('already exists.'))

        await Mixin.drop()

    async def test_read_by_id(self):

        test = Mixin()

        await test.save()

        response = await Mixin._read(None, test.id)

        response = decode(response)

        self.assertEqual(response.data.id, test.id)

        await Mixin.drop()

    async def test_read_multiple(self):

        await Mixin.add([
            { },
            { },
            { }
        ])

        response = await Mixin._read(Document({
            'args': ''
        }))

        response = decode(response)

        self.assertEqual(len(response.data), 3)

        await Mixin.drop()
