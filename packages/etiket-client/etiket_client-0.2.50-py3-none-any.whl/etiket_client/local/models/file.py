from etiket_client.remote.endpoints.models.types import FileType, FileStatusLocal

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator

import datetime, uuid

from etiket_client.local.models.utility import convert_time_from_local_to_utc, convert_time_from_utc_to_local

class FileBase(BaseModel):
    name : str
    filename : str
    uuid : uuid.UUID
    creator : str
    collected : datetime.datetime
    size : int
    type : FileType
    file_generator : Optional[str]
    version_id : int

    etag: Optional[str] = None
    status : FileStatusLocal
    ranking : int = Field(default=0)
    
    local_path : str
    ntimes_accessed : int = 0
    synchronized : bool = Field(default=False)

class FileCreate(FileBase):
    ds_uuid : uuid.UUID

class FileRead(FileBase):
    model_config = ConfigDict(from_attributes=True)
    
    created: datetime.datetime
    modified: datetime.datetime
    
    last_accessed : Optional[datetime.datetime]
    ntimes_accessed : int
    synchronized : bool
    
    @field_validator('collected', mode='before')
    @classmethod
    def convert_collected_time_utc_to_local(cls, collected : datetime.datetime):
        return convert_time_from_utc_to_local(collected)
    
    @field_validator('created', mode='before')
    @classmethod
    def convert_created_time_utc_to_local(cls, created : datetime.datetime):
        return convert_time_from_utc_to_local(created)
    
    @field_validator('modified', mode='before')
    @classmethod
    def convert_modified_time_utc_to_local(cls, modified : datetime.datetime):
        return convert_time_from_utc_to_local(modified)
    
class FileUpdate(BaseModel):
    file_generator : Optional[str] = None
    size : Optional[int] = None
    type : Optional[FileType] = None
    etag: Optional[str] = None
    status : Optional[FileStatusLocal] = None
    ranking : Optional[int] = None
    
    local_path : Optional[str] = None
    s3_link : Optional[str] = None
    s3_validity : Optional[datetime.datetime] = None
    last_accessed : Optional[datetime.datetime] = None
    ntimes_accessed : Optional[int] = None
    synchronized : bool = False
    
    @field_serializer('last_accessed')
    def last_accessed_serialzer(self, last_accessed: Optional[datetime.datetime], _info):
        return convert_time_from_local_to_utc(last_accessed)
    
    @field_serializer('s3_validity')
    def s3_validity_serialzer(self, s3_validity: Optional[datetime.datetime], _info):
        return convert_time_from_local_to_utc(s3_validity)

class FileSelect(BaseModel):
    uuid : uuid.UUID
    version_id : Optional[int] = Field(default=None) 

class FileSignedUploadLinks(BaseModel):
    upload_id : str
    part_size : int
    presigned_urls : List[str]
    
