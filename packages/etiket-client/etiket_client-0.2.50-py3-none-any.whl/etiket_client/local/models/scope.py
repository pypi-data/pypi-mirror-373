from etiket_client.local.models.schema import SchemaRead
from etiket_client.local.models.user_base import UserRead
from etiket_client.remote.endpoints.models.types import scopestr

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

import datetime, uuid

from etiket_client.local.models.utility import convert_time_from_utc_to_local


class ScopeBase(BaseModel):
    name : scopestr
    uuid : uuid.UUID
    description: str
    archived: bool

class ScopeCreate(ScopeBase):
    pass

class ScopeUpdate(BaseModel):
    name : Optional[scopestr] = None
    description: Optional[str] = None

class ScopeRead(ScopeBase):
    model_config = ConfigDict(from_attributes=True)
    
    created: datetime.datetime
    modified: datetime.datetime
    archived: bool
    
    schema_: Optional["SchemaRead"] = Field(alias="schema")

    @field_validator('created', mode='before')
    @classmethod
    def convert_created_time_utc_to_local(cls, created : datetime.datetime):
        return convert_time_from_utc_to_local(created)
    
    @field_validator('modified', mode='before')
    @classmethod
    def convert_modified_time_utc_to_local(cls, modified : datetime.datetime):
        return convert_time_from_utc_to_local(modified)

class ScopeReadWithUsers(ScopeRead):
    users : List["UserRead"]