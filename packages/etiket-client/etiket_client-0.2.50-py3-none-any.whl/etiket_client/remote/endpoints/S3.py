from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.S3 import (S3ResourceCreate, S3ResourceUpdate, 
            S3BucketRead, S3ResourceRead, S3ResourcePermission)
from etiket_client.remote.endpoints.models.S3_transfers import S3FileTransfer, S3TransferStatus
import typing, uuid


# Resources Endpoints

def s3_resource_read() -> typing.List[S3ResourceRead]:
    response = client.get("/S3/resource/read/")
    return [S3ResourceRead.model_validate(r) for r in response]

def s3_resource_create(s3Create: S3ResourceCreate) -> None:
    client.post("/S3/resource/create/", json_data=s3Create.model_dump(mode="json"))

def s3_resource_update(resource_uuid: uuid.UUID, s3Update: S3ResourceUpdate) -> None:
    client.patch("/S3/resource/update/", json_data=s3Update.model_dump(mode="json"), params={"resource_uuid": resource_uuid})

def s3_resource_grant_access(resource_uuid: uuid.UUID, target_user: str, permissions : S3ResourcePermission) -> None:
    client.post("/S3/resource/grant_access/", json_data=permissions.model_dump(),
                params={"resource_uuid": resource_uuid, "target_user": target_user})

def s3_resource_revoke_access(resource_uuid: uuid.UUID, target_user: str) -> None:
    client.delete("/S3/resource/revoke_access/", params={"resource_uuid": resource_uuid, "target_user": target_user})

# Buckets Endpoints

def s3_bucket_read() -> typing.List[S3BucketRead]:
    response = client.get("/S3/bucket/read/")
    return [S3BucketRead.model_validate(r) for r in response]

def s3_bucket_create(resource_uuid: uuid.UUID, bucket_name: str) -> None:
    client.post("/S3/bucket/create/", params={"resource_uuid": str(resource_uuid), "bucket_name": bucket_name})

def s3_bucket_add(resource_uuid: uuid.UUID, bucket_name: str) -> None:
    client.post("/S3/bucket/add_existing/", params={"resource_uuid": str(resource_uuid), "bucket_name": bucket_name})

def s3_bucket_grant_access(target_user: str, bucket_uuid: uuid.UUID) -> None:
    client.post("/S3/bucket/grant_access/", params={"target_user": target_user, "bucket_uuid": bucket_uuid})

def s3_bucket_revoke_access(target_user: str, bucket_uuid: uuid.UUID) -> None:
    client.delete("/S3/bucket/revoke_access/", params={"target_user": target_user, "bucket_uuid": bucket_uuid})

# transfer Endpoints

def s3_transfer_data(scope_uuid: uuid.UUID, bucket_uuid: uuid.UUID) -> None:
    client.post("/S3/transfer/create/", params={"scope_uuid": str(scope_uuid), "bucket_uuid": bucket_uuid})

def s3_transfer_status() -> typing.List[S3TransferStatus]:
    response = client.get("/S3/transfer/status-overview/")
    return [S3TransferStatus.model_validate(r) for r in response]

# admin Endpoints

# def s3_request_transfers(approximate_size) -> typing.List[S3FileTransfer]:
#     response = client.get("/admin/S3/request_transfers/", params={"approximate_size": approximate_size})
#     return [S3FileTransfer.model_validate(r) for r in response]

# def s3_confirm_transfers(file_transfers: typing.List[S3FileTransfer]) -> None:
#     client.post("/admin/S3/confirm_transfers/", json_data=[ft.model_dump(mode="json") for ft in file_transfers])
