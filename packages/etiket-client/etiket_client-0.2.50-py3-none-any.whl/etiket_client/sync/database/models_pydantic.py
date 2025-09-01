from etiket_client.sync.database.dao_sync_utils import updateDatasetUUID
from etiket_client.sync.database.types import SyncSourceStatus, SyncSourceTypes

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from typing import List, Optional, Tuple, Dict

import uuid, datetime, pathlib
    
class sync_source(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : Optional[int] = Field(default=None)
    name : str
    type : SyncSourceTypes
    status : SyncSourceStatus = Field(default=SyncSourceStatus.pending)
    creator : Optional[str] = Field(default=None)
    
    sync_config_module : Optional[str] = Field(default=None)
    sync_config_name : Optional[str] = Field(default=None)
    sync_class_module : Optional[str] = Field(default=None)
    sync_class_name : Optional[str] = Field(default=None)
    
    items_total : int = Field(default=0)
    items_synchronized : int = Field(default=0)
    items_failed : int = Field(default=0)
    items_skipped : int = Field(default=0)
    
    last_update : datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    config_data : dict
    
    auto_mapping : Optional[bool] = Field(default=False)
    default_scope : Optional[uuid.UUID] = Field(default=None)
    
    @field_serializer('config_data')
    def serialize_config_data(self, config_data: Dict, _info):
        formatted_config_data = {}
        for key, value in config_data.items():
            if isinstance(value, pathlib.Path):
                formatted_config_data[key] = str(value)
            else:
                formatted_config_data[key] = value
        return formatted_config_data 
    
    @field_validator('last_update', mode='before')
    @classmethod
    def convert_last_update_utc_to_local(cls, created : datetime.datetime):
        return created.replace(tzinfo=datetime.timezone.utc).astimezone()

class sync_source_update(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status : Optional[SyncSourceStatus] = Field(default=None)
    items_total : Optional[int] = Field(default=None)
    items_synchronized : Optional[int] = Field(default=None)
    items_failed : Optional[int] = Field(default=None)
    items_skipped : Optional[int] = Field(default=None)

class sync_scope_mapping(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sync_source_id : int
    scope_identifier : str 
    scope_uuid : uuid.UUID

class new_sync_item_db(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataIdentifier: int
    scopeIdentifier : Optional[str] = None
    
class new_sync_item_file(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataIdentifier: str
    scopeIdentifier : Optional[str] = None
    syncPriority : float

class sync_item(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    dataIdentifier: str
    datasetUUID : Optional[uuid.UUID]
    scopeUUID : Optional[uuid.UUID]
    creator : Optional[str]
    
    def updateDatasetUUID(self, newDatasetUUID : uuid.UUID):    
        updateDatasetUUID(self.datasetUUID, newDatasetUUID)
        self.datasetUUID = newDatasetUUID