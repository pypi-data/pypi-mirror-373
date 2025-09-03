"""
Token creation and signing functions.
"""

from time import time

import jwt
from django.conf import settings
from jwt.api_jwk import PyJWK


def create_jwt(lms_user_id, expires_in_seconds, additional_token_claims, now=None):
    """
    Produce an encoded JWT (string) indicating some temporary permission for the indicated user.

    What permission that is must be encoded in additional_claims.
    Arguments:
        lms_user_id (int): LMS user ID this token is being generated for
        expires_in_seconds (int): Time to token expiry, specified in seconds.
        additional_token_claims (dict): Additional claims to include in the token.
        now(int): optional now value for testing
    """
    now = now or int(time())

    payload = {
        'lms_user_id': lms_user_id,
        'exp': now + expires_in_seconds,
        'iat': now,
        'iss': settings.TOKEN_SIGNING['JWT_ISSUER'],
        'version': settings.TOKEN_SIGNING['JWT_SUPPORTED_VERSION'],
    }
    payload.update(additional_token_claims)
    return _encode_and_sign(payload)


def _encode_and_sign(payload):
    """
    Encode and sign the provided payload.

    The signing key and algorithm are pulled from settings.
    """
    private_key = PyJWK.from_json(settings.TOKEN_SIGNING['JWT_PRIVATE_SIGNING_JWK'])
    algorithm = settings.TOKEN_SIGNING['JWT_SIGNING_ALGORITHM']
    return jwt.encode(payload, key=private_key.key, algorithm=algorithm)
