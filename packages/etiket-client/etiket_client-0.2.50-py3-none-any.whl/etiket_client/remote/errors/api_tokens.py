from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class APITokenNotFound(Exception):
    """Raised when the specified API token cannot be found."""

class APITokenAccessDenied(Exception):
    """Raised when access to the API token is denied."""

class APITokenNameAlreadyExists(Exception):
    """Raised when attempting to create a token with an existing name."""

class APITokenErrors(metaclass=EtiketExceptionsMeta):
    api_token_not_found = APITokenNotFound
    api_token_access_denied = APITokenAccessDenied
    api_token_name_already_exists = APITokenNameAlreadyExists