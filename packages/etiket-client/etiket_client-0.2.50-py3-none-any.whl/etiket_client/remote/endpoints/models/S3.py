import uuid

from typing import Optional
from pydantic import BaseModel, Field

from etiket_client.remote.endpoints.models.user import UserRead
from etiket_client.remote.endpoints.models.types import ObjectStoreType

class S3ResourcePermission(BaseModel):
    can_create_buckets : bool
    can_add_users : bool

class S3ResourceInfo(BaseModel):    
    name: str
    type : ObjectStoreType
    resource_uuid : uuid.UUID
    
    endpoint : str
    region : Optional[str] = Field(None)
    
class S3ResourceRead(BaseModel):
    name: str
    type : ObjectStoreType
    
    resource_uuid : uuid.UUID
    endpoint : str
    region : Optional[str] = Field(None)
    access_key : str
    
    created_by : UserRead
    
    public : Optional[bool] = Field(False)
    permissions: S3ResourcePermission

class S3BucketInfo(BaseModel):
    name : str
    bucket_uuid : uuid.UUID
    
    resource : S3ResourceInfo

class S3BucketRead(BaseModel):
    name : str
    bucket_uuid : uuid.UUID
    
    resource : S3ResourceRead
    
class S3ResourceCreate(BaseModel):
    name: str = Field(min_length=5, max_length=100)
    type : ObjectStoreType
    
    endpoint : str
    region : Optional[str] = Field(None)
    
    access_key : str
    secret_key : str
    
    public : Optional[bool] = Field(False)

class S3ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    access_key : Optional[str] = Field(None)
    secret_key : Optional[str] = Field(None)