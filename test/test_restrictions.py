from sugar_asynctest import AsyncTestCase

from sugar_api.restrictions import _apply_restrictions


class RestrictionsTest(AsyncTestCase):

    default_loop = True

    def test_restrictions_allowed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = { }

        groups = [ ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ])

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_removed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = {
            'test': ['group']
        }

        groups = [ ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ])

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_group_allowed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = {
            'test': ['group']
        }

        groups = [ 'group' ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ])

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_nested_allowed(self):

        attributes = {
            'test': {
                'ing': 'value'
            }
        }

        restrictions = {
            'test': {
                'ing': ['group']
            }
        }

        groups = [ 'group' ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ])

        self.assertIsNotNone(attributes['test'].get('ing'))

    def test_restrictions_nested_removed(self):

        attributes = {
            'test': {
                'ing': 'value'
            }
        }

        restrictions = {
            'test': {
                'ing': ['group']
            }
        }

        groups = [ ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ])

        print(attributes)

        self.assertIsNone(attributes.get('test'))
