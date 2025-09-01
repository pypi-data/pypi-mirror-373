import uuid 

from etiket_client.local.dao.dataset import dao_dataset, DatasetCreate
from etiket_client.local.database import Session

from etiket_client.remote.endpoints.dataset import dataset_read as dataset_read_remote
from etiket_client.remote.errors import CONNECTION_ERRORS
from etiket_client.local.exceptions import DatasetNotFoundException, DatasetFoundInMultipleScopesException


def dataset_create_raw(datasetCreate : DatasetCreate):
    with Session() as session:
        ds = dao_dataset.create(datasetCreate, session)
    return ds

def dataset_read_raw(dataset_uuid:'uuid.UUID | str', scope_uuid:'uuid.UUID | None' = None):
    local_ds = None
    
    if isinstance(scope_uuid, str):
        scope_uuid = uuid.UUID(scope_uuid)
    
    with Session() as session:
        try :
            local_ds = dao_dataset.read_by_uuid_and_alt_uid(dataset_uuid, scope_uuid,session)
        except DatasetNotFoundException:
            pass
        except Exception as e:
            raise e
    
    try:
        remote_ds = dataset_read_remote(dataset_uuid, scope_uuid)
    except DatasetNotFoundException:
        remote_ds = None
    except CONNECTION_ERRORS:
        print("Unable to connect to the server. Using local data only.")
        remote_ds = None
    except Exception as e:
        raise e
    
    if local_ds is None and remote_ds is None:
        raise DatasetNotFoundException(f"Dataset with uid/uuid {dataset_uuid} not found")

    # if both, check if the scope is the same,
    if local_ds is not None and remote_ds is not None:
        if local_ds.scope.uuid != remote_ds.scope.uuid:
            message = f"Found dataset with uid/uuid {dataset_uuid} in multiple scopes, please specify. \n\tlocal scope : {local_ds.scope_uuid}\n\tremote scope : {remote_ds.scope_uuid}\n"
            raise DatasetFoundInMultipleScopesException(message)
        
    return local_ds, remote_ds