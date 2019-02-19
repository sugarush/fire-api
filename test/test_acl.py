from unittest import TestCase
from sugar_asynctest import AsyncTestCase
from sugar_odm import MemoryModel, Model, Field

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
            'data': { 'groups': [ 'test_group' ] }
        }, None, None)

        self.assertFalse(result)

    async def test_check_acl_group_valid(self):

        result = await _check_acl('action', {
            'test_group': ['action']
        }, {
            'data': { 'groups': [ 'test_group' ] }
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

    async def test_check_acl_other_skip_self(self):

        result = await _check_acl('action', {
            'self': [ ],
            'other': ['action']
        }, {
            'data': { 'id': 'aabbcc' }
        }, 'aabbcc', None)

        self.assertFalse(result)

    async def test_check_acl_other_skip_group(self):

        result = await _check_acl('action', {
            'test_group': [ ],
            'other': ['action']
        }, {
            'data': { 'groups': [ 'test_group' ] }
        }, None, None)

        self.assertFalse(result)

    async def test_check_acl_self_and_group(self):

        result = await _check_acl('action', {
            'self': ['action'],
            'test_group': [ ]
        }, {
            'data': { 'groups': [ 'test_group' ] }
        }, None, None)

        self.assertTrue(result)

        result = await _check_acl('action', {
            'self': [ ],
            'test_group': ['action']
        }, {
            'data': { 'groups': [ 'test_group' ] }
        }, None, None)

        self.assertTrue(result)

    async def test_check_acl_field_invalid(self):

        class Beta(MemoryModel):
            pass

        class Alpha(MemoryModel):
            owner = Field()

        beta = Beta()
        await beta.save()

        alpha = Alpha()
        alpha.owner = 'invalid'
        await alpha.save()

        result = await _check_acl('action', {
            '$owner': ['action']
        }, {
            'data': { 'id': beta.id }
        }, alpha.id, Alpha)

        self.assertFalse(result)

    async def test_check_acl_field_valid(self):

        class Beta(MemoryModel):
            pass

        class Alpha(MemoryModel):
            owner = Field()

        beta = Beta()
        await beta.save()

        alpha = Alpha()
        alpha.owner = beta.id
        await alpha.save()

        result = await _check_acl('action', {
            '$owner': ['action']
        }, {
            'data': { 'id': beta.id }
        }, alpha.id, Alpha)

        self.assertTrue(result)

    async def test_check_acl_field_valid_nested(self):

        class Gamma(Model):
            owner = Field()

        class Beta(MemoryModel):
            pass

        class Alpha(MemoryModel):
            gamma = Field(type=Gamma)

        beta = Beta()
        await beta.save()

        alpha = Alpha()
        alpha.gamma = { 'owner': beta.id }
        await alpha.save()

        result = await _check_acl('action', {
            '$gamma.owner': ['action']
        }, {
            'data': { 'id': beta.id }
        }, alpha.id, Alpha)

        self.assertTrue(result)

    async def test_check_acl_field_self_skip(self):

        class Beta(MemoryModel):
            pass

        class Alpha(MemoryModel):
            owner = Field()

        beta = Beta()
        await beta.save()

        alpha = Alpha()
        alpha.owner = beta.id
        await alpha.save()

        result = await _check_acl('action', {
            'self': [ ],
            '$owner': ['action']
        }, {
            'data': { 'id': alpha.id }
        }, alpha.id, Alpha)

        self.assertFalse(result)
