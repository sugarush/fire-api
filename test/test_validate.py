import json

from sugar_asynctest import AsyncTestCase
from sugar_document import Document

from sugar_api import validate


async def handler(*args, **kargs):
    pass


class TestValidate(AsyncTestCase):

    default_loop = True

    async def test_validate_missing_json(self):

        request = Document({
            'json': None
        })

        decorator = validate(handler)
        response = await decorator(request)

        data = Document(json.loads(response.body))

        self.assertEqual(data.errors[0].detail, 'No data supplied.')

    async def test_validate_data_not_supplied(self):

        request = Document({
            'json': { }
        })

        decorator = validate(handler)
        response = await decorator(request)

        data = Document(json.loads(response.body))

        self.assertEqual(data.errors[0].detail, 'No data supplied.')

    async def test_validate_data_not_a_dict(self):

        request = Document({
            'json': {
                'data': 'fail'
            }
        })

        decorator = validate(handler)
        response = await decorator(request)

        data = Document(json.loads(response.body))

        self.assertEqual(data.errors[0].detail, 'Data is not a JSON object.')

    async def test_validate_attributes_not_supplied(self):

        request = Document({
            'json': {
                'data': {
                    'invalid': 'fail'
                }
            }
        })

        decorator = validate(handler)
        response = await decorator(request)

        data = Document(json.loads(response.body))

        self.assertEqual(data.errors[0].detail, 'No attributes supplied.')

    async def test_validate_attributes_not_a_dict(self):

        request = Document({
            'json': {
                'data': {
                    'attributes': 'fail'
                }
            }
        })

        decorator = validate(handler)
        response = await decorator(request)

        data = Document(json.loads(response.body))

        self.assertEqual(data.errors[0].detail, 'Attributes is not a JSON object.')
