from dataclasses import asdict
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from etiket_client.local.exceptions import UserDoesNotExistException
from etiket_client.local.models.api_tokens import APIKeyInfo
from etiket_client.local.model import Users


class dao_api_token:
    @staticmethod
    def create(user_sub: str, api_key_info: APIKeyInfo, session: Session) -> None:
        """
        Creates or updates the API token for a user.
        
        Args:
            user_sub (str): The unique username of the user.
            api_key_info (APIKeyInfo): The API token info to store.
            session (Session): SQLAlchemy session.
        
        Raises:
            UserDoesNotExistException: When a user with the given username is not found.
        """
        stmt = select(Users).filter_by(username=user_sub)
        user : Optional[Users] = session.scalars(stmt).one_or_none()
        if user is None:
            raise UserDoesNotExistException(f"User {user_sub} does not exist.")
        # Update the user's api_token field with the dictionary representation of APIKeyInfo.
        user.api_token = asdict(api_key_info)
        session.add(user)
        session.commit()

    @staticmethod
    def read(user_sub: str, session: Session) -> Optional[APIKeyInfo]:
        """
        Reads and returns the API token info for a user.
        
        Args:
            user_sub (str): The unique username of the user.
            session (Session): SQLAlchemy session.
            
        Returns:
            APIKeyInfo: The API token information or None if not found.
            
        """
        stmt = select(Users).filter_by(username=user_sub)
        user : Optional[Users] = session.execute(stmt).scalar_one_or_none()
        if user is None or not user.api_token:
            return None
        # Recreate APIKeyInfo from the stored dictionary.
        token_dict = user.api_token
        return APIKeyInfo(
            uid=token_dict.get("uid"),
            name=token_dict.get("name"),
            api_token=token_dict.get("api_token"),
            server_url=token_dict.get("server_url")
        )

    @staticmethod
    def delete(user_sub: str, session: Session) -> None:
        """
        Deletes the API token for a given user by setting it to None.
        
        Args:
            user_sub (str): The unique username of the user.
            session (Session): SQLAlchemy session.
            
        Raises:
            UserDoesNotExistException: When a user with the given username is not found.
        """
        stmt = select(Users).filter_by(username=user_sub)
        user : Optional[Users] = session.scalars(stmt).one_or_none()
        if user is None:
            raise UserDoesNotExistException(f"User {user_sub} does not exist.")
        user.api_token = None
        session.add(user)
        session.commit()