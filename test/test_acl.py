from unittest import TestCase

from sugar_api.acl import _check_acl

class ACLTest(TestCase):

    def test_action_no_token_invalid(self):

        result = _check_acl('action', {
            'unauthorized': [ ]
        }, None, None)

        self.assertFalse(result)

    def test_action_no_token_valid(self):

        result = _check_acl('action', {
            'unauthorized': ['action']
        }, None, None)

        self.assertTrue(result)

    def test_action_self_invalid(self):

        result = _check_acl('action', {
            'self': [ ]
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc')

        self.assertFalse(result)

    def test_action_self_valid(self):

        result = _check_acl('action', {
            'self': ['action']
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc')

        self.assertTrue(result)

    def test_action_group_invalid(self):

        result = _check_acl('action', {
            'test_group': [ ]
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertFalse(result)

    def test_action_group_valid(self):

        result = _check_acl('action', {
            'test_group': ['action']
        }, {
            'data': { 'type': 'test_group' }
        }, None)

        self.assertTrue(result)

    def test_action_other_invalid(self):

        result = _check_acl('action', {
            'other': [ ]
        }, { }, None)

        self.assertFalse(result)

    def test_action_other_valid(self):

        result = _check_acl('action', {
            'other': ['action']
        }, {
            'data': { }
        }, None)

        self.assertTrue(result)

    def test_action_self_and_group(self):

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
