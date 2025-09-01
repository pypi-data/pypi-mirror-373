from etiket_client.local.exceptions import MultipleScopesWithSameNameException, ScopeDoesAlreadyExistException,\
    CannotDeleteAScopeWithDatasetsException, MemberHasNoBusinessInThisScopeException,\
    UserAlreadyNotPartOfScopeException, UserAlreadyPartOfScopeException, \
    ScopeDoesNotExistException

from etiket_client.local.models.scope import ScopeUpdate, ScopeCreate, ScopeReadWithUsers
from etiket_client.local.model import Scopes, Datasets, Users

from etiket_client.local.dao.schema import _get_schema_raw
from etiket_client.local.dao.user import _get_user_raw, UserType
from etiket_client.local.dao.base import dao_base
from etiket_client.remote.endpoints.models.types import UserType

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from typing import Optional, List
from uuid import UUID

class dao_scope(dao_base):
    @staticmethod
    def create(scopeCreate : ScopeCreate, session: Session):
        if not dao_scope._unique(Scopes, Scopes.uuid == scopeCreate.uuid, session):
            raise ScopeDoesAlreadyExistException(scopeCreate.uuid)
        return dao_scope._create(scopeCreate, Scopes, session)

    @staticmethod
    def read(scope_uuid : UUID, session : Session) -> ScopeReadWithUsers:
        scope = _get_scope_raw(scope_uuid=scope_uuid, session=session, lazy=False)
        return ScopeReadWithUsers.model_validate(scope)
    
    @staticmethod
    def read_all(name_query : Optional[str] = None,  archived : Optional[bool] = None,
                 username : Optional[str]=None, offset : Optional[int] = None, 
                 limit : Optional[int] = None, session : Session = None):
        # TODO add better permission handling
        stmt = dao_scope._query(Scopes, string_query = {Scopes.name : name_query},
                                            is_equal_query ={Scopes.archived : archived},
                                            orderby = Scopes.name, offset=offset, limit=limit)
        if username:
            stmt = stmt.join(Users.scopes).where(Users.username==username)
        stmt = stmt.options(selectinload(Scopes.users))

        result = session.execute(stmt).scalars().all()
        return [ScopeReadWithUsers.model_validate(res) for res in result]
    
    @staticmethod
    def read_by_name(name : str, session : Session) -> ScopeReadWithUsers:
        stmt = select(Scopes).where(Scopes.name == name)
        stmt = stmt.options(selectinload(Scopes.users))
        
        results = session.execute(stmt).scalars().all()
        if len(results) == 0:
            raise ScopeDoesNotExistException(name)
        if len(results) > 1:
            raise MultipleScopesWithSameNameException([scope.name for scope in results])
        
        return ScopeReadWithUsers.model_validate(results[0])

    @staticmethod
    def update(scope_uuid : UUID, scopeUpdate : ScopeUpdate, session : Session):
        scope = _get_scope_raw(scope_uuid, session)
        return dao_scope._update(scope, scopeUpdate, session)

    @staticmethod
    def delete(scope_uuid : UUID, session : Session):
        scope = _get_scope_raw(scope_uuid, session)
        
        if _n_datasets_in_scope(scope, session) != 0:
            raise CannotDeleteAScopeWithDatasetsException(scope.name)
        
        session.delete(scope)
        session.commit()
    
    @staticmethod
    def user_in_scope(scope_uuid : UUID, username : str, session : Session):
        stmt = select(func.count(Scopes.id)).where(Scopes.uuid==scope_uuid)
        stmt = stmt.join(Users.scopes).where(Users.username==username)     
        if session.execute(stmt).scalar_one() == 0:
            return False
        return True
        
    @staticmethod
    def assign_user(scope_uuid : UUID, username : str, session : Session):
        user  = _get_user_raw(username, session)
        scope = _get_scope_raw(scope_uuid, session, lazy=False)

        if user in scope.users:
            raise UserAlreadyPartOfScopeException(username, scope.name)
        
        scope.users.append(user)
        session.commit()
    
    @staticmethod
    def remove_user(scope_uuid : UUID, username : str, session : Session):
        scope = _get_scope_raw(scope_uuid, session, lazy=False)
        user  = _get_user_raw(username, session)

        if user not in scope.users:
            raise UserAlreadyNotPartOfScopeException(scope.uuid)
        
        scope.users.remove(user)
        session.commit()
    
    @staticmethod
    def assign_schema(scope_uuid : UUID, schema_uuid : UUID, session : Session):
        schema  = _get_schema_raw(schema_uuid, session)
        scope = _get_scope_raw(scope_uuid, session, lazy=False)        
        scope.schema = schema
        session.commit()
        
    @staticmethod
    def remove_schema(scope_uuid : UUID, session : Session):
        scope = _get_scope_raw(scope_uuid, session, lazy=False)
        scope.schema = None
        session.commit()
    
    @staticmethod  
    def validate_scope_UUID(scope_uuid : UUID, username : str, user_type:UserType, session:Session):
        scope_uuids_user = _get_user_scope_UUIDs(username, user_type, session)
        if scope_uuid not in scope_uuids_user:
            raise MemberHasNoBusinessInThisScopeException(scope_uuid)
        
        return scope_uuid
    
    @staticmethod
    def validate_scope_UUIDs(scope_uuids : List[UUID], username : str, user_type:UserType, session:Session):
        scope_uuids_user = _get_user_scope_UUIDs(username, user_type, session)
            
        if scope_uuids:
            for scope_uuid in scope_uuids:
                if scope_uuid not in scope_uuids_user:
                    raise MemberHasNoBusinessInThisScopeException(scope_uuid)
            return scope_uuids
        else:
            return scope_uuids_user

def _get_user_scope_UUIDs(username : str, user_type:UserType, session:Session):
    scopes = dao_scope.read_all(username=username, session=session)
    return [scope.uuid for scope in scopes]

def _get_user_scope_ids(username : str, session:Session):
    stmt = select(Scopes.id).join(Users.scopes).where(Users.username==username)
    return session.execute(stmt).scalars().all()

def _get_scope_raw(scope_uuid : UUID, session:Session, lazy=True) -> Scopes:
    try:
        stmt = select(Scopes).where(Scopes.uuid == scope_uuid)
        if lazy == False:
            stmt.options(selectinload(Scopes.users))
        return session.execute(stmt).scalars().one()
    except:
        raise ScopeDoesNotExistException(scope_uuid)

def _n_datasets_in_scope(scope : Scopes, session:Session):
    stmt = select(func.count(Datasets.id)).where(Datasets.scope_id == scope.id)
    return session.execute(stmt).scalar_one()