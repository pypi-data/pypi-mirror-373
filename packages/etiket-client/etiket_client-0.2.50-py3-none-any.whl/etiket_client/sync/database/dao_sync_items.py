from etiket_client.sync.database.dao_scope_mappings import dao_sync_scope_mapping
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources
from etiket_client.sync.database.models_db import SyncItemsSQL
from etiket_client.sync.database.models_pydantic import new_sync_item_file, sync_item, new_sync_item_db


from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Union

from sqlalchemy import select, update, func, insert, bindparam, delete
from sqlalchemy.orm import Session

import uuid

class dao_sync_items:
    @staticmethod
    def write_sync_items(sync_source_id : int ,sync_items : List[Union[new_sync_item_db, new_sync_item_file]], session : Session):        
        if len(sync_items) == 0:
            return
        existing_items = []
        batch_size = 10000
        
        for i in range(0, len(sync_items), batch_size):
            batch = sync_items[i:i+batch_size]
            data_identifiers = [item.dataIdentifier for item in batch]
            
            stmt = select(SyncItemsSQL.dataIdentifier).where(SyncItemsSQL.sync_source_id == sync_source_id)
            stmt = stmt.where(SyncItemsSQL.dataIdentifier.in_(data_identifiers))

            result = session.execute(stmt).scalars().all()
            existing_items.extend(result)
        
        create_list = []
        update_list = []
        
        for s_item in sync_items:
            if isinstance(s_item, new_sync_item_db):
                s_item = new_sync_item_file(dataIdentifier = str(s_item.dataIdentifier), scopeIdentifier= s_item.scopeIdentifier, syncPriority = s_item.dataIdentifier)
            
            if s_item.dataIdentifier in existing_items:
                update_list.append({'dataIdentifier' : s_item.dataIdentifier, 'syncPriority' : s_item.syncPriority})
            else:
                create_list.append({"sync_source_id" : sync_source_id,
                            "dataIdentifier" : s_item.dataIdentifier,
                            "scopeIdentifier" : s_item.scopeIdentifier,
                            "datasetUUID" : uuid.uuid4(),
                            "syncPriority" : s_item.syncPriority,
                            })
        
        if create_list:
            session.execute(insert(SyncItemsSQL), create_list)
            session.commit()
        if update_list:
            # bulk updating with where not supported in sqlalchemy (yet)
            for item in update_list:
                stmt = (
                    update(SyncItemsSQL)
                    .where(SyncItemsSQL.sync_source_id == sync_source_id)
                    .where(SyncItemsSQL.dataIdentifier == item['dataIdentifier'])
                    .values(syncPriority = item['syncPriority'], synchronized = False, attempts = 0)
                )
                session.execute(stmt)
            session.commit()
        
    @staticmethod
    def read_sync_item(sync_source_id : int, offset :int, session : Session) -> 'sync_item | None':
        # get mappings
        scope_mappings, default_scope = dao_sync_items.__get_mappings(sync_source_id, session)
        select_stmt = (
            select(SyncItemsSQL)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
            .where(SyncItemsSQL.synchronized == False)
            .where(SyncItemsSQL.attempts == 0)
            .order_by(SyncItemsSQL.syncPriority.desc())
            .limit(1)
            .offset(offset)
        )
        if default_scope is None:
            select_stmt = select_stmt.where(SyncItemsSQL.scopeIdentifier.in_(scope_mappings.keys()))
        
        result = session.execute(select_stmt).scalar_one_or_none()
        
        # retry rules : 1st attempt after 1 hour, 2nd attempt after 1 day, 3rd attempt after 1 week, 4th attempt after 1 month
        if result is None:
            select_stmt = (
                select(SyncItemsSQL)
                .where(SyncItemsSQL.sync_source_id == sync_source_id)
                .where(SyncItemsSQL.synchronized == False)
                .where((SyncItemsSQL.attempts == 1) & (SyncItemsSQL.last_update < datetime.now() - timedelta(minutes=20)) |
                        (SyncItemsSQL.attempts == 2) & (SyncItemsSQL.last_update < datetime.now() - timedelta(hours=1)) |
                        (SyncItemsSQL.attempts == 3) & (SyncItemsSQL.last_update < datetime.now() - timedelta(hours=2)) |
                        (SyncItemsSQL.attempts == 4) & (SyncItemsSQL.last_update < datetime.now() - timedelta(hours=8)) |
                        (SyncItemsSQL.attempts >= 5) & (SyncItemsSQL.last_update < datetime.now() - timedelta(days=1)))
                .order_by(SyncItemsSQL.attempts.asc(), SyncItemsSQL.syncPriority.desc())
                .limit(1)
                .offset(offset)
            )
            if default_scope is None:
                select_stmt = select_stmt.where(SyncItemsSQL.scopeIdentifier.in_(scope_mappings.keys()))
            result = session.execute(select_stmt).scalar_one_or_none()
        
        if result is None:
            return None 
                
        scope_uuid = default_scope
        if result.scopeIdentifier in scope_mappings.keys():
            scope_uuid = scope_mappings[result.scopeIdentifier]
        
        creator = dao_sync_items.__get_creator(sync_source_id, session)
        
        return sync_item(dataIdentifier=str(result.dataIdentifier), datasetUUID=result.datasetUUID, scopeUUID=scope_uuid, creator=creator)
    
    @staticmethod
    def update_uuid(oldDatasetUUID : uuid.UUID, newDatasetUUID : uuid.UUID, session: Session) -> None:
        update_stmt = (
            update(SyncItemsSQL)
            .where(SyncItemsSQL.datasetUUID == oldDatasetUUID)
            .values(datasetUUID = newDatasetUUID)
        )

        session.execute(update_stmt)
        session.commit()
    
    @staticmethod
    def update_manifest(sync_source_id : int, dataIdentifier : str, last_mod_time : float, session: Session) -> None:
        update_stmt = (
            update(SyncItemsSQL)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
            .where(SyncItemsSQL.dataIdentifier == dataIdentifier)
            .values(syncPriority = last_mod_time)
        )
        
        session.execute(update_stmt)
        session.commit()
    
    @staticmethod
    def get_manifest(sync_source_id : int, session : Session) -> 'Dict[str, float]':
        stmt = (
            select(SyncItemsSQL.dataIdentifier, SyncItemsSQL.syncPriority)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
        )
        result = session.execute(stmt).all()
        
        manifest = {}
        for item in result:
            manifest[item.dataIdentifier] = item.syncPriority
        return manifest
    
    @staticmethod
    def is_max_priority(sync_source_id : int, s_item : sync_item, session : Session) -> bool:
        stmt = (
            select(SyncItemsSQL.dataIdentifier)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
            .order_by(SyncItemsSQL.syncPriority.desc())
            .limit(1)
        )
        result = session.execute(stmt).scalar_one()
        if result == s_item.dataIdentifier:
            return True
        return False

    @staticmethod
    def mark_successful_sync(sync_source_id : int, dataIdentifier : str, session: Session = None):
        update_stmt = (
            update(SyncItemsSQL)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
            .where(SyncItemsSQL.dataIdentifier == dataIdentifier)
            .values(synchronized = True)
        )
        
        session.execute(update_stmt)
        session.commit()
    
    @staticmethod
    def mark_failed_attempt(sync_source_id : int, dataIdentifier : str, session: Session = None):
        sync_source = dao_sync_sources.read_source_from_id(sync_source_id, session)
        sync_item = _get_sync_item(sync_source.id, dataIdentifier, session)
        sync_item.attempts += 1
        session.commit()
    
    @staticmethod
    def get_last_identifier(sync_source_id : int, session : Session) -> int:
        sync_source = dao_sync_sources.read_source_from_id(sync_source_id, session)
        stmt = select(func.max(SyncItemsSQL.syncPriority)).where(SyncItemsSQL.sync_source_id==sync_source.id)
        result = session.execute(stmt).scalar_one_or_none()
        if result is None :
            return None
        return result
    
    @staticmethod
    def count_items(sync_source_id : int, session : Session) -> int:
        stmt = (
            select(func.count(SyncItemsSQL.dataIdentifier))            
            .where(SyncItemsSQL.sync_source_id==sync_source_id)
        )
        return session.execute(stmt).scalar_one()

    @staticmethod
    def count_items_to_sync(sync_source_id : int, session : Session) -> int:
        scope_mappings, default_scope = dao_sync_items.__get_mappings(sync_source_id, session)
        
        stmt = (
            select(func.count(SyncItemsSQL.dataIdentifier))            
            .where(SyncItemsSQL.sync_source_id==sync_source_id)
            .where(SyncItemsSQL.synchronized == False)
            .where(SyncItemsSQL.attempts == 0)
        )
        if default_scope is None:
            stmt = stmt.where(SyncItemsSQL.scopeIdentifier.in_(scope_mappings.keys()))
        
        return session.execute(stmt).scalar_one()

    @staticmethod
    def count_items_failed(sync_source_id : int, session : Session) -> int:
        stmt = (
            select(func.count(SyncItemsSQL.dataIdentifier))            
            .where(SyncItemsSQL.sync_source_id==sync_source_id)
            .where(SyncItemsSQL.synchronized == False)
            .where(SyncItemsSQL.attempts > 0)
        )
        return session.execute(stmt).scalar_one()

    @staticmethod
    def count_items_synchronized(sync_source_id : int, session : Session) -> int:
        stmt = (
            select(func.count(SyncItemsSQL.dataIdentifier))            
            .where(SyncItemsSQL.sync_source_id==sync_source_id)
            .where(SyncItemsSQL.synchronized == True)
        )
        return session.execute(stmt).scalar_one()
    
    @staticmethod
    def count_items_not_in_scope(sync_source_id : int, session : Session) -> int:
        scope_mappings, default_scope = dao_sync_items.__get_mappings(sync_source_id, session)
        
        if default_scope is not None:
            return 0
        
        stmt = (
            select(func.count(SyncItemsSQL.dataIdentifier))            
            .where(SyncItemsSQL.sync_source_id==sync_source_id)
            .where(SyncItemsSQL.scopeIdentifier.not_in(scope_mappings.keys()))
        )
        return session.execute(stmt).scalar_one()

    @staticmethod
    def __get_mappings(sync_source_id : int, session : Session) -> 'Tuple[Dict[str, uuid.UUID], uuid.UUID | None]':
        '''
        Returns : 
        - dict with scopeIdentifier as key and scope_uuid as value
        - default_scope (if applicable, else None)
        '''
        sync_source = dao_sync_sources.read_source_from_id(sync_source_id, session)
        mappings = dao_sync_scope_mapping.get_mappings(sync_source_id, sync_source.auto_mapping, session)
        
        return mappings, sync_source.default_scope 
    
    @staticmethod
    def __get_creator(sync_source_id : int, session : Session) -> str:
        sync_source = dao_sync_sources.read_source_from_id(sync_source_id, session)
        return sync_source.creator
    
    @staticmethod
    def delete_sync_items(sync_source_id : int, session : Session) -> None:
        stmt = (
            delete(SyncItemsSQL)
            .where(SyncItemsSQL.sync_source_id == sync_source_id)
        )
        session.execute(stmt)
        session.commit()
    
def _get_sync_item(sync_source_id : int, dataIdentifier : str, session : Session) -> SyncItemsSQL:
    select_stmt = (
        select(SyncItemsSQL)
        .where(SyncItemsSQL.sync_source_id == sync_source_id)
        .where(SyncItemsSQL.dataIdentifier == dataIdentifier)
    )
    result = session.execute(select_stmt).scalar_one_or_none()
    
    if result is None:
        raise ValueError(f"Sync item {dataIdentifier} not found")
    return result