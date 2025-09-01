import uuid
# scope exceptions
class ScopeDoesAlreadyExistException(Exception):
    pass
class ScopeDoesNotExistException(Exception):
    def __init__(self, scope_identifier = None):
        if isinstance(scope_identifier, uuid.UUID):
            super().__init__(f"Scope with uuid {scope_identifier} does not exist")
        else:
            super().__init__(f"Scope with name {scope_identifier} does not exist")

class MultipleScopesWithSameNameException(Exception):
    def __init__(self, names : list):
        super().__init__(f"Multiple scopes with the same name found: {names}")

class CannotDeleteAScopeWithDatasetsException(Exception):
    pass
class MemberHasNoBusinessInThisScopeException(Exception):
    pass
class UserAlreadyNotPartOfScopeException(Exception):
    pass
class UserAlreadyPartOfScopeException(Exception):
    pass
class SchemaAlreadyAssignedException(Exception):
    pass

# user exceptions
class UserAlreadyExistsException(Exception):
    pass
class UserMailAlreadyRegisteredException(Exception):
    pass
class UserDoesNotExistException(Exception):
    pass

# schema exceptions
class SchemaDoesNotExistException(Exception):
    pass
class SchemaDoesAlreadyExistException(Exception):
    pass

# dataset exceptions
class  DatasetAlreadyExistException(Exception):
    pass
class DatasetAltUIDAlreadyExistException(Exception):
    pass
class DatasetNotFoundException(Exception):
    pass

class MultipleDatasetFoundException(Exception):
    pass

class DatasetFoundInMultipleScopesException(Exception):
    pass

# files exceptions
class FileNotAvailableException(Exception):
    pass
class FileAlreadyExistsException(Exception):
    pass
class UnexpectedFileVersionException(Exception):
    pass