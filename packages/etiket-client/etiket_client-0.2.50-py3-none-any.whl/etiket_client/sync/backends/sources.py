from etiket_client.local.models.scope import ScopeReadWithUsers

from etiket_client.sync.database.dao_sync_items import dao_sync_items
from etiket_client.sync.database.models_db import SyncSourcesSQL
from etiket_client.sync.database.types import SyncSourceStatus, SyncSourceTypes
from etiket_client.sync.database.models_pydantic import sync_source
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources

from etiket_client.sync.base.sync_source_abstract import SyncSourceFileBase, SyncSourceDatabaseBase

from etiket_client.local.database import Session

from typing import Optional, Type, Union

import dataclasses, typing, uuid, importlib


def add_sync_source(name : str, 
                    sync_class : Type[Union[SyncSourceFileBase, SyncSourceDatabaseBase]],
                    sync_config : Type[dataclasses.dataclass],
                    default_scope : Optional[ScopeReadWithUsers] = None):
    if sync_class.MapToASingleScope is True and default_scope is None:
        raise ValueError("This sync source requires a default scope to be specified")
    
    source_type = detect_type(sync_class, sync_config)
    
    with Session() as session:
        syncSource = sync_source(name=name,
                                    type=source_type,
                                    status=SyncSourceStatus.pending,
                                    sync_config_module=sync_config.__module__,
                                    sync_config_name=type(sync_config).__name__,
                                    sync_class_module=sync_class.__module__,
                                    sync_class_name=sync_class.__name__,
                                    config_data=dataclasses.asdict(sync_config),
                                    auto_mapping=not sync_class.MapToASingleScope,
                                    default_scope=default_scope.uuid)
                                
        dao_sync_sources.add_new_source(syncSource, session)


def remove_sync_source(name : str):
    with Session() as session:
        source = dao_sync_sources.read(name, session)
        dao_sync_items.delete_sync_items(source.id, session)
        dao_sync_sources.delete_source(source.id, session)
        
@dataclasses.dataclass  
class SyncSource:
    id : int
    name : str
    type : SyncSourceTypes
    creator : Optional[str]
    sync_class : typing.Type[typing.Union[SyncSourceFileBase, SyncSourceDatabaseBase]]
    sync_config : typing.Type[dataclasses.dataclass]
    default_scope : typing.Optional[uuid.uuid4]

    @staticmethod
    def init_from_sql(sync_src : SyncSourcesSQL):
        if sync_src.sync_class_module is not None:
            module = importlib.import_module(sync_src.sync_config_module)
            sync_config = getattr(module, sync_src.sync_config_name)(**sync_src.config_data)
            module = importlib.import_module(sync_src.sync_class_module)
            sync_class = getattr(module, sync_src.sync_class_name)
        else:
            type_mapping, config_mapping = get_mapping()
            if sync_src.type == SyncSourceTypes.native:
                sync_config = dict()
                sync_class = None
            else:
                sync_config = config_mapping[sync_src.type](**sync_src.config_data)
                sync_class = type_mapping[sync_src.type]
            
        return SyncSource(id = sync_src.id, name = sync_src.name, type = sync_src.type,
                          sync_class = sync_class,
                          sync_config = sync_config,
                          default_scope = sync_src.default_scope,
                          creator = sync_src.creator)


def get_mapping():
    # TODO : This is a temporary solution.
    from etiket_client.sync.backends.quantify.quantify_sync_class import QuantifySync, QuantifyConfigData
    from etiket_client.sync.backends.qcodes.qcodes_sync_class import QCoDeSSync, QCoDeSConfigData
    from etiket_client.sync.backends.core_tools.core_tools_sync_class import CoreToolsSync, CoreToolsConfigData
    from etiket_client.sync.backends.filebase.filebase_sync_class import FileBaseSync, FileBaseConfigData
    from etiket_client.sync.backends.labber.labber_sync_class import LabberSync, LabberConfigData

    type_mapping = {SyncSourceTypes.native : None,
                    SyncSourceTypes.quantify : QuantifySync,
                    SyncSourceTypes.qcodes : QCoDeSSync,
                    SyncSourceTypes.coretools : CoreToolsSync,
                    SyncSourceTypes.fileBase : FileBaseSync,
                    SyncSourceTypes.labber : LabberSync}

    config_mapping = {SyncSourceTypes.native : dict,
                    SyncSourceTypes.quantify : QuantifyConfigData,
                    SyncSourceTypes.qcodes : QCoDeSConfigData,
                    SyncSourceTypes.coretools : CoreToolsConfigData,
                    SyncSourceTypes.fileBase : FileBaseConfigData,
                    SyncSourceTypes.labber : LabberConfigData}

    return type_mapping, config_mapping

def detect_type(sync_class, sync_config):
    # TODO : This is a temporary solution.
    from etiket_client.sync.backends.quantify.quantify_sync_class import QuantifySync, QuantifyConfigData
    from etiket_client.sync.backends.qcodes.qcodes_sync_class import QCoDeSSync, QCoDeSConfigData
    from etiket_client.sync.backends.core_tools.core_tools_sync_class import CoreToolsSync, CoreToolsConfigData
    from etiket_client.sync.backends.filebase.filebase_sync_class import FileBaseSync, FileBaseConfigData
    from etiket_client.sync.backends.labber.labber_sync_class import LabberSync, LabberConfigData
    sync_type = SyncSourceTypes.custom
    if sync_class == QuantifySync and isinstance(sync_config, QuantifyConfigData):
        sync_type = SyncSourceTypes.quantify
    elif sync_class == QCoDeSSync and isinstance(sync_config, QCoDeSConfigData):
        sync_type = SyncSourceTypes.qcodes
    elif sync_class == CoreToolsSync and isinstance(sync_config, CoreToolsConfigData):
        sync_type = SyncSourceTypes.coretools
    elif sync_class == LabberSync and isinstance(sync_config, LabberConfigData):
        sync_type = SyncSourceTypes.labber
    elif sync_class == FileBaseSync and isinstance(sync_config, FileBaseConfigData):
        sync_type = SyncSourceTypes.fileBase
    
    return sync_type