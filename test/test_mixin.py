import json

from sugar_asynctest import AsyncTestCase
from sugar_document import Document
from sugar_odm import MongoDBModel, Field

from sugar_api import JSONAPIMixin


def decode(response):
    return Document(json.loads(response.body.decode()))


class Mixin(MongoDBModel, JSONAPIMixin):
    field = Field()


class JSONAPIMixinTest(AsyncTestCase):

    default_loop = True

    async def test_create_type_missing(self):

        #response = await Mixin._create(Document({
        #    'json': {
        #        'data': {
        #            'test': 'ing'
        #        }
        #    }
        #}))

        decorator = Mixin._check_create(None)

        response = await decorator(Document({
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

        #response = await Mixin._create(Document({
        #    'json': {
        #        'data': {
        #            'type': 'invalid'
        #        }
        #    }
        #}))

        decorator = Mixin._check_create(None)

        response = await decorator(Document({
            'json': {
                'data': {
                    'type': 'invalid'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Provided type does not match resource type.')

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

        response = await Mixin._read(Document({
            'args': { }
        }), test.id)

        response = decode(response)

        self.assertEqual(response.data.id, test.id)

        await Mixin.drop()

    async def test_read_by_id_no_data_found(self):

        response = await Mixin._read(Document({
            'args': { }
        }), 'aabbccddeeffaabbccddeeff')

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'No data found.')

    async def test_read_multiple(self):

        await Mixin.add([
            { },
            { },
            { }
        ])

        response = await Mixin._read(Document({
            'args': { }
        }))

        response = decode(response)

        self.assertEqual(len(response.data), 3)

        await Mixin.drop()

    async def test_read_multiple_limit(self):

        await Mixin.add([
            { },
            { },
            { }
        ])

        response = await Mixin._read(Document({
            'args': {
                'page[limit]': 1
            }
        }))

        response = decode(response)

        self.assertEqual(len(response.data), 1)

        await Mixin.drop()

    async def test_read_multiple_offset(self):

        await Mixin.add([
            { 'field': '1' },
            { 'field': '2' },
            { 'field': '3'}
        ])

        response = await Mixin._read(Document({
            'args': {
                'page[limit]': 1,
                'page[offset]': 1,
                'sort': 'field'
            }
        }))

        response = decode(response)

        self.assertEqual(response.data[0].attributes.field, '2')

        await Mixin.drop()

    async def test_read_multiple_no_data_found(self):

        response = await Mixin._read(Document({
            'args': { }
        }))

        response = decode(response)

        self.assertEqual(len(response.data), 0)

    async def test_read_multiple_query(self):

        await Mixin.add({
            'field': 'value'
        })

        response = await Mixin._read(Document({
            'args': {
                'query': '{ "field": "value" }'
            }
        }))

        response = decode(response)

        self.assertEqual(response.data[0].attributes.field, 'value')

        await Mixin.drop()

    async def test_read_multiple_sort_ascending(self):

        await Mixin.add([
            { 'field': '2' },
            { 'field': '1' },
            { 'field': '3' }
        ])

        response = await Mixin._read(Document({
            'args': {
                'sort': 'field'
            }
        }))

        response = decode(response)

        count = 1

        for data in response.data:
            self.assertEqual(data.attributes.field, str(count))
            count += 1

        await Mixin.drop()

    async def test_read_multiple_sort_descending(self):

        await Mixin.add([
            { 'field': '2' },
            { 'field': '1' },
            { 'field': '3' }
        ])

        response = await Mixin._read(Document({
            'args': {
                'sort': '-field'
            }
        }))

        response = decode(response)

        count = 3

        for data in response.data:
            self.assertEqual(data.attributes.field, str(count))
            count -= 1

        await Mixin.drop()

    async def test_read_multiple_sort_missing(self):

        await Mixin.add([
            { 'field': '2' },
            { 'field': '1' },
            { 'field': '3' }
        ])

        response = await Mixin._read(Document({
            'args': { }
        }))

        response = decode(response)

        count = 0

        results = [ '2', '1', '3' ]

        for data in response.data:
            self.assertEqual(data.attributes.field, results[count])
            count += 1

        await Mixin.drop()

    async def test_update_type_missing(self):

        #response = await Mixin._update(Document({
        #    'json': {
        #        'data': {
        #            'non-existent': 'value'
        #        }
        #    }
        #}))

        decorator = Mixin._check_update(None)

        response = await decorator(Document({
            'json': {
                'data': {
                    'non-existent': 'value'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Type is missing.')

    async def test_update_type_mismatch(self):

        #response = await Mixin._update(Document({
        #    'json': {
        #        'data': {
        #            'type': 'invalid'
        #        }
        #    }
        #}))

        decorator = Mixin._check_update(None)

        response = await decorator(Document({
            'json': {
                'data': {
                    'type': 'invalid'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'Type in payload does not match collection type.')

    async def test_update_id_missing(self):

        #response = await Mixin._update(Document({
        #    'json': {
        #        'data': {
        #            'type': 'mixins'
        #        }
        #    }
        #}))

        decorator = Mixin._check_update(None)

        response = await decorator(Document({
            'json': {
                'data': {
                    'type': 'mixins'
                }
            }
        }))

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'ID is missing.')

    async def test_update_id_mismatch(self):

        #response = await Mixin._update(Document({
        #    'json': {
        #        'data': {
        #            'type': 'mixins',
        #            'id': 'alpha'
        #        }
        #    }
        #}), 'beta')

        decorator = Mixin._check_update(None)

        response = await decorator(Document({
            'json': {
                'data': {
                    'type': 'mixins',
                    'id': 'alpha'
                }
            }
        }), 'beta')

        response = decode(response)

        self.assertEqual(response.errors[0].detail, 'ID provided does not match ID in the URL.')

    async def test_delete_id_missing(self):

        test = Mixin()

        await test.save()

        response = await Mixin._delete(Document({
            'json': { }
        }), test.id)

        response = decode(response)

        self.assertDictEqual(response, {
            'data': {
                'id': test.id
            }
        })
