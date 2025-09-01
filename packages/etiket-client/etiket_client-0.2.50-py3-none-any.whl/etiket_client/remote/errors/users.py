from etiket_client.remote.errors.meta import EtiketExceptionsMeta

class UserSubAlreadyExists(Exception):
    """Raised when the user sub already exists."""

class UserMailAlreadyExists(Exception):
    """Raised when the user email already exists."""

class UserNotFound(Exception):
    """Raised when the user cannot be found."""

class UsersNotFound(Exception):
    """Raised when the users cannot be found."""

class UserIsDisabled(Exception):
    """Raised when the user account is disabled."""

class UserCannotSelfDelete(Exception):
    """Raised when a user attempts to delete their own account."""

class UserErrors(metaclass=EtiketExceptionsMeta):
    user_sub_already_exists = UserSubAlreadyExists
    user_mail_already_exists = UserMailAlreadyExists
    user_not_found = UserNotFound
    users_not_found = UsersNotFound
    user_is_disabled = UserIsDisabled
    user_cannot_self_delete = UserCannotSelfDelete
