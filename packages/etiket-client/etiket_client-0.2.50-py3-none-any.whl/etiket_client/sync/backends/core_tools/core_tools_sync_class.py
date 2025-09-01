from etiket_client.sync.backends.core_tools.core_tools_config_class import CoreToolsConfigData
from etiket_client.sync.backends.core_tools.data_getters.get_gates import get_gates_formatted
from etiket_client.sync.backends.core_tools.data_getters.get_pulses import get_AWG_pulses
from etiket_client.sync.backends.core_tools.real_time_sync.measurement_sync import live_measurement_synchronizer
from etiket_client.sync.base.sync_source_abstract import SyncSourceDatabaseBase
from etiket_client.sync.base.sync_utilities import file_info, sync_utilities,\
    dataset_info, sync_item, new_sync_item_db, FileType

import typing, time, logging, json


logger = logging.getLogger(__name__)

try:
    import psycopg2
    from core_tools.data.ds.data_set import load_by_id, data_set
    from core_tools.data.ds.ds2xarray import ds2xarray
    from core_tools.data.SQL.connect import SQL_conn_info_local
    from core_tools.data.SQL.SQL_connection_mgr import SQL_database_init
except ImportError:
    logger.warning("Core-tools not installed, will not be able to use core tools sync")


class CoreToolsSync(SyncSourceDatabaseBase):
    SyncAgentName = "core-tools"
    ConfigDataClass = CoreToolsConfigData
    MapToASingleScope = False
    LiveSyncImplemented = True

    @staticmethod
    def getNewDatasets(configData: CoreToolsConfigData, lastIdentifier: str) -> 'typing.List[new_sync_item_db] | None':
        SQL_conn_info_local(configData.host, configData.port, configData.user,
                        configData.password, configData.dbname, True)
        if SQL_database_init.conn_local is not None:
            SQL_database_init.conn_local.close()
        SQL_database_init.conn_local = psycopg2.connect(database=configData.dbname, user=configData.user, password=configData.password,
                                        host=configData.host, port=configData.port)
        logger.info("Connected to core-tools database %s", SQL_database_init.conn_local.info.dbname)
        
        lastIdentifier = 0 if lastIdentifier is None else int(lastIdentifier)

        conn = psycopg2.connect(database=configData.dbname, user=configData.user, password=configData.password,
                                host=configData.host, port=configData.port)
        cur = conn.cursor()
        stmt = "SELECT id, project FROM global_measurement_overview WHERE id > %s ORDER BY id ASC"
        cur.execute(stmt, (lastIdentifier,))
        newSyncIdentifiers = [new_sync_item_db(dataIdentifier = str(row[0]), scopeIdentifier=row[1]) for row in cur.fetchall()]
        logger.info("Found %d new datasets, last id was %d", len(newSyncIdentifiers), lastIdentifier)
        cur.close()
        conn.close()
        
        return newSyncIdentifiers
    
    @staticmethod
    def checkLiveDataset(configData: CoreToolsConfigData, syncIdentifier: sync_item, maxPriority: bool) -> bool:
        if maxPriority is False:
            return False
        
        ds_ct = load_by_id(int(syncIdentifier.dataIdentifier))
        return not ds_ct.completed
    
    @staticmethod
    def syncDatasetNormal(configData: CoreToolsConfigData, syncIdentifier: sync_item):
        ds_ct = create_ds_from_core_tools(configData, syncIdentifier, False)
        pulses, gates = retrieve_metadata(ds_ct)
        ds_xarray = ds2xarray(ds_ct, snapshot='json')
        
        if pulses is not None:
            f_info_pulses = file_info(name = "pulses", fileName = 'pulses.hdf5', fileType= FileType.HDF5_NETCDF,
                                        created = ds_ct.run_timestamp, file_generator = "core-tools")
            sync_utilities.upload_xarray(pulses, syncIdentifier, f_info_pulses)
            
        if gates is not None:
            ds_xarray['gates'] = json.dumps(gates)
        
        f_info = file_info(name = "measurement", fileName = 'measured_data.hdf5', fileType= FileType.HDF5_NETCDF,
                           created = ds_ct.run_timestamp, file_generator = "core-tools")
        sync_utilities.upload_xarray(ds_xarray, syncIdentifier,f_info)
        
    @staticmethod
    def syncDatasetLive(configData: CoreToolsConfigData, syncIdentifier: sync_item):
        ds_ct = create_ds_from_core_tools(configData, syncIdentifier, True)
        
        pulses, _ = retrieve_metadata(ds_ct)
        
        if pulses is not None:
            f_info_pulses = file_info(name = "pulses",
                                        fileName = 'pulses.hdf5',
                                        fileType= FileType.HDF5_NETCDF,
                                        created = ds_ct.run_timestamp, file_generator = "core-tools")
            sync_utilities.upload_xarray(pulses, syncIdentifier, f_info_pulses)


        lms = live_measurement_synchronizer(int(syncIdentifier.dataIdentifier), syncIdentifier.datasetUUID)
        try:
            while lms.is_complete() is not True:
                lms.sync()
                time.sleep(0.2)
        except Exception as e:
            raise e
        finally:
            lms.complete()
        logger.info("Live sync for dataset with id : %s is complete", ds_ct.exp_id)


def retrieve_metadata(ds_ct : 'data_set'):
    pulses = None
    gates = None
    
    if ds_ct.snapshot:  
        pulses = get_AWG_pulses(ds_ct.snapshot)
        gates = get_gates_formatted(ds_ct.snapshot)
    
    return pulses, gates

def create_ds_from_core_tools(configData: CoreToolsConfigData, syncIdentifier: sync_item, live : bool):
    ds_ct = load_by_id(int(syncIdentifier.dataIdentifier))
    logger.info("Loaded dataset with id : %s and ct_uuid : %s", ds_ct.exp_id, ds_ct.exp_uuid)
    description = f'database : {configData.dbname} | id : {ds_ct.exp_id} | ct_uuid : {ds_ct.exp_uuid}'
    
    ds_info = dataset_info(name = ds_ct.name, datasetUUID = syncIdentifier.datasetUUID,
                alt_uid = str(ds_ct.exp_uuid), scopeUUID = syncIdentifier.scopeUUID,
                created = ds_ct.run_timestamp, keywords = ds_ct.keywords, description = description,
                attributes = {"sample" : ds_ct.sample_name, "set-up" : ds_ct.set_up}, creator=syncIdentifier.creator)
    
    sync_utilities.create_ds(live, syncIdentifier, ds_info)
    return ds_ct