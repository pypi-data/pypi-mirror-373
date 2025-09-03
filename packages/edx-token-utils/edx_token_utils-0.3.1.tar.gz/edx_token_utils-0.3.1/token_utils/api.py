"""
Public API for token_utils.
"""
from token_utils.sign import create_jwt
from token_utils.unpack import unpack_jwt


def sign_token_for(lms_user_id, expires_in_seconds, additional_token_claims):
    """
    Produce a signed JWT token indicating some temporary permission for the indicated user.

    What permission that is must be encoded in additional_claims.
    Arguments:
        lms_user_id (int): LMS user ID this token is being generated for
        expires_in_seconds (int): Time to token expiry, specified in seconds.
        additional_token_claims (dict): Additional claims to include in the token.
    """
    return create_jwt(lms_user_id, expires_in_seconds, additional_token_claims)


def unpack_token_for(token, lms_user_id):
    """
    Unpack and verify a signed JWT token. Validate the user and expiration.

    Arguments:
        token (string): The token to be unpacked.
        lms_user_id (int): The LMS user ID that this token should match.

    Returns a valid, decoded json payload (string).
    """
    return unpack_jwt(token, lms_user_id)
