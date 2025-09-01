from etiket_client.remote.errors import api_tokens, tokens, scopes, usergroups, permissions, users

ERROR_CLASSES = [api_tokens.APITokenErrors, tokens.OAuth2Errors, tokens.TokenAuthErrors,\
                 scopes.ScopeErrors, users.UserErrors, usergroups.UsergroupErrors,\
                 permissions.PermissionErrors]
class EtiketError(Exception):
    """Raised when the error is unknown."""

def http_exception_handler(error_message: dict) -> EtiketError:
    error = error_message.get("error")
    detail = error_message.get("detail")
    for error_class in ERROR_CLASSES:
        if error in error_class:
            if "trace_id" in error:
                detail += f" | Trace ID: {error_message.get('trace_id')}"
                
            raise error_class[error](detail)
    return EtiketError(detail)