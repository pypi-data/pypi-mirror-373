from etiket_client.remote.endpoints.models.utility import convert_time_from_local_to_utc, convert_time_from_utc_to_local
from etiket_client.remote.endpoints.models.types import usernamestr, UserType

from pydantic import BaseModel, EmailStr, Field, field_validator, field_serializer
from typing import Optional

import datetime

# class UserBase(BaseModel):
#     username: usernamestr
#     firstname: str
#     lastname: str
#     email: Optional[EmailStr] = Field(default=None)
#     user_type: UserType = Field(default=UserType.standard_user)

#     disable_on: Optional[datetime.datetime] = Field(default=None)

# class UserRead(UserBase):  
#     created: datetime.datetime
#     modified: datetime.datetime
    
#     active: bool
    
#     @field_validator('created', mode='before')
#     @classmethod
#     def convert_created_time_utc_to_local(cls, created : datetime.datetime):
#         return convert_time_from_utc_to_local(created)
    
#     @field_validator('modified', mode='before')
#     @classmethod
#     def convert_modified_time_utc_to_local(cls, modified : datetime.datetime):
#         return convert_time_from_utc_to_local(modified)
    
#     @field_serializer('disable_on')
#     def collected_serialzer(self, disable_on: 'datetime.datetime | None', _info):
#         return convert_time_from_local_to_utc(disable_on)
