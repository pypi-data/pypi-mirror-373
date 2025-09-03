"""
Tests for token creation and signing
"""
import unittest
from time import time

from jwt.exceptions import InvalidSignatureError

from token_utils import api
from token_utils.sign import create_jwt
from token_utils.unpack import unpack_and_verify

test_user_id = 121
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


class TestSign(unittest.TestCase):
    def test_create_jwt(self):
        token = create_jwt(test_user_id, test_timeout, {}, test_now)

        decoded = unpack_and_verify(token)
        self.assertEqual(expected_full_token, decoded)

    def test_create_jwt_with_claims(self):
        token = create_jwt(test_user_id, test_timeout, test_claims, test_now)

        expected_token_with_claims = expected_full_token.copy()
        expected_token_with_claims.update(test_claims)

        decoded = unpack_and_verify(token)
        self.assertEqual(expected_token_with_claims, decoded)

    def test_malformed_token(self):
        token = create_jwt(test_user_id, test_timeout, test_claims, test_now)
        token = token + "a"

        expected_token_with_claims = expected_full_token.copy()
        expected_token_with_claims.update(test_claims)

        with self.assertRaises(InvalidSignatureError):
            unpack_and_verify(token)

    def test_sign_api_hooked_up(self):
        api_token = api.sign_token_for(test_user_id, test_timeout, test_claims)
        decoded = unpack_and_verify(api_token)
        # we've verified full token flow above and have no now access via the API
        # so just check that an item we know we put in came through properly
        self.assertEqual(42, decoded['meaning'])
        # and an item from config came through properly
        self.assertEqual('token-test-issuer', decoded['iss'])
