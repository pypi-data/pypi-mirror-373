from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.scope import ScopeRead, ScopeCreate, ScopeUpdate
from etiket_client.remote.endpoints.models.S3 import S3BucketInfo
import typing, uuid

api_version = "v3"

def scope_create(scopeCreate : ScopeCreate) -> None:
    client.post("/scopes", json_data=scopeCreate.model_dump(mode="json", by_alias=True), api_version=api_version)

def scope_update(scope_uuid : uuid.UUID, scopeUpdate : ScopeUpdate) -> None:
    client.patch(f"/scopes/{scope_uuid}", json_data=scopeUpdate.model_dump(mode="json"), api_version=api_version)

def scope_read(scope_uuid : uuid.UUID) -> ScopeRead:
    response = client.get(f"/scopes/{scope_uuid}", api_version=api_version)
    return ScopeRead.model_validate(response)

def scope_delete(scope_uuid : uuid.UUID) -> None:
    client.delete(f"/scopes/{scope_uuid}", api_version=api_version)

def scope_list(name_query : typing.Optional[str] = None) -> typing.List[ScopeRead]:
    response = client.get("/scopes", params={"name":name_query}, api_version=api_version)
    return [ScopeRead.model_validate(scope) for scope in response]

def scope_bucket(scope_uuid : uuid.UUID) -> S3BucketInfo:
    response = client.get(f"/scopes/{scope_uuid}/bucket", api_version=api_version)
    return S3BucketInfo.model_validate(response)