from etiket_client.remote.endpoints.models.types import FileType, FileStatusRem

from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer, field_validator

import datetime, uuid

from etiket_client.remote.endpoints.models.utility import convert_time_from_local_to_utc, convert_time_from_utc_to_local

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
    ranking : int = Field(default=0)

class FileCreate(FileBase):
    ds_uuid : uuid.UUID
    immutable : bool = Field(default=True)
    
    @field_serializer('collected')
    def collected_serialzer(self, collected: datetime, _info):
        return convert_time_from_local_to_utc(collected)

class FileUpdate(BaseModel):
    ranking : int = Field(default=None)

class FileRead(FileBase):
    created: datetime.datetime
    modified: datetime.datetime
    immutable: bool
    
    md5_checksum : Optional[str]
    etag: Optional[str]
    status : FileStatusRem
    
    S3_link : Optional[str]
    S3_validity : Optional[float]
    
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

class FileSelect(BaseModel):
    uuid : uuid.UUID
    version_id : Optional[int] = Field(default=None)

class FileSignedUploadLinks(BaseModel):
    uuid : uuid.UUID
    version_id : int
    upload_id : str
    part_size : int
    presigned_urls : List[str]

class FileSignedUploadLink(BaseModel):
    uuid : uuid.UUID
    version_id : int
    url : str

class FileValidate(BaseModel):
    uuid : uuid.UUID
    version_id : int
    
    md5_checksum : str
    upload_id : str
    etags: List[str]

