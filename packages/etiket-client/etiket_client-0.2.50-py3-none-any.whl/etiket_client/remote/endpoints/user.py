from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.user import UserRead, UserCreate, UserType, UserUpdate

from typing import List

api_version = "v3"

def create_user(data: UserCreate):
    client.post("/users", json_data=data.model_dump(mode="json"), api_version=api_version)
    
def read_users(name : str = None, email : UserType = None) -> List[UserRead]:
    response = client.get("/users", params={"name":name, "email": email}, api_version=api_version)
    return [UserRead.model_validate(user) for user in response]

def read_user(sub : str) -> UserRead:
    response = client.get(f"/users/{sub}", api_version=api_version)
    return UserRead.model_validate(response)

def update_user(sub : str, data: UserUpdate):
    client.patch(f"/users/{sub}", json_data=data.model_dump(mode="json"), api_version=api_version)
    
def delete_user(sub : str):
    client.delete(f"/users/{sub}", api_version=api_version)
    
def user_read_me() -> UserRead:
    response = client.get("/me", api_version=api_version)
    return UserRead.model_validate(response)

def user_update_me(password: str):
    client.patch("/me/password", params = {"password": password}, api_version=api_version)