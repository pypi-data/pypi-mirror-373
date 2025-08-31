from .api_jwk import PyJWK
from .api_jwk import PyJWKSet
from .api_jws import PyJWS
from .api_jws import get_algorithm_by_name
from .api_jws import get_unverified_header
from .api_jws import register_algorithm
from .api_jws import unregister_algorithm
from .api_jwt import PyJWT
from .api_jwt import decode
from .api_jwt import decode_complete
from .api_jwt import encode
from .exceptions import DecodeError
from .exceptions import ExpiredSignatureError
from .exceptions import ImmatureSignatureError
from .exceptions import InvalidAlgorithmError
from .exceptions import InvalidAudienceError
from .exceptions import InvalidIssuedAtError
from .exceptions import InvalidIssuerError
from .exceptions import InvalidKeyError
from .exceptions import InvalidSignatureError
from .exceptions import InvalidTokenError
from .exceptions import MissingRequiredClaimError
from .exceptions import PyJWKClientConnectionError
from .exceptions import PyJWKClientError
from .exceptions import PyJWKError
from .exceptions import PyJWKSetError
from .exceptions import PyJWTError
from .jwks_client import PyJWKClient

__version__ = "2.10.1"

__title__ = "PyJWT"
__description__ = "JSON Web Token implementation in Python"
__url__ = "https://pyjwt.readthedocs.io"
__uri__ = __url__
__doc__ = f"{__description__} <{__uri__}>"

__author__ = "José Padilla"
__email__ = "hello@jpadilla.com"

__license__ = "MIT"
__copyright__ = "Copyright 2015-2022 José Padilla"


__all__ = [
    "PyJWS",
    "PyJWT",
    "PyJWKClient",
    "PyJWK",
    "PyJWKSet",
    "decode",
    "decode_complete",
    "encode",
    "get_unverified_header",
    "register_algorithm",
    "unregister_algorithm",
    "get_algorithm_by_name",
    # Exceptions
    "DecodeError",
    "ExpiredSignatureError",
    "ImmatureSignatureError",
    "InvalidAlgorithmError",
    "InvalidAudienceError",
    "InvalidIssuedAtError",
    "InvalidIssuerError",
    "InvalidKeyError",
    "InvalidSignatureError",
    "InvalidTokenError",
    "MissingRequiredClaimError",
    "PyJWKClientConnectionError",
    "PyJWKClientError",
    "PyJWKError",
    "PyJWKSetError",
    "PyJWTError",
]
