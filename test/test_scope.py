from unittest import TestCase

from sugar_api.scope import _check_scope


class ScopeTest(TestCase):

    def test_scope_valid(self):

        result = _check_scope({
            'action': True
        }, {
            'action': True
        }, { })

        self.assertTrue(result)

    def test_scope_invalid(self):

        result = _check_scope({
            'action': True
        }, {
            'action': False
        }, { })

        self.assertFalse(result)

    def test_scope_missing(self):

        result = _check_scope({
            'action': True
        }, { }, { })

        self.assertFalse(result)

    def test_scope_karg_valid(self):

        result = _check_scope({
            'action': '$value'
        }, {
            'action': 'aabbcc'
        }, {
            'value': 'aabbcc'
        })

        self.assertTrue(result)

    def test_scope_karg_invalid(self):

        result = _check_scope({
            'action': '$value'
        }, {
            'action': 'aabbcc',
        }, {
            'value': 'ddeeff'
        })

        self.assertFalse(result)

    def test_scope_karg_missing_token(self):

        result = _check_scope({
            'action': '$value'
        }, { }, {
            'value': 'aabbcc'
        })

        self.assertFalse(result)

    def test_scope_karg_missing_karg(self):

        result = _check_scope({
            'action': '$value'
        }, {
            'action': 'aabbcc'
        }, { })

        self.assertFalse(result)

    def test_scope_karg_token_list_valid(self):

        result = _check_scope({
            'action': '#value'
        }, {
            'action': [ 'aabbcc' ]
        }, {
            'value': 'aabbcc'
        })

        self.assertTrue(result)

    def test_scope_karg_token_list_invalid(self):

        result = _check_scope({
            'action': '#value'
        }, {
            'action': [ 'aabbcc' ]
        }, {
            'value': 'ddeeff'
        })

        self.assertFalse(result)

    def test_scope_karg_token_list_missing_token(self):

        result = _check_scope({
            'action': '#value'
        }, { }, {
            'value': 'aabbcc'
        })

        self.assertFalse(result)

    def test_scope_karg_token_list_missing_karg(self):

        result = _check_scope({
            'action': '#value'
        }, {
            'action': [ 'aabbcc' ]
        }, { })

        self.assertFalse(result)
