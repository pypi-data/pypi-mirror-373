from etiket_client.remote.endpoints.models.types import usernamestr, UserType

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional

import datetime

from etiket_client.local.models.utility import convert_time_from_utc_to_local

class UserBase(BaseModel):
    username: usernamestr
    firstname: str
    lastname: str
    email: Optional[EmailStr] = Field(default=None)
    active: bool
    user_type: UserType = Field(default=UserType.standard_user)

    disable_on: Optional[datetime.datetime] = Field(default=None)

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
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
    
    @field_validator('disable_on', mode='before')
    @classmethod
    def convert_disable_on_time_utc_to_local(cls, disable_on : datetime.datetime):
        return convert_time_from_utc_to_local(disable_on)
    