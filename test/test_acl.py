from unittest import TestCase
from sugar_asynctest import AsyncTestCase

from sugar_api.acl import _check_acl, _check_action

class ACLTest(AsyncTestCase):

    default_loop = True

    async def test_check_action_invalid(self):

        result = _check_action('action', [ ])

        self.assertFalse(result)

    async def test_check_action_valid(self):

        result = _check_action('action', [ 'action' ])

        self.assertTrue(result)

    async def test_check_action_all(self):

        result = _check_action('action', [ 'all' ])

        self.assertTrue(result)

    async def test_check_acl_no_token_invalid(self):

        result = await _check_acl('action', {
            'unauthorized': [ ]
        }, None, None, None)

        self.assertFalse(result)

    async def test_check_acl_no_token_valid(self):

        result = await _check_acl('action', {
            'unauthorized': ['action']
        }, None, None, None)

        self.assertTrue(result)

    async def test_check_acl_self_invalid(self):

        result = await _check_acl('action', {
            'self': [ ]
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc', None)

        self.assertFalse(result)

    async def test_check_acl_self_valid(self):

        result = await _check_acl('action', {
            'self': ['action']
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc', None)

        self.assertTrue(result)

    async def test_check_acl_group_invalid(self):

        result = await _check_acl('action', {
            'test_group': [ ]
        }, {
            'data': { 'type': 'test_group' }
        }, None, None)

        self.assertFalse(result)

    async def test_check_acl_group_valid(self):

        result = await _check_acl('action', {
            'test_group': ['action']
        }, {
            'data': { 'type': 'test_group' }
        }, None, None)

        self.assertTrue(result)

    async def test_check_acl_other_invalid(self):

        result = await _check_acl('action', {
            'other': [ ]
        }, { }, None, None)

        self.assertFalse(result)

    async def test_check_acl_other_valid(self):

        result = await _check_acl('action', {
            'other': ['action']
        }, {
            'data': { }
        }, None, None)

        self.assertTrue(result)

    async def test_check_acl_self_and_group(self):

        result = await _check_acl('action', {
            'self': ['action'],
            'test_group': [ ]
        }, {
            'data': { 'type': 'test_group' }
        }, None, None)

        self.assertTrue(result)

        result = await _check_acl('action', {
            'self': [ ],
            'test_group': ['action']
        }, {
            'data': { 'type': 'test_group' }
        }, None, None)

        self.assertTrue(result)
