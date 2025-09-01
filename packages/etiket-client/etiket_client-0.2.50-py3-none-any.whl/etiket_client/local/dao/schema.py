from etiket_client.local.exceptions import SchemaDoesNotExistException, SchemaDoesAlreadyExistException
from etiket_client.local.models.schema import SchemaCreate, SchemaRead, SchemaUpdate
from etiket_client.local.model import Schemas

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from etiket_client.local.dao.base import dao_base
from typing import Optional

from uuid import UUID

class dao_schema(dao_base):
    @staticmethod
    def create(schemaCreate : SchemaCreate, session : Session):
        if not dao_schema._unique(Schemas, Schemas.uuid == schemaCreate.uuid, session):
            raise SchemaDoesAlreadyExistException(schemaCreate.uuid)
        return dao_schema._create(schemaCreate, Schemas, session)
    
    @staticmethod
    def read(schema_uuid : UUID, session : Session):
        return SchemaRead.model_validate(_get_schema_raw(schema_uuid, session))
    
    @staticmethod
    def read_all(session : Session, schemaname_query : Optional[str] = None, offset :  Optional[int] = None, limit : Optional[int]=None):
        return dao_schema._read_all(Schemas, SchemaRead, session,
                                   string_query = {Schemas.name : schemaname_query},
                                   is_equal_query ={},
                                   orderby = Schemas.name, offset=offset, limit=limit)

    @staticmethod
    def update(schema_uuid : UUID, schemaUpdate : SchemaUpdate, session : Session):
        shema = _get_schema_raw(schema_uuid, session)
        dao_schema._update(shema, schemaUpdate, session)

    @staticmethod
    def delete(schema_uuid : UUID, session : Session):
        schema = _get_schema_raw(schema_uuid, session)
        session.delete(schema)
        session.commit()
    
def _get_schema_raw(schema_uuid : UUID, session : Session, lazy = False):
    try:
        stmt = select(Schemas).where(Schemas.uuid == schema_uuid).options(selectinload(Schemas.scopes))
        if lazy == True:
            stmt = select(Schemas).where(Schemas.uuid == schema_uuid)
        return session.execute(stmt).scalars().one()
    except:
        raise SchemaDoesNotExistException