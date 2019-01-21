from sugar_asynctest import AsyncTestCase
from sugar_document import Document

from sugar_api import JSONAPIMixin


class JSONAPIMixinTest(AsyncTestCase):

    async def test_create_no_data_supplied(self):

        test = JSONAPIMixin()

        response = await test._create(Document({ 'json': { } }))

        print(response.body)
