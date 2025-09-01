import datetime

from pydantic import BaseModel, Field
from typing import Optional

from etiket_client.remote.endpoints.models.user import UserRead
from etiket_client.remote.endpoints.models.types import UserLogStatus

class UserLogUploadInfo(BaseModel):
    key : str
    url : str

class UserLogRead(BaseModel):    
    key : str
    reason : Optional[str] = Field(default=None)
    status : UserLogStatus
    
    user : UserRead
    
    url : Optional[str] = Field(default=None)
    url_expiration_timestamp : Optional[float] = Field(default=None)
    
    created : datetime.datetime