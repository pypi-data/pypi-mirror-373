
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from etiket_client.local.types import ProcTypes

class AppRegisterCreate(BaseModel):
    type: ProcTypes
    version: str
    
    location : str

class AppRegisterUpdate(BaseModel):
    last_session : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppRegisterRead(BaseModel):
    id: int
    type: ProcTypes
    version: str
    
    location : str
    last_session : datetime