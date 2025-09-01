from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class ScopeNotFound(Exception):
    """Raised when the scope cannot be found."""

class ScopeAccessDenied(Exception):
    """Raised when access to the scope is denied."""

class ScopeUidInUse(Exception):
    """Raised when the scope UID is already in use."""

class ScopeErrors(metaclass=EtiketExceptionsMeta):
    scope_not_found = ScopeNotFound
    scope_access_denied = ScopeAccessDenied
    scope_uid_in_use = ScopeUidInUse