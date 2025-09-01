from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint, func, TIMESTAMP, types, text, literal_column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from etiket_client.local.types import ProcTypes
from etiket_client.remote.endpoints.models.types import FileStatusLocal, FileType, UserType
from uuid import UUID
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class DATETIME_MS(types.TypeDecorator):
    """
    This type decorator is used to store datetime with microsecond precision in the database.
    The datetime is stored as a string in the format of "%Y-%m-%d %H:%M:%f"
    """
    impl = types.Unicode
    cache_ok = True

    def process_bind_param(self, value : datetime, dialect):
        value = value.astimezone(tz=timezone.utc).replace(tzinfo=None)
        return value.strftime("%Y-%m-%d %H:%M:%S.%f")

    def process_result_value(self, value : str, dialect):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid datetime format: {value}")

class ScopeUserLink(Base):
    __tablename__ = "scope_user_link"
    scope: Mapped[int] = mapped_column(ForeignKey("scopes.id"), primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True) 

class Scopes(Base):
    __tablename__ = "scopes"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(unique=True)
    created : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now())
    modified: Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now(), onupdate=func.current_timestamp())
    name : Mapped[str]
    description : Mapped[str]
    archived : Mapped[bool] = mapped_column(default=False)
    schema_id : Mapped[Optional[int]] = mapped_column(ForeignKey("schemas.id")) 
    
    schema : Mapped["Schemas"] = relationship(back_populates="scopes")
    users : Mapped[List["Users"]] = relationship(back_populates="scopes", secondary="scope_user_link")

class Schemas(Base):
    __tablename__ = "schemas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] =mapped_column(unique=True)
    name : Mapped[str]
    description : Mapped[str]
    created : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now())
    modified: Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now(), onupdate=func.current_timestamp())
    schema : Mapped[dict] = mapped_column(types.JSON)
    
    scopes : Mapped[List["Scopes"]] = relationship(back_populates="schema")

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    firstname: Mapped[str]
    lastname: Mapped[str]
    email: Mapped[Optional[str]]
    created : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now())
    modified: Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now(), onupdate=func.current_timestamp())
    active: Mapped[bool]
    disable_on: Mapped[Optional[datetime]]
    user_type: Mapped[UserType]
    
    api_token : Mapped[Optional[dict]] = mapped_column(types.JSON, nullable=True)
    
    scopes: Mapped[List["Scopes"]] = relationship(back_populates="users", secondary="scope_user_link")

class DsAttrLink(Base):
    __tablename__ = "ds_attr_link"
    
    dataset_id : Mapped[int] = mapped_column(ForeignKey("datasets.id"), primary_key=True) 
    dataset_attr_id : Mapped[int] = mapped_column(ForeignKey("dataset_attr.id"), primary_key=True) 
    
class Datasets(Base):
    __tablename__ = "datasets"
    __table_args__ = (UniqueConstraint('uuid', name = 'datasets_uuid_unique'),
                      UniqueConstraint('alt_uid', 'scope_id', name = 'datasets_alt_uid_scope_id_unique'),)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid : Mapped[UUID] = mapped_column(index=True)
    alt_uid : Mapped[Optional[str]] = mapped_column(index = True)
    collected: Mapped[datetime] = mapped_column(DATETIME_MS)
    created : Mapped[datetime] = mapped_column(DATETIME_MS, default=datetime.now)
    modified : Mapped[datetime] = mapped_column(DATETIME_MS, default=datetime.now, onupdate=datetime.now)
    name: Mapped[str]
    scope_id : Mapped[int] = mapped_column(ForeignKey("scopes.id"), nullable=False, index=True)
    creator : Mapped[str]
    description : Mapped[Optional[str]]
    notes : Mapped[Optional[str]]
    keywords : Mapped[List[str]] = mapped_column(types.JSON, nullable=False)
    search_helper : Mapped[str]
    ranking : Mapped[int]
    
    synchronized : Mapped[bool]

    scope : Mapped["Scopes"] = relationship(innerjoin=True)
    files : Mapped[List["Files"]] = relationship(cascade="all, delete")
    attributes  : Mapped[List["DatasetAttr"]] = relationship(secondary="ds_attr_link", back_populates="datasets")

class DatasetFTS(Base):
    __tablename__ = "datasets_fts"
    
    rowid: Mapped[int] = mapped_column(primary_key=True)
    search_helper : Mapped[str]
    
class DatasetAttr(Base):
    __tablename__ = "dataset_attr"
    __table_args__ = (UniqueConstraint("key", "value", "scope_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key : Mapped[str]
    value : Mapped[str]
    scope_id : Mapped[int] = mapped_column(ForeignKey("scopes.id"), index=True)
    
    datasets : Mapped[List[Datasets]] = relationship(secondary="ds_attr_link", back_populates="attributes")

class Files(Base):
    __tablename__ = "files"
    __table_args__ = (UniqueConstraint("uuid", "version_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    filename : Mapped[str]
    file_generator : Mapped[Optional[str]]

    uuid : Mapped[UUID]
    version_id : Mapped[int]
    creator : Mapped[str]
    type : Mapped[FileType]
    
    scope_id : Mapped[int] = mapped_column(ForeignKey("scopes.id"))
    dataset_id : Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    
    collected: Mapped[datetime] = mapped_column(DATETIME_MS)
    created : Mapped[datetime] = mapped_column(DATETIME_MS, default=datetime.now)
    modified : Mapped[datetime] = mapped_column(DATETIME_MS, default=datetime.now, onupdate=datetime.now)
    
    etag : Mapped[Optional[str]] = mapped_column(default=None)
    size :  Mapped[int]
    status : Mapped[FileStatusLocal]
    ranking : Mapped[int]

    local_path : Mapped[Optional[str]]
    S3_link : Mapped[Optional[str]]
    S3_validity : Mapped[Optional[datetime]]
    last_accessed : Mapped[Optional[datetime]]
    ntimes_accessed : Mapped[int] = 0 # todo implement later...
    synchronized : Mapped[bool] = mapped_column(index=True)
    
class FileDeleteQueue(Base):
    __tablename__ = "file_delete_queue"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    local_path : Mapped[str]
    delete_after : Mapped[datetime] = mapped_column(types.DateTime(timezone=True))
    
class QHarborAppRegister(Base):
    __tablename__ = "qharbor_app_register"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    type : Mapped[ProcTypes]
    version : Mapped[str]
    
    location : Mapped[str]
    last_session : Mapped[datetime] = mapped_column(types.DateTime(timezone=True), default=func.now())