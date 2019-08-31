from sugar_asynctest import AsyncTestCase

from sugar_api.restrictions import _apply_restrictions, _get_value


class RestrictionsTest(AsyncTestCase):

    default_loop = True

    def test_get_value(self):

        value = _get_value('test.ing', {
            'test': {
                'ing': '123'
            }
        })

        self.assertEqual(value, '123')

    def test_restrictions_allowed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = { }

        groups = [ ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ], None, '')

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_removed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = {
            'test': ['group']
        }

        groups = [ ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ], None, '')

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_group_allowed(self):

        attributes = {
            'test': 'ing'
        }

        restrictions = {
            'test': ['group']
        }

        groups = [ 'group' ]

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ], None, '')

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

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ], None, '')

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

        _apply_restrictions(attributes, restrictions, groups, [ ], [ ], None, '')

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_specific_allowed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '$owner' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': 'abcd'
        }, 'abcd')

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_specific_removed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '$owner' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': 'abc'
        }, 'abcd')

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_grouped_allowed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '#owner' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': [ 'abcd' ]
        }, 'abcd')

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_grouped_removed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '#owner' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': [ 'abc' ]
        }, 'abcd')

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_specific_nested_allowed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '$owner.id' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': {
                'id': 'abcd'
            }
        }, 'abcd')

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_specific_nested_removed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '$owner.id' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': {
                'id': 'abc'
            }
        }, 'abcd')

        self.assertIsNone(attributes.get('test'))

    def test_restrictions_grouped_nested_allowed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '#owner.id' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner': {
                'id': [ 'abcd' ]
            }
        }, 'abcd')

        self.assertIsNotNone(attributes.get('test'))

    def test_restrictions_grouped_nested_removed(self):

        attributes = {
            'test': 'value'
        }

        restrictions = {
            'test': [ '#owner.id' ]
        }

        _apply_restrictions(attributes, restrictions, None, [ ], [ ], {
            'owner':{
                'id': [ 'abc' ]
            }
        }, 'abcd')

        self.assertIsNone(attributes.get('test'))
