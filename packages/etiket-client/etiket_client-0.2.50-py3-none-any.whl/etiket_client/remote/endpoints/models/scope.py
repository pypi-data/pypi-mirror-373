from etiket_client.remote.endpoints.models.utility import convert_time_from_utc_to_local
from etiket_client.remote.endpoints.models.types import scopestr

from uuid import UUID
from typing import Optional
from pydantic import AliasChoices, BaseModel, Field, field_validator

import datetime


class ScopeCreate(BaseModel):
    name : scopestr
    uuid : UUID = Field(serialization_alias="uid")
    description: str = Field(default = "")
    is_restricted : bool = Field(default=True)
    is_archived : bool = Field(default=False)
    bucket_uuid : UUID

class ScopeRead(BaseModel):
    name : scopestr
    uuid : UUID = Field(validation_alias=AliasChoices("uid", "uuid"))
    is_restricted : bool = Field(default=True)
    is_archived : bool = Field(validation_alias=AliasChoices("is_archived", "archived"))
    description: str
      
    created: datetime.datetime
    modified: datetime.datetime
    
    
    @field_validator('created', mode='before')
    @classmethod
    def convert_created_time_utc_to_local(cls, created : datetime.datetime):
        return convert_time_from_utc_to_local(created)
    
    @field_validator('modified', mode='before')
    @classmethod
    def convert_modified_time_utc_to_local(cls, modified : datetime.datetime):
        return convert_time_from_utc_to_local(modified)

class ScopeUpdate(BaseModel):
    name : Optional[scopestr] = Field(default = None)
    description: Optional[str] = Field(default = None)
    is_restricted : Optional[bool] = Field(default = None)
    is_archived : Optional[bool] = Field(default = None)