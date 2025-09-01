from etiket_client.remote.endpoints.models.utility import convert_time_from_utc_to_local
from etiket_client.exceptions import SchemaNotValidException
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
import datetime, uuid, re

class SchemaData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    attributes : List['SchemaAttributes']

class SchemaAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    attribute_name : str
    is_required : bool
    default_values : List[str] = Field(default_factory=lambda:[])
    regex_validation : Optional[str] = Field(default=None)

    @field_validator('regex_validation')
    @classmethod
    def is_valid_regex(cls, v: str) -> str:
        if v is not None:
            try:
                re.compile(v)
            except re.error:
                raise SchemaNotValidException(f'the regex "{v}" is invalid.')
        return v

class SchemaBase(BaseModel):
    uuid : uuid.UUID
    name : str
    description: str = Field(default='')
    schema_ : Optional[SchemaData] = Field(alias='schema', default_factory=lambda:SchemaData(attributes=[]))

class SchemaRead(SchemaBase):
    model_config = ConfigDict(populate_by_name=True)
    
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