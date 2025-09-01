from etiket_client.sync.database.models_db import SyncScopeMappingsSQL
from etiket_client.sync.database.models_pydantic import sync_scope_mapping

from etiket_client.local.dao.scope import dao_scope

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

class dao_sync_scope_mapping:
    @staticmethod
    def set_mapping(mapping : sync_scope_mapping, session : Session):
        select_stmt = (
            select(SyncScopeMappingsSQL)
            .where(SyncScopeMappingsSQL.sync_source_id == mapping.sync_source_id)
            .where(SyncScopeMappingsSQL.scope_identifier == mapping.scope_identifier)
        )
        
        result = session.execute(select_stmt).scalar_one_or_none()
        
        if result is not None:
            insert_stmt = insert(SyncScopeMappingsSQL).values(**mapping.model_dump())
            session.execute(insert_stmt)
        else:
            result.scope_uuid = mapping.scope_uuid
        
        session.commit()
    
    @staticmethod
    def delete_mapping(sync_source_id : int, scope_identifier : str, session : Session):
        delete_stmt = (
            delete(SyncScopeMappingsSQL)
            .where(SyncScopeMappingsSQL.sync_source_id == sync_source_id)
            .where(SyncScopeMappingsSQL.scope_identifier == scope_identifier)
        )
        
        session.execute(delete_stmt).scalar_one_or_none()
        session.commit()
        
    @staticmethod
    def get_mappings(sync_source_id : int, auto_mapping : bool, session : Session) -> dict:
        stmt = select(SyncScopeMappingsSQL).where(SyncScopeMappingsSQL.sync_source_id == sync_source_id)
        result = session.execute(stmt).all()
        
        mapping = {res.scope_identifier : res.scope_uuid for res in result}
        if auto_mapping:
            scopes = dao_scope.read_all(session=session)
            auto_map = {scope.name : scope.uuid for scope in scopes}
            mapping = {**auto_map, **mapping}
        
        return mapping