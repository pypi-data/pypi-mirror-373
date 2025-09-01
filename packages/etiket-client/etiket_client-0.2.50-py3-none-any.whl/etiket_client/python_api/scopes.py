import requests, uuid, socket, ssl, urllib3

from etiket_client.local.dao.scope import dao_scope, ScopeReadWithUsers
from etiket_client.local.database import Session

from etiket_client.remote.errors import CONNECTION_ERRORS

from etiket_client.settings.user_settings import user_settings
from etiket_client.sync.backends.native.sync_scopes import sync_scopes

from typing import List


def get_selected_scope() -> ScopeReadWithUsers:
    user_settings.load()
    with Session() as session:
        if user_settings.current_scope is None:
            raise ValueError("No default scope set. Please set a default scope using set_default_scope.")
        current_scope = dao_scope.read(uuid.UUID(user_settings.current_scope), session)
    return current_scope

def get_scopes() -> List[ScopeReadWithUsers]:
    with Session() as session:
        _safe_sync_scopes(session)
        scopes = dao_scope.read_all(username=user_settings.user_sub,
                                    session=session)
    return scopes

def get_scope_by_name(name : str) -> ScopeReadWithUsers:
    with Session() as session:
        _safe_sync_scopes(session)
        return dao_scope.read_by_name(name, session)

def get_scope_by_uuid(uuid : uuid.UUID) -> ScopeReadWithUsers:
    with Session() as session:
        _safe_sync_scopes(session)
        return dao_scope.read(uuid, session)

def _safe_sync_scopes(session):
    try:
        sync_scopes(session)
    except CONNECTION_ERRORS:
        pass