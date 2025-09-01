import typing, sqlite3, qcodes as qc, os, logging

from datetime import datetime

from etiket_client.sync.base.sync_source_abstract import SyncSourceDatabaseBase
from etiket_client.sync.base.sync_utilities import file_info, sync_utilities,\
    dataset_info, sync_item, new_sync_item_db, FileType
from etiket_client.sync.backends.qcodes.real_time_sync import QCoDeS_live_sync
from etiket_client.sync.backends.qcodes.qcodes_config_class import QCoDeSConfigData
from etiket_client.sync.backends.utility.extract_metadata_from_QCoDeS import extract_labels_and_attributes_from_snapshot, MetaDataExtractionError

from qcodes.dataset import load_by_id
from qcodes.dataset.data_set import DataSet

logger = logging.getLogger(__name__)

class QCoDeSSync(SyncSourceDatabaseBase):
    SyncAgentName = "QCoDeS"
    ConfigDataClass = QCoDeSConfigData
    MapToASingleScope = True
    LiveSyncImplemented = True
    
    @staticmethod
    def getNewDatasets(configData: QCoDeSConfigData, lastIdentifier: str) -> 'typing.List[new_sync_item_db] | None':
        if not os.path.exists(configData.database_directory):
            raise FileNotFoundError(f"Database file not found at {configData.database_directory}")
        
        qc.config.core.db_location = str(configData.database_directory)
        
        newSyncIdentifiers = []
        
        with sqlite3.connect(configData.database_directory) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            if not lastIdentifier:
                lastIdentifier = 0         
            
            get_newer_guid_query = """SELECT run_id FROM runs
                                      WHERE run_id > ? ORDER BY run_id ASC"""
            
            cursor = conn.cursor()
            cursor.execute(get_newer_guid_query, (int(lastIdentifier),))
            rows = cursor.fetchall()
            
            newSyncIdentifiers += [new_sync_item_db(dataIdentifier=str(row[0])) for row in rows]
        return newSyncIdentifiers
    
    @staticmethod
    def checkLiveDataset(configData: QCoDeSConfigData, syncIdentifier: sync_item, maxPriority: bool) -> bool:
        if maxPriority is False:
            return False
            
        ds_qc = load_by_id(int(syncIdentifier.dataIdentifier))
        return not ds_qc.completed
    
    @staticmethod
    def syncDatasetNormal(configData: QCoDeSConfigData, syncIdentifier: sync_item):
        ds_qc = create_ds_from_qcodes(configData, syncIdentifier, False)
        ds_xr = ds_qc.to_xarray_dataset()
        
        created_time = datetime.fromtimestamp(ds_qc.run_timestamp_raw)
        
        f_info = file_info(name = 'measurement', fileName = 'measured_data.hdf5',
                           fileType= FileType.HDF5_NETCDF,
                           created = created_time, file_generator = "QCoDeS")
        sync_utilities.upload_xarray(ds_xr, syncIdentifier, f_info)

    @staticmethod
    def syncDatasetLive(configData: QCoDeSConfigData, syncIdentifier: sync_item):
        create_ds_from_qcodes(configData, syncIdentifier, True)
        QCoDeS_live_sync(int(syncIdentifier.dataIdentifier), str(configData.database_directory), syncIdentifier.datasetUUID)

def create_ds_from_qcodes(configData: QCoDeSConfigData, syncIdentifier: sync_item, live : bool) -> DataSet:
    ds_qc = load_by_id(int(syncIdentifier.dataIdentifier))

    collected_time = datetime.fromtimestamp(ds_qc.run_timestamp_raw)
    
    ranking = 0
    if 'inspectr_tag' in ds_qc.metadata.keys():
        if ds_qc.metadata['inspectr_tag']=='star': ranking=1
        if ds_qc.metadata['inspectr_tag']=='cross': ranking=-1
        
    # get variable names in the dataset, this is handy for searching!
    ds_xr = ds_qc.to_xarray_dataset()
    keywords = set()
    try:
        for key in ds_xr.keys():
            if 'long_name' in ds_xr[key].attrs.keys():
                keywords.add(ds_xr[key].attrs['long_name'])
                continue
            if 'name' in ds_xr[key].attrs.keys():
                keywords.add(ds_xr[key].attrs['name'])

        for key in ds_xr.coords:
            if 'long_name' in ds_xr[key].attrs.keys():
                keywords.add(ds_xr[key].attrs['long_name'])
                continue
            if 'name' in ds_xr[key].attrs.keys():
                keywords.add(ds_xr[key].attrs['name'])
    except Exception:
        pass
    
    name_lines = ds_qc.name.splitlines()
    name = name_lines[0] if name_lines else ""

    additional_description = "\n".join(name_lines[1:]) if len(name_lines) > 1 else ""
    description = f"database : {os.path.basename(configData.database_directory)} | run ID : {ds_qc.run_id} | GUID : {ds_qc.guid} | exp name : {ds_qc.exp_name}"
    
    if additional_description:
        description += f"\n\n{additional_description}"
    
    attributes = {"sample" : ds_qc.sample_name,
                    "set-up" : configData.set_up}
    attributes.update(configData.extra_attributes) 
    
    try: # experimental
        extra_labels, extra_attributes = extract_labels_and_attributes_from_snapshot(ds_qc.snapshot)
    except MetaDataExtractionError:
        logger.exception("Could not extract labels and attributes from snapshot.")
        extra_labels = []
        extra_attributes = {}
    keywords.update(extra_labels)
    attributes.update(extra_attributes)   
    
    ds_info = dataset_info(name = name, datasetUUID = syncIdentifier.datasetUUID,
                alt_uid = ds_qc.guid, scopeUUID = syncIdentifier.scopeUUID,
                created = collected_time, keywords = list(keywords),  description = description,
                ranking=ranking, creator=syncIdentifier.creator,
                # exp_name not added, since some people use it to name their experiments ...
                attributes = attributes)
    sync_utilities.create_or_update_dataset(live, syncIdentifier, ds_info)
    return ds_qc
    