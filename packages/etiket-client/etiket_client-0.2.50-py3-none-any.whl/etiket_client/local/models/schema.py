from etiket_client.remote.endpoints.models.schema_base import SchemaData, SchemaAttributes
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

import datetime, uuid

from etiket_client.local.models.utility import convert_time_from_utc_to_local

class SchemaBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid : uuid.UUID
    name : str
    description: str = Field(default='')
    schema_ : SchemaData = Field(alias='schema')

class SchemaCreate(SchemaBase):
    pass

class SchemaRead(SchemaBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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

class SchemaUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name : Optional[str] = Field(default=None)
    description : Optional[str] = Field(default=None)
    schema_ : Optional[SchemaData] = Field(alias='schema', default=None)

class SchemaDelete(BaseModel):
    uuid: uuid.UUID