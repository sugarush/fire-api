from unittest import TestCase

from sugar_api.acl import _check_acl, _check_action

class ACLTest(TestCase):

    def test_check_action_invalid(self):

        result = _check_action('action', [ ])

        self.assertFalse(result)

    def test_check_action_valid(self):

        result = _check_action('action', [ 'action' ])

        self.assertTrue(result)

    def test_check_action_all(self):

        result = _check_action('action', [ 'all' ])

        self.assertTrue(result)

    def test_check_acl_no_token_invalid(self):

        result = _check_acl('action', {
            'unauthorized': [ ]
        }, None, None)

        self.assertFalse(result)

    def test_check_acl_no_token_valid(self):

        result = _check_acl('action', {
            'unauthorized': ['action']
        }, None, None)

        self.assertTrue(result)

    def test_check_acl_self_invalid(self):

        result = _check_acl('action', {
            'self': [ ]
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc')

        self.assertFalse(result)

    def test_check_acl_self_valid(self):

        result = _check_acl('action', {
            'self': ['action']
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc')

        self.assertTrue(result)

    def test_check_acl_group_invalid(self):

        result = _check_acl('action', {
            'test_group': [ ]
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertFalse(result)

    def test_check_acl_group_valid(self):

        result = _check_acl('action', {
            'test_group': ['action']
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertTrue(result)

    def test_check_acl_other_invalid(self):

        result = _check_acl('action', {
            'other': [ ]
        }, { }, None)

        self.assertFalse(result)

    def test_check_acl_other_valid(self):

        result = _check_acl('action', {
            'other': ['action']
        }, {
            'data': { }
        }, None)

        self.assertTrue(result)

    def test_check_acl_self_and_group(self):

        result = _check_acl('action', {
            'self': ['action'],
            'test_group': [ ]
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertTrue(result)

        result = _check_acl('action', {
            'self': [ ],
            'test_group': ['action']
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertTrue(result)
