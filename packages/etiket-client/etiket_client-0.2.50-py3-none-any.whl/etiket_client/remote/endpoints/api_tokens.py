import uuid, typing

from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.api_tokens import APITokenCreate, APITokenCreateResponse, APITokenRead

api_version = "v3"

def api_token_create(name):
    api_token_create_model = APITokenCreate(name=name)
    response = client.post("/api-tokens", json_data=api_token_create_model.model_dump(mode="json"), api_version=api_version)
    return APITokenCreateResponse.model_validate(response)

def api_token_list(user_name : typing.Optional[str] = None) -> typing.List[APITokenRead]:
    response = client.get("/api-tokens", params={"sub":user_name}, api_version=api_version)
    return [APITokenRead.model_validate(api_token) for api_token in response]

def api_token_delete(api_token_uid : uuid.UUID) -> None:
    client.delete(f"/api-tokens/{api_token_uid}", api_version=api_version)
