from etiket_client.local.exceptions import UserAlreadyExistsException,\
    UserMailAlreadyRegisteredException, UserDoesNotExistException
from etiket_client.local.models.user import UserCreate, UserRead, UserType, UserReadWithScopes, UserUpdate
from etiket_client.local.model import Users

from etiket_client.local.dao.base import dao_base

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

class dao_user(dao_base):
    @staticmethod
    def create(userCreate : UserCreate, session : Session):
        if not dao_user._unique(Users, Users.username == userCreate.username, session):
            raise UserAlreadyExistsException(userCreate.username)
        if not dao_user._unique(Users, Users.email == userCreate.email, session):
            raise UserMailAlreadyRegisteredException(userCreate.email)
        dao_user._create(userCreate, Users, session)
        
    @staticmethod
    def read(username : str, read_scopes : bool, session : Session):
        user = _get_user_raw(username, session, lazy= not read_scopes)
        if read_scopes == True:
            return UserReadWithScopes.model_validate(user)
        return UserRead.model_validate(user)

    @staticmethod
    def read_all(session : Session, username_query : str = None,
                 user_type : UserType = None, offset : int = None, limit :int=None):
        return dao_user._read_all(Users, UserRead, session,
                                   string_query = {Users.username : username_query},
                                   is_equal_query ={Users.user_type : user_type},
                                   orderby = Users.username, offset=offset, limit=limit)
            
    @staticmethod
    def update(username : str, userUpdate : UserUpdate, session : Session):
        user = _get_user_raw(username, session)
        dao_user._update(user, userUpdate, session)
        
    @staticmethod
    def delete(username : str, session : Session):
        user = _get_user_raw(username, session)
        session.delete(user)
        session.commit()

def _get_user_raw(username: str, session:Session, lazy=True) -> Users:
    try:
        stmt = select(Users).where(Users.username == username)
        if lazy == False:
            stmt.options(selectinload(Users.scopes))
        return session.execute(stmt).scalars().one()
    except:
        raise UserDoesNotExistException(username)