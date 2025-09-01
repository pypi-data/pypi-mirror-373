from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class PermissionsInsufficient(Exception):
    """Raised when the user has insufficient permissions."""
    
class PermissionErrors(metaclass=EtiketExceptionsMeta):
    permissions_insufficient = PermissionsInsufficient