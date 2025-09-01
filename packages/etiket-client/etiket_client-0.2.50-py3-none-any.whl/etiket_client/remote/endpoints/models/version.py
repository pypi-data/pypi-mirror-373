import datetime, re

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from etiket_client.remote.endpoints.models.types import SoftwareType

class VersionCreate(BaseModel):
    type : SoftwareType
    version : str
    version_notes : str
    version_url : str
    needs_update : bool = Field(default=False)
    
    @field_validator('version', mode='before')
    @classmethod
    def check_semantic_version_number(cls, version):
        if not re.match(r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$', version):
            raise ValueError("Version number is not a semantic version number. See https://semver.org/ for more information.")
        return version

class VersionRead(BaseModel):
    id : int
    type : SoftwareType
    
    version : str
    version_release_date : datetime.datetime  
    version_notes : str
    version_url : str
    
    needs_update : bool = Field(default=False)

class VersionUpdate(BaseModel):
    version_notes : Optional[str] = Field(default=None)
    version_url : Optional[str] = Field(default=None)
    needs_update : Optional[bool] = Field(default=None)

class ReleaseCreate(BaseModel):
    beta_release : bool
    
    min_version_etiket_id : int
    min_version_dataQruiser_id : int
    min_version_qdrive_id : int

class ReleaseRead(BaseModel):
    release_id : int
    release_date : datetime.datetime
    
    beta_release : bool
    
    etiket_version : VersionRead
    dataQruiser_version : VersionRead
    qdrive_version : VersionRead
    
    min_etiket_version : VersionRead
    min_dataQruiser_version : VersionRead
    min_qdrive_version : VersionRead
    
class currentVersionsNumbers(BaseModel):
    etiket_version : str
    dataQruiser_version : Optional[str]
    qdrive_version : str