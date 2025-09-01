from etiket_client.remote.endpoints.models.utility import convert_time_from_local_to_utc, convert_time_from_utc_to_local
from etiket_client.remote.endpoints.models.file import FileRead
from etiket_client.remote.endpoints.models.scope import ScopeRead

from pydantic import BaseModel, Field, model_validator, field_validator, field_serializer
from typing import Optional, List, Dict

import datetime, uuid


class DatasetBase(BaseModel):
    uuid : uuid.UUID
    alt_uid : Optional[str] = Field(default=None)
    collected : datetime.datetime
    name: str
    creator : str
    description : Optional[str] = Field(default=None)
    notes : Optional[str] = Field(default=None)
    keywords : List[str]
    ranking : int

class DatasetCreate(DatasetBase):
    scope_uuid : uuid.UUID
    attributes : Optional[Dict[str, str]] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def same_identifier_check(self):
        if self.alt_uid != str(self.uuid):
            return self
        raise ValueError("The uuid and alternative uid need to be different.")

    @field_serializer('collected')
    def collected_serialzer(self, collected: datetime, _info):
        return convert_time_from_local_to_utc(collected)

class DatasetRead(DatasetBase):
    created : datetime.datetime
    modified : datetime.datetime

    scope : ScopeRead
    attributes : Optional[Dict[str, str]] = Field(default={})
    files : List["FileRead"]
        
    @field_validator('created', mode='before')
    @classmethod
    def convert_created_time_utc_to_local(cls, created : datetime.datetime):
        return convert_time_from_utc_to_local(created)
    
    @field_validator('modified', mode='before')
    @classmethod
    def convert_modified_time_utc_to_local(cls, modified : datetime.datetime):
        return convert_time_from_utc_to_local(modified)

    @field_validator('collected', mode='before')
    @classmethod
    def convert_collected_time_utc_to_local(cls, collected : datetime.datetime):
        return convert_time_from_utc_to_local(collected)
    
class DatasetUpdate(BaseModel):
    alt_uid : Optional[str] = Field(default=None)
    name:  Optional[str] = Field(default=None)
    description : Optional[str] = Field(default=None)
    notes : Optional[str] = Field(default=None)
    keywords :  Optional[List[str]] = Field(default=None)
    ranking :  Optional[int] = Field(default=None)
    
    attributes : Optional[Dict[str, str]] = Field(default=None)

class DatasetDelete(BaseModel):
    uuid : uuid.UUID
    
class DatasetSelection(BaseModel):
    scope_uuids : Optional[List[uuid.UUID]] = Field(default=None)
    attributes : Optional[Dict[str, List[str]]] = Field(default={})
    
class DatasetSearch(DatasetSelection):
    scope_uuids : Optional[List[uuid.UUID]] = Field(default=None)
    attributes : Optional[Dict[str, List[str]]] = Field(default={})
    search_query : Optional[str] = Field(default=None)
    ranking : Optional[int] = Field(default=0)
    
    has_notes : Optional[bool] = Field(default=False)
    
    start_date : Optional[datetime.datetime] = Field(default=None)
    end_date : Optional[datetime.datetime] = Field(default=None)
    time_zone : Optional[str] = Field(default=None)
    
    @field_serializer('start_date')
    def start_time_serializer(self, start_date: Optional[datetime.datetime], _info):
        if start_date is None:
            return None
        return convert_time_from_local_to_utc(start_date)
    
    @field_serializer('end_date')
    def end_time_serializer(self, end_date: Optional[datetime.datetime], _info):
        if end_date is None:
            return None
        return convert_time_from_local_to_utc(end_date)