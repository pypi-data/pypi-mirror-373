from etiket_client.exceptions import RequestFailedException
from etiket_client.local.exceptions import DatasetNotFoundException, MultipleDatasetFoundException
from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.dataset import \
    DatasetCreate, DatasetUpdate, DatasetRead, \
    DatasetSearch, DatasetSelection

import uuid, typing

def dataset_create(datasetCreate : DatasetCreate) -> None:
    client.post("/dataset/", json_data=datasetCreate.model_dump(mode="json"))
    return None

def dataset_read(dataset_uuid_or_uid : 'uuid.UUID | str', scope_uuid : 'uuid.UUID | None' = None) -> DatasetRead:
    params = {'dataset_uuid_or_uid' : str(dataset_uuid_or_uid)}
    if scope_uuid is not None:
        params["scope_uuid"] = str(scope_uuid)
    try :
        data = client.get("/dataset/by_uuid_or_alt_uid/", params=params)
    except RequestFailedException as e:
        if e.status_code == 404:
            raise DatasetNotFoundException(e.message) from None
        elif e.status_code == 406:
            raise MultipleDatasetFoundException(e.message) from None
        else : 
            raise e
    return DatasetRead.model_validate(data)

def dataset_read_by_uuid(dataset_uuid : uuid.UUID, scope_uuid : 'uuid.UUID | None' = None) -> DatasetRead:
    params = {"dataset_uuid" : str(dataset_uuid)}
    if scope_uuid is not None:
        params["scope_uuid"] = str(scope_uuid)
    try :
        data = client.get("/dataset/", params=params)
    except RequestFailedException as e:
        if e.status_code == 404:
            raise DatasetNotFoundException(f"Dataset with uuid {dataset_uuid} not found") from None
        raise e
    return DatasetRead.model_validate(data)

def dataset_read_by_alt_uid(dataset_alt_uid : str, scope_uuid : uuid.UUID) -> DatasetRead:
    params = {"dataset_alt_uid" : str(dataset_alt_uid), "scope_uuid" : str(scope_uuid)}
    try: 
        data = client.get("/dataset/by_alt_uid/", params=params)
    except RequestFailedException as e:
        if e.status_code == 404:
            raise DatasetNotFoundException(f"Dataset with alt_uid {dataset_alt_uid} not found") from None
        raise e
    
    return DatasetRead.model_validate(data)
    
def dataset_update(dataset_uuid :uuid.UUID, datasetUpdate : DatasetUpdate) ->  None :
    params = {"dataset_uuid" : str(dataset_uuid)}
    client.patch("/dataset/", json_data=datasetUpdate.model_dump(mode="json"), params=params)

def dataset_search(datasetSearch : DatasetSearch, offset = 0, limit = 100) -> typing.List[DatasetRead]:
    params = {"offset" : offset, "limit" : limit}
    datasets = client.post("/datasets/search/", json_data=datasetSearch.model_dump(mode="json"), params=params)
    return [DatasetRead.model_validate(dataset) for dataset in datasets]

def dataset_attributes(datasetSelection : DatasetSelection) -> typing.List[DatasetRead]:
    attr = client.post("/datasets/attributes/", json_data=datasetSelection.model_dump(mode="json"))
    return attr[0]