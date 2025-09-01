from etiket_client.exceptions import NoLoginInfoFoundException
from etiket_client.local.models.file import FileSelect

from etiket_client.local.dao.file import dao_file, dao_file_delete_queue
from etiket_client.local.dao.dataset import dao_dataset
from etiket_client.local.exceptions import DatasetNotFoundException
from etiket_client.remote.client import client, user_settings
from etiket_client.remote.api_tokens import api_token_session
from etiket_client.remote.endpoints.models.types import FileType
from etiket_client.sync.backends.native.sync_agent import run_native_sync
from etiket_client.sync.backends.sources import SyncSource
from etiket_client.sync.base.manifest_mgr import manifest_manager
from etiket_client.sync.base.sync_source_abstract import SyncSourceDatabaseBase
from etiket_client.sync.database.dao_sync_items import dao_sync_items
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources,\
    sync_source_update

from etiket_client.sync.database.models_pydantic import new_sync_item_db, new_sync_item_file, sync_item
from etiket_client.sync.database.types import SyncSourceStatus, SyncSourceTypes
from etiket_client.sync.backends.native.sync_scopes import sync_scopes
from etiket_client.remote.utility import check_internet_connection
from etiket_client.local.database import Session 
from etiket_client.remote.errors import CONNECTION_ERRORS

from setproctitle import setproctitle

import logging, time

logger = logging.getLogger(__name__)


def sync_loop():
    last_sync_time = 0
    scope_sync_interval = 60  # 60 seconds
    user_check_interval = 5  # 5 seconds -- should be captured automatically in most cases.
    running = True
    while running == True:
        try:
            current_time = time.time()
            # try to use API token for this (more robust)
            with api_token_session(user_settings.user_sub):
                with Session() as session:
                    if current_time - last_sync_time >= scope_sync_interval:
                        sync_scopes(session)
                    if current_time - last_sync_time >= user_check_interval:
                        client.check_user_session()
                    last_sync_time = current_time
                    
                    run_sync_iter(session)
        except NoLoginInfoFoundException:
            logger.info("No access token found, waiting for 2 seconds.")
            time.sleep(2)
        except Exception:
            # usually when connection is lost, try again in 10 seconds.
            if check_internet_connection() == True:
                logger.exception('Sync loop broken!')
                time.sleep(1)
            else:
                logger.warning("No connection, waiting for 60 seconds.")
                time.sleep(60)


def run_sync_iter(session):
    n_syncs = 0
    sync_sources_raw = dao_sync_sources.read_sources(session)
    sync_sources = []
    for source in sync_sources_raw:
        try:
            sync_sources.append(SyncSource.init_from_sql(source))
        except Exception as e:
            logger.exception("Failed to initialize sync source %s", source.name)
            continue
    
    dao_file_delete_queue.clean_files(session)
    
    for sync_source in sync_sources:
        if sync_source.type == SyncSourceTypes.native:
            try:
                logger.info("Syncing %s, of type %s", sync_source.name, sync_source.type)
                items_synced = run_native_sync(sync_source, session)
                n_syncs += items_synced
                continue
            except CONNECTION_ERRORS as e:
                raise e
            except Exception as e:
                logger.exception("Failed to sync %s", sync_source.name)
                continue
        else:
            with api_token_session(sync_source.creator):
                try:
                    logger.info("Syncing %s, of type %s", sync_source.name, sync_source.sync_class.SyncAgentName)
                    try:
                        get_new_sync_items(sync_source, session)
                    except Exception as e :
                        ssu = sync_source_update(status=SyncSourceStatus.error)
                        dao_sync_sources.update_status(sync_source.id, ssu, session)
                        raise e                    
                    
                    s_item = dao_sync_items.read_sync_item(sync_source.id, offset = 0, session=session)
                    
                    if s_item is not None:
                        liveDS = sync_source.sync_class.checkLiveDataset(sync_source.sync_config, s_item,
                                                                        dao_sync_items.is_max_priority(sync_source.id, s_item, session)
                                                                        )
                        # this is needed to not get stuck in a loop of live datasets (though not the cleanest way)
                        liveDS_already_tried = check_live_DS_already_tried(s_item, session)
                        if (liveDS is True) and (sync_source.sync_class.LiveSyncImplemented is False or liveDS_already_tried):
                            # assume only one live dataset at a time.
                            s_item = dao_sync_items.read_sync_item(sync_source.id, offset = 1, session=session)
                            liveDS = False
                    
                    if s_item is None:
                        ssu = sync_source_update(status=SyncSourceStatus.synchronized)
                        dao_sync_sources.update_status(sync_source.id, ssu, session)
                        logger.info("No new items to sync from %s.", sync_source.name)
                        continue


                    liveSync_successful = False
                    if liveDS is True:
                        try:
                            logger.info("Syncing live dataset, %s from %s.", s_item.dataIdentifier, sync_source.name)
                            sync_source.sync_class.syncDatasetLive(sync_source.sync_config, s_item)
                            liveSync_successful = True
                            logger.info("Synced live dataset, %s from %s.", s_item.dataIdentifier, sync_source.name)
                            # do not mark as successfull -- upload the final version of the files using the normal sync.
                        except CONNECTION_ERRORS as e:
                            raise e
                        except Exception:
                            logger.exception("Failed to synchronize %s from %s.", s_item.dataIdentifier, sync_source.name)
                                                
                    if liveDS is False or liveSync_successful is True:
                        try:
                            logger.info("Syncing %s from %s.", s_item.dataIdentifier, sync_source.name)                        
                            sync_dataset_normal(sync_source, s_item)
                            
                            try: # remove any dataset caches:
                                dataset_local = dao_dataset.read(s_item.datasetUUID, session)
                                for file in dataset_local.files:
                                    if file.type == FileType.HDF5_CACHE:
                                        fs = FileSelect(uuid=file.uuid, version_id=file.version_id)
                                        dao_file.delete(fs, session)
                            except DatasetNotFoundException:
                                pass
                            except Exception as e:
                                raise e                            
                            
                            n_syncs += 1
                            logger.info("Synced %s from %s.", s_item.dataIdentifier, sync_source.name)

                            dao_sync_items.mark_successful_sync(sync_source.id, s_item.dataIdentifier ,session)
                        except CONNECTION_ERRORS as e:
                            raise e  # do not mark as failed, try again later.
                        except Exception:
                            logger.exception("Failed to synchronize %s from %s.", s_item.dataIdentifier, sync_source.name)
                            dao_sync_items.mark_failed_attempt(sync_source.id, s_item.dataIdentifier,session)   
                    
                    # update statistics and state of the sync source.
                    n_items = dao_sync_items.count_items(sync_source.id, session)
                    n_items_failed = dao_sync_items.count_items_failed(sync_source.id, session)
                    n_items_synced = dao_sync_items.count_items_synchronized(sync_source.id, session)
                    n_items_skipped = dao_sync_items.count_items_not_in_scope(sync_source.id, session)
                    
                    ssu = sync_source_update(status=SyncSourceStatus.synchronizing, 
                                            items_total = n_items,
                                            items_synchronized = n_items_synced,
                                            items_skipped=n_items_skipped,
                                            items_failed=n_items_failed)
                    
                    if n_items == n_items_failed+n_items_skipped+n_items_synced:
                        ssu.status=SyncSourceStatus.synchronized
                        logger.info("Sync source %s is now fully synchronized (failed : %s, skipped %s).", sync_source.name, n_items_failed, n_items_skipped)
                    dao_sync_sources.update_status(sync_source.id, ssu, session)
                except CONNECTION_ERRORS as e:
                    raise e
                except Exception:
                    logger.exception("Failed to sync %s", sync_source.name)
    if n_syncs == 0:
        time.sleep(1)

