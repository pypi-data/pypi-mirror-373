from etiket_client.local.dao.dataset import dao_dataset, DatasetUpdate as DatasetUpdateLocal
from etiket_client.local.dao.file import dao_file, FileUpdate as FileUpdateLocal
from etiket_client.local.models.file import FileSelect, FileStatusLocal, FileType
from etiket_client.local.exceptions import DatasetNotFoundException

from etiket_client.remote.api_tokens import api_token_session
from etiket_client.remote.endpoints.dataset import dataset_read, dataset_create, dataset_update
from etiket_client.remote.endpoints.file import file_create, file_generate_presigned_upload_link_single

from etiket_client.remote.endpoints.models.dataset import DatasetCreate, DatasetUpdate
from etiket_client.remote.endpoints.models.file import FileCreate, FileRead

from etiket_client.remote.endpoints.models.types import FileStatusRem
from etiket_client.remote.errors import CONNECTION_ERRORS
from etiket_client.sync.database.types import SyncSourceStatus
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources
from etiket_client.sync.database.models_pydantic import sync_source_update
from etiket_client.sync.base.sync_utilities import md5
from etiket_client.sync.uploader.file_uploader import upload_new_file_single
from etiket_client.sync.backends.sources import SyncSource

from sqlalchemy.orm import Session

import logging, typing, uuid

logger = logging.getLogger(__name__)

# TODO refactor to work in the new base class model

def run_native_sync(source : SyncSource, session : Session):
    logger.info("start sync of local datasets")
    unsynced_uuids = dao_dataset.get_unsynced_datasets(session)
    total_items = dao_dataset.get_number_of_datasets(session)    
    
    ssu = sync_source_update(status=SyncSourceStatus.synchronizing, 
                        items_synchronized = total_items - len(unsynced_uuids),
                        items_total = total_items)
    if ssu.items_synchronized == ssu.items_total:
        ssu.status=SyncSourceStatus.synchronized
    dao_sync_sources.update_status(source.id, ssu, session)

    n_syncs = 0
    
    logger.info("synchronizing %s datasets", len(unsynced_uuids))

    for unsynced_uuid in unsynced_uuids:
        try:
            dataset_local = dao_dataset.read(unsynced_uuid, session)
            with api_token_session(dataset_local.creator):
                dataset_remote = None
                logger.info("synchronizing dataset with uuid : %s.", dataset_local.uuid)
                
                try :
                    dataset_remote = dataset_read(dataset_local.uuid, dataset_local.scope.uuid)
                    logger.info("A remote dataset is already present.")
                except DatasetNotFoundException:
                    logger.info("No remote dataset found.")
                except Exception as e:
                    logger.exception("Error reading remote dataset.")
                    raise e
                
                if not dataset_remote:
                    logger.info("Trying to create remote dataset.")
                    dc = DatasetCreate(**dataset_local.model_dump(), scope_uuid=dataset_local.scope.uuid)
                    dataset_create(dc)
                    logger.info("Remote dataset created.")
                    dataset_remote = dataset_read(dataset_local.uuid, dataset_local.scope.uuid)
                    logger.info("dataset read")
                else:
                    if dataset_local.modified > dataset_remote.modified:
                        logger.info("Trying to update field of the remote dataset.")
                        du = DatasetUpdate(**dataset_local.model_dump())
                        dataset_update(dataset_local.uuid, du)
                        logger.info("Fields updated.")
                
                for file in dataset_local.files:
                    if file.status == FileStatusLocal.complete and file.synchronized is False and file.type != FileType.HDF5_CACHE:
                        logger.info("Synchronizing file with name %s, uuid %s and version_id %s", file.name, file.uuid, file.version_id)
                        fs = FileSelect(uuid=file.uuid, version_id=file.version_id)

                        file_remote = get_remote_file(dataset_remote.files, file.uuid, file.version_id)
                        if file_remote:
                            logger.info("File record already present on the remote server, updating details.")
                            # TODO update details.
                            if file_remote.status == FileStatusRem.secured:
                                fu = FileUpdateLocal(synchronized=True, ranking=file.ranking)
                                dao_file.update(fs, fu, session)
                                continue
                        else:
                            logger.info("Creating file record on the remote server.")
                            fc = FileCreate(**file.model_dump(), ds_uuid=dataset_local.uuid)
                            file_create(fc)
                            logger.info("File record created.")
                        
                        
                        logger.info("Starting upload of the file.")
                        upload_info = file_generate_presigned_upload_link_single(file.uuid, file.version_id)
                        md5_checksum = md5(file.local_path)
                        upload_new_file_single(file.local_path, upload_info, md5_checksum)
                        logger.info("Upload finished.")
                    
                        fu = FileUpdateLocal(synchronized=True)
                        dao_file.update(fs, fu, session)
                
                du = DatasetUpdateLocal(synchronized=True)
                dao_dataset.update(dataset_local.uuid, du,session)
                
                current_sync_status = dao_sync_sources.read_source_from_id(source.id, session)
                ssu = sync_source_update(items_synchronized = current_sync_status.items_synchronized + 1)
                dao_sync_sources.update_status(source.id, ssu, session)
            
                logger.info("Dataset Synchronization is successful!")
                n_syncs += 1
        except CONNECTION_ERRORS as e:
            raise e
        except Exception:
            logger.exception("Error occurred during the sync of the dataset.")
                
    ssu = sync_source_update(status=SyncSourceStatus.pending)
    if ssu.items_synchronized == ssu.items_total:
        ssu.status=SyncSourceStatus.synchronized
        logger.info("Done with native uploads. All files are up to date.")
    else:
        logger.info("Done with native uploads, though failed some uploads :/ Will try again later.")
    dao_sync_sources.update_status(source.id, ssu, session)
    return n_syncs

def get_remote_file(files : typing.List[FileRead], file_uuid : uuid.UUID, version_id : int):
    for file in files:
        if file.uuid == file_uuid and file.version_id == version_id:
            return file
    return None