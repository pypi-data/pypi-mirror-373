from typing import Optional
from pydantic import BaseModel, Field, AwareDatetime

class APITokenCreate(BaseModel):
    name: str = Field(min_length=3)

class APITokenCreateResponse(BaseModel):    
    uid : str
    name: str
    api_token: str
    owner: str

class APITokenRead(BaseModel):    
    uid: str
    name: str
    owner: str
    last_validated : Optional[AwareDatetime]

    