def get_new_sync_items(sync_source : SyncSource, session):
    if issubclass(sync_source.sync_class, SyncSourceDatabaseBase):
        last_identifier = dao_sync_items.get_last_identifier(sync_source.id, session)
        new_items = sync_source.sync_class.getNewDatasets(sync_source.sync_config, last_identifier)
        logger.info("Found %s new items in remote location, to add to the list of things to synchronize.", len(new_items))
        dao_sync_items.write_sync_items(sync_source.id, new_items, session)
    else:
        current_manifest = dao_sync_items.get_manifest(sync_source.id, session)

        is_NFS = sync_source.sync_config.server_folder if hasattr(sync_source.sync_config, 'server_folder') else False
        manifest_mgr = manifest_manager(sync_source.name, sync_source.sync_class.rootPath(sync_source.sync_config),
                                            current_manifest, level = sync_source.sync_class.level,
                                            is_NFS=is_NFS, is_single_file=sync_source.sync_class.is_single_file)
        
        new_manifests = manifest_mgr.get_updates()
        
        logger.info("Found %s new datasets (file base), will add these in the sync queue.", len(new_manifests))
        new_sync_items = []
        for identifier, priority in new_manifests.items():
            new_sync_items.append(new_sync_item_file(dataIdentifier=identifier, syncPriority=priority))
        dao_sync_items.write_sync_items(sync_source.id, new_sync_items, session)

def sync_dataset_normal(sync_source : SyncSource, s_item : sync_item):
    if issubclass(sync_source.sync_class, SyncSourceDatabaseBase):
        sync_source.sync_class.syncDatasetNormal(sync_source.sync_config, s_item)
    else:
        manifest_mgr = manifest_manager(sync_source.name)

        manifest_before =  manifest_mgr.get_last_change(s_item.dataIdentifier)
        sync_source.sync_class.syncDatasetNormal(sync_source.sync_config, s_item)
        manifest_after = manifest_mgr.get_last_change(s_item.dataIdentifier)
        if manifest_before != manifest_after:
            manifest_mgr.push_update(s_item.dataIdentifier, manifest_after)
        
def check_live_DS_already_tried(s_item : sync_item, session):
    try:
        dataset = dao_dataset.read(s_item.datasetUUID, session)
        for file in dataset.files:
            if file.type == FileType.HDF5_CACHE:
                return True
    except DatasetNotFoundException:
        return False
    return False


if __name__ == '__main__':
    import etiket_client
    from etiket_client.settings.logging import set_up_sync_logger
    
    logger = set_up_sync_logger(etiket_client.__name__)
    
    try: 
        setproctitle('Python qdrive sync')
    except Exception:
        logger.exception("Failed to set process title.")
    
    sync_loop()