from typing import List, Optional

from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.types import SoftwareType
from etiket_client.remote.endpoints.models.version import VersionCreate, VersionRead, VersionUpdate, ReleaseCreate, ReleaseRead

def get_web_api_version() -> str:
    response = client.get("/version/API/")
    return response

def get_latest_version(software_type : SoftwareType, allow_beta : bool = None) -> VersionRead:
    params = {"software_type": software_type, "allow_beta": allow_beta}
    response = client.get("/version/latest/", params=params)
    return VersionRead.model_validate(response)

def get_versions(software_type : SoftwareType, min_version : Optional[str] = None,  allow_beta : bool = False) -> List[VersionRead]:
    params = {"software_type": software_type, "min_version": min_version, "allow_beta": allow_beta}
    response = client.get("/version/", params=params)
    return [VersionRead.model_validate(version) for version in response]

def get_latest_release(allow_beta : bool = False) -> ReleaseRead:
    params = {"allow_beta": allow_beta}
    response = client.get("/release/latest/", params=params)
    return ReleaseRead.model_validate(response)

def get_release_from_version(software_type : SoftwareType, version: str, allow_beta : bool = False) -> ReleaseRead:
    params = {"version": version, "software_type": software_type, "allow_beta": allow_beta}
    response = client.get("/release/get_release_from_version/", params=params)
    return ReleaseRead.model_validate(response)

def create_version(version_create: VersionCreate) -> None:
    client.post("/version/create/", json_data=version_create.model_dump(mode="json"))

def update_version(version_id: int, version_update: VersionUpdate) -> None:
    params = {"version_id": version_id}
    client.patch("/version/update/", json_data=version_update.model_dump(mode="json", exclude_none=True), params=params)

def create_release(release_create: ReleaseCreate) -> None:
    client.post("/release/create/", json_data=release_create.model_dump(mode="json"))
