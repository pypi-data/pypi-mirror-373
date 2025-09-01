from etiket_client.settings.user_settings import user_settings
from etiket_client.exceptions import SyncSourceNotFoundException
from etiket_client.sync.database.models_db import SyncSourcesSQL
from etiket_client.sync.database.models_pydantic import sync_source, sync_source_update

from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete

from typing import List


class dao_sync_sources:
    @staticmethod
    def add_new_source(sync_source : sync_source, session : Session):
        sync_source.creator = user_settings.user_sub
        insert_stmt = insert(SyncSourcesSQL).values(**sync_source.model_dump())
        session.execute(insert_stmt)
        session.commit()
    
    @staticmethod
    def read_sources(session : Session) -> List[sync_source]:
        stmt = select(SyncSourcesSQL)
        result = session.execute(stmt).scalars().all()

        return [sync_source.model_validate(i) for i in result]
    
    @staticmethod
    def read(sync_source_name : str, session : Session) -> sync_source:
        stmt = select(SyncSourcesSQL).where(SyncSourcesSQL.name == sync_source_name)
        result = session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise SyncSourceNotFoundException(f"Sync source {sync_source_name} not found")
        return sync_source.model_validate(result)
    
    @staticmethod
    def read_source_from_id(sync_source_id : int, session : Session) -> sync_source:
        stmt = select(SyncSourcesSQL).where(SyncSourcesSQL.id == sync_source_id)
        result = session.execute(stmt).scalar_one()
        return sync_source.model_validate(result)
    
    @staticmethod
    def update_status(sync_source_id : int, ss_update : sync_source_update, session : Session):
        stmt = (
            update(SyncSourcesSQL)
            .where(SyncSourcesSQL.id == sync_source_id)
            .values(**ss_update.model_dump(exclude_none=True))
        )
        session.execute(stmt)
        session.commit()
    
    @staticmethod
    def delete_source(sync_source_id : int, session : Session):
        stmt = (
            delete(SyncSourcesSQL)
            .where(SyncSourcesSQL.id == sync_source_id)
        )
        session.execute(stmt)
        session.commit()