class LoginFailedException(Exception):
    pass

class TokenRefreshException(Exception):
    pass

class NoLoginInfoFoundException(Exception):
    pass

class NotLoggedInException(Exception):
    pass

class APIKeyInvalidException(Exception):
    pass
class RequestFailedException(Exception):
    def __init__(self, status_code, message, *args: object) -> None:
        super().__init__(f"Code : {status_code} -- content : {message}", *args)
        self.status_code = status_code
        self.message = message
        
class uploadFailedException(Exception):
    pass

class SchemaNotValidException(Exception):
    pass

class SyncSourceNotFoundException(Exception):
    pass

class NoConvertorException(Exception):
    pass

class SynchronizationErrorException(Exception):
    pass

class UpdateSyncDatasetUUIDException(Exception):
    pass