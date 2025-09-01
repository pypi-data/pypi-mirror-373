from etiket_client.local.models.file import FileRead
from etiket_client.local.models.scope import ScopeRead

from etiket_client.local.models.utility import convert_time_from_local_to_utc, convert_time_from_utc_to_local
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator, field_serializer
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
    
    synchronized : bool = Field(default=False)

class DatasetCreate(DatasetBase):
    scope_uuid : uuid.UUID
    attributes : Optional[Dict[str, str]] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def same_identifier_check(self):
        if self.alt_uid != str(self.uuid):
            return self
        raise ValueError("The uuid and alternative uid need to be different.")
    
class DatasetRead(DatasetBase):
    model_config = ConfigDict(from_attributes=True)
    
    created : datetime.datetime
    modified : datetime.datetime

    scope : ScopeRead
    attributes : Optional[Dict[str, str]] = Field(default={})
    files : Optional[List["FileRead"]]
    
    @field_validator('attributes', mode='before')
    @classmethod
    def convert_orm_type_to_dict(cls, attributes):
        out = {}
        for attr in attributes:
            out[attr.key]= attr.value
        return out
    
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
    synchronized : Optional[bool] = Field(default=None)
    
    attributes : Optional[Dict[str, str]] = Field(default=None)

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
    
    @field_validator('start_date', mode='before')
    @classmethod
    def convert_start_time_local_to_utc(cls, start_date : datetime.datetime):
        return convert_time_from_local_to_utc(start_date)
    
    @field_validator('end_date', mode='before')
    @classmethod
    def convert_end_time_local_to_utc(cls, end_date : datetime.datetime):
        return convert_time_from_local_to_utc(end_date)