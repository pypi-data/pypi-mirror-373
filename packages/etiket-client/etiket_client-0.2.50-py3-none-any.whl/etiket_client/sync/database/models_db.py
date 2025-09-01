from etiket_client.sync.database.types import SyncSourceTypes, SyncSourceStatus

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func, null, types
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.types import JSON

from datetime import datetime

import uuid, typing

class SyncBase(DeclarativeBase):
    pass

class SyncSourcesSQL(SyncBase):
    __tablename__ = "sync_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(unique=True)
    type : Mapped[SyncSourceTypes]
    status : Mapped[SyncSourceStatus]
    creator : Mapped[typing.Optional[str]]
    
    sync_config_module : Mapped[typing.Optional[str]]
    sync_config_name : Mapped[typing.Optional[str]]
    sync_class_module : Mapped[typing.Optional[str]]
    sync_class_name : Mapped[typing.Optional[str]]
    
    items_total : Mapped[int] 
    items_synchronized : Mapped[int]
    items_failed : Mapped[int]
    items_skipped : Mapped[int]
    last_update : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    config_data : Mapped[dict] = mapped_column(JSON)
    
    auto_mapping : Mapped[bool]
    default_scope : Mapped[typing.Optional[uuid.UUID]]
    

class SyncScopeMappingsSQL(SyncBase):
    __tablename__ = "sync_scope_mappings"
    __table_args__ = (UniqueConstraint('sync_source_id', 'scope_identifier', name='sync_source_did_constraint_scope_mapping'), )

    id: Mapped[int] = mapped_column(primary_key=True)
    sync_source_id : Mapped[int] = mapped_column(ForeignKey("sync_sources.id"))
    scope_identifier : Mapped[str]
    scope_uuid : Mapped[uuid.UUID]

class SyncItemsSQL(SyncBase):
    __tablename__  = "sync_items"
    
    __table_args__ = (UniqueConstraint('sync_source_id', 'dataIdentifier', name='sync_source_did_constraint_sync_items'),
                      Index('read_item_index', 'sync_source_id', 'scopeIdentifier', 'synchronized', 'dataIdentifier'),
                      Index('failed_upload_index', 'sync_source_id', 'attempts'),
                      Index('sync_upload_index', 'sync_source_id', 'attempts', 'synchronized'))

    id: Mapped[int] = mapped_column(primary_key=True)
    sync_source_id : Mapped[int] = mapped_column(ForeignKey("sync_sources.id"))
    dataIdentifier: Mapped[str] = mapped_column(index = True)
    scopeIdentifier : Mapped[typing.Optional[str]]
    datasetUUID  : Mapped[uuid.UUID] = mapped_column(unique=True)
    
    syncPriority : Mapped[float] = mapped_column(index = True)
    
    synchronized : Mapped[bool] = mapped_column(default = False)
    attempts : Mapped[int] = mapped_column(default = 0)
    
    last_update : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())