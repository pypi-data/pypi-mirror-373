from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class InvalidRequest(Exception):
    """The request is missing a required parameter, includes an invalid parameter value, or is otherwise malformed."""

class InvalidClient(Exception):
    """Client authentication failed."""

class InvalidGrant(Exception):
    """The provided authorization grant is invalid, expired, revoked, or was issued to another client."""

class UnauthorizedClient(Exception):
    """The authenticated client is not authorized to use this authorization grant type."""

class UnsupportedGrantType(Exception):
    """The authorization grant type is not supported by the authorization server."""

class InvalidScope(Exception):
    """The requested scope is invalid, unknown, malformed, or exceeds the scope granted."""

class AccessDenied(Exception):
    """The resource owner or authorization server denied the request."""

class UnsupportedResponseType(Exception):
    """The authorization server does not support obtaining an authorization code using this method."""

class TemporarilyUnavailable(Exception):
    """The authorization server is currently unable to handle the request."""

class TokenInvalid(Exception):
    """The provided token is invalid."""

class TokenRevoked(Exception):
    """The provided token has been revoked."""

class TokenUserCreateFailed(Exception):
    """Failed to create user from token information."""

class OAuth2Errors(metaclass=EtiketExceptionsMeta):
    invalid_request = InvalidRequest
    invalid_client = InvalidClient
    invalid_grant = InvalidGrant
    unauthorized_client = UnauthorizedClient
    unsupported_grant_type = UnsupportedGrantType
    invalid_scope = InvalidScope
    access_denied = AccessDenied
    unsupported_response_type = UnsupportedResponseType
    temporarily_unavailable = TemporarilyUnavailable

class TokenAuthErrors(metaclass=EtiketExceptionsMeta):
    token_invalid = TokenInvalid
    token_revoked = TokenRevoked
    token_user_create_failed = TokenUserCreateFailed