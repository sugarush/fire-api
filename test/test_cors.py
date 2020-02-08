from unittest import TestCase

from sugar_api import CORS


class OriginsTest(TestCase):

    def test_get_origins(self):
        self.assertEqual(CORS.get_origins(), '')

    def test_set_origins(self):
        CORS.set_origins('*')

        self.assertEqual(CORS.get_origins(), '*')
