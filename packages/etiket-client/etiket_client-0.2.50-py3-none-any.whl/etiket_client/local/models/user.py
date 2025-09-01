import datetime

from etiket_client.remote.endpoints.models.types import UserType

from etiket_client.local.models.user_base import UserBase, UserRead
from etiket_client.local.models.scope import ScopeRead

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_serializer

from etiket_client.local.models.utility import convert_time_from_local_to_utc

class UserCreate(UserBase):
    pass

    @field_serializer('disable_on')
    def collected_serialzer(self, collected: datetime, _info):
        return convert_time_from_local_to_utc(collected)
        
class UserReadWithScopes(UserRead):    
    scopes : List[ScopeRead]

class UserUpdate(BaseModel):
    firstname: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    user_type: Optional[UserType] = Field(default=None)  
    active : Optional[bool] = Field(default=None)
    disable_on: Optional[datetime.datetime] = Field(default=None)
    
    api_token : Optional[dict] = Field(default=None)

    @field_serializer('disable_on')
    def collected_serialzer(self, collected: datetime, _info):
        return convert_time_from_local_to_utc(collected)
    
    @field_serializer('api_token')
    def serialize_api_token(self, api_token, _info):
        raise "!!! TODO !!!"
        return api_token.asdict()