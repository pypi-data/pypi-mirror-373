from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.file import FileCreate, FileValidate,\
    FileRead, FileSelect, FileSignedUploadLinks, FileSignedUploadLink, FileUpdate

import typing, uuid

def file_create(fileCreate : FileCreate):
    client.post("/file/", json_data=fileCreate.model_dump(mode="json"))

def file_generate_presigned_upload_link_multi(file_uuid : uuid.UUID, version_id : int) -> FileSignedUploadLinks:
    params = {"file_uuid" : str(file_uuid), "version_id" : str(version_id)}
    data = client.get("/file/presigned_link/", params=params)
    return FileSignedUploadLinks.model_validate(data)

def file_generate_presigned_upload_link_single(file_uuid : uuid.UUID, version_id : int) -> FileSignedUploadLink:
    params = {"file_uuid" : str(file_uuid), "version_id" : str(version_id)}
    data = client.get("/file/presigned_link/single_part/", params=params)
    return FileSignedUploadLink.model_validate(data)

def file_read(fileSelect : FileSelect) -> typing.List[FileRead]:
    file_uuid = fileSelect.uuid
    version_id = fileSelect.version_id
    data = client.get("/file/read/", params={"uuid" : str(file_uuid), "version_id" : version_id})
    return [FileRead.model_validate(d) for d in data]

def file_update(file_uuid : uuid.UUID, version_id : int, fileUpdate : FileUpdate):
    client.patch("/file/", json_data=fileUpdate.model_dump(mode="json"),
                 params={"uuid" : str(file_uuid), "version_id" : version_id})
    
def file_read_by_name(dataset_uuid : uuid.UUID, name : str) -> typing.List[FileRead]:
    params = {"dataset_uuid" : str(dataset_uuid), "name" : name}
    data = client.get("/file/by_name/", params=params)
    return [FileRead.model_validate(d) for d in data]

def mark_immutable(file_uuid : uuid.UUID, version_id : int):
    client.post("/file/mark_immutable/",
                json_data={"file_uuid" : str(file_uuid), "version_id" : version_id})

def file_validate_upload_multi(fileValidate : FileValidate):
    client.post("/file/validate_upload/", json_data=fileValidate.model_dump(mode="json"))
    
def file_validate_upload_single(fileValidate : FileValidate):
    client.post("/file/validate_upload/single_part/", json_data=fileValidate.model_dump(mode="json"))
    
def file_abort_upload(fileValidate : FileValidate):
    client.post("/file/abort_upload/", json_data=fileValidate.model_dump(mode="json"))