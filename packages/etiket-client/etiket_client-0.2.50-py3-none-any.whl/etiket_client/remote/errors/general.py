
from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class ServerError(Exception):
    """Raised when a general server error occurs."""
    
class GeneralErrors(metaclass=EtiketExceptionsMeta):
    server_error = ServerError