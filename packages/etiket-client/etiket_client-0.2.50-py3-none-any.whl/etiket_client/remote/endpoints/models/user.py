from etiket_client.remote.endpoints.models.utility import convert_time_from_local_to_utc
from etiket_client.remote.endpoints.models.types import UserType, Role

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_serializer, SecretStr, AwareDatetime

import datetime


class UserBase(BaseModel):
    """Base class for user models."""
    firstname: str
    lastname: str
    email: Optional[EmailStr]
    role: Role

class UserCreate(UserBase):
    """Model for creating a new user."""
    sub: str = Field(serialization_alias='username')
    password: str = Field(min_length=6)
    email: EmailStr

class UserUpdate(BaseModel):
    """Model for updating user data."""    
    password: Optional[str] = Field(default=None, min_length=6)
    role: Optional[Role] = Field(default=None)
    is_enabled: Optional[bool] = Field(default=None, serialization_alias='active')

class UserRead(UserBase):
    """Model for reading user data."""    
    sub : str
    is_enabled: bool
    
    created : AwareDatetime
    modified : AwareDatetime
    
class UserInfo(BaseModel):
    '''
    Class the return user information to the client, formatted according to the openid standard.
    '''
    sub : str
    email: Optional[str] = Field(default=None)
    given_name : str
    family_name : str

# class UserCreate(UserBase):
#     password : str
    
#     @field_serializer('disable_on')
#     def collected_serialzer(self, disable_on: datetime, _info):
#         return convert_time_from_local_to_utc(disable_on)
        
# class UserReadWithScopes(UserRead):
#     scopes : List[ScopeRead]

# class UserUpdateMe(BaseModel):
#     firstname: Optional[str] = Field(default=None)
#     lastname: Optional[str] = Field(default=None)
#     email: Optional[EmailStr] = Field(default=None)

# class UserPasswordUpdate(BaseModel):
#     username : str
#     password : str
#     new_password : passwordstr

# class UserUpdate(UserUpdateMe):
#     password : Optional[str] = Field(default=None)
#     disable_on: Optional[datetime.datetime] = Field(default=None)    
#     user_type: Optional[UserType] = Field(default=None)
#     active : Optional[bool] = Field(default=None)
    
#     @field_serializer('disable_on')
#     def collected_serialzer(self, disable_on: datetime, _info):
#         return convert_time_from_local_to_utc(disable_on)
    
class UserLogin(BaseModel):
    username : str
    password : str