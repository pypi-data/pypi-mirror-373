"""
Tests for token unpacking and verifying.
"""

import unittest
from time import time
from unittest.mock import patch

from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, MissingRequiredClaimError

from token_utils import api
from token_utils.sign import _encode_and_sign, create_jwt
from token_utils.unpack import unpack_jwt

test_user_id = 121
invalid_test_user_id = 120
test_timeout = 1000
test_now = int(time())
test_claims = {"foo": "bar", "baz": "quux", "meaning": 42}
expected_full_token = {
    "lms_user_id": test_user_id,
    "iat": test_now,
    "exp": test_now + test_timeout,
    "iss": "token-test-issuer",  # these lines from test_settings.py
    "version": "1.2.0",  # these lines from test_settings.py
}


class TestUnpack(unittest.TestCase):
    def test_unpack_jwt(self):
        token = create_jwt(test_user_id, test_timeout, {}, test_now)
        decoded = unpack_jwt(token, test_user_id, test_now)

        self.assertEqual(expected_full_token, decoded)

    def test_unpack_jwt_with_claims(self):
        token = create_jwt(test_user_id, test_timeout, test_claims, test_now)

        expected_token_with_claims = expected_full_token.copy()
        expected_token_with_claims.update(test_claims)

        decoded = unpack_jwt(token, test_user_id, test_now)

        self.assertEqual(expected_token_with_claims, decoded)

    def test_malformed_token(self):
        token = create_jwt(test_user_id, test_timeout, test_claims, test_now)
        token = token + "a"

        expected_token_with_claims = expected_full_token.copy()
        expected_token_with_claims.update(test_claims)

        with self.assertRaises(InvalidSignatureError):
            unpack_jwt(token, test_user_id, test_now)

    @patch('token_utils.api.unpack_jwt')
    def test_unpack_api_hooked_up(self, mock_unpack):
        expected_token_with_claims = expected_full_token.copy()
        expected_token_with_claims.update(test_claims)
        mock_unpack.return_value = expected_token_with_claims

        token = create_jwt(test_user_id, test_timeout, test_claims, test_now)
        api_token = api.unpack_token_for(token, test_user_id)

        # we've verified full token flow, just check that an item came through properly
        self.assertEqual(42, api_token['meaning'])
        # and an item from config came through properly
        self.assertEqual('token-test-issuer', api_token['iss'])

    def test_unpack_token_with_invalid_user(self):
        token = create_jwt(invalid_test_user_id, test_timeout, {}, test_now)

        with self.assertRaises(InvalidSignatureError):
            unpack_jwt(token, test_user_id, test_now)

    def test_unpack_expired_token(self):
        token = create_jwt(test_user_id, test_timeout, {}, test_now)

        with self.assertRaises(ExpiredSignatureError):
            unpack_jwt(token, test_user_id, test_now + test_timeout + 1)

    def test_missing_expired_lms_user_id(self):
        payload = expected_full_token.copy()
        del payload['lms_user_id']
        token = _encode_and_sign(payload)

        with self.assertRaises(MissingRequiredClaimError):
            unpack_jwt(token, test_user_id, test_now)

    def test_missing_expired_key(self):
        payload = expected_full_token.copy()
        del payload['exp']
        token = _encode_and_sign(payload)

        with self.assertRaises(MissingRequiredClaimError):
            unpack_jwt(token, test_user_id, test_now)
