from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class UsergroupNotFound(Exception):
    """Raised when the usergroup cannot be found."""

class UsergroupNameAlreadyExists(Exception):
    """Raised when the usergroup name already exists."""

class UsergroupUidAlreadyExists(Exception):
    """Raised when the usergroup UID already exists."""

class UsergroupCannotModifyExternal(Exception):
    """Raised when attempting to modify an external usergroup."""

class UsergroupErrors(metaclass=EtiketExceptionsMeta):
    usergroup_not_found = UsergroupNotFound
    usergroup_name_already_exists = UsergroupNameAlreadyExists
    usergroup_uid_already_exists = UsergroupUidAlreadyExists
    usergroup_cannot_modify_external = UsergroupCannotModifyExternal