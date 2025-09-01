from semantic_version import Version

from etiket_client.sync.backends.core_tools.core_tools_config_class import CoreToolsConfigData
from etiket_client.sync.backends.filebase.filebase_sync_class import FileBaseConfigData, FileBaseSync
from etiket_client.sync.backends.sources import add_sync_source, remove_sync_source
from etiket_client.sync.backends.quantify.quantify_config_class import QuantifyConfigData
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources
from etiket_client.sync.database.models_pydantic import sync_source
from etiket_client.sync.database.types import SyncSourceStatus, SyncSourceTypes
from etiket_client.sync.backends.qcodes.qcodes_config_class import QCoDeSConfigData
from etiket_client.python_api.scopes import get_scope_by_uuid, get_scopes

from etiket_client.local.database import Session

from PyQt5.QtCore import pyqtSlot, QAbstractListModel, Qt, QUrl, QTimer, QModelIndex

import pathlib, dataclasses, sys, uuid, datetime

class synchronisation_manager(QAbstractListModel):
    name = Qt.UserRole + 1
    sourceType = Qt.UserRole + 2
    status = Qt.UserRole + 3
    item_remaining = Qt.UserRole + 4
    total_items = Qt.UserRole + 5
    SourceInfo = Qt.UserRole + 6
    LastUpdate = Qt.UserRole + 7
    items_failed = Qt.UserRole + 8
    items_skipped = Qt.UserRole + 9
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = self.__get_data()
        self.scopes = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, QModelIndex, role):
        row = QModelIndex.row()
        if role == self.name:
            return self._data[row].name
        if role == self.sourceType:
            return self._data[row].type.name
        if role == self.status:
            return self._data[row].status.name
        if role == self.item_remaining:
            return self._data[row].items_total - self._data[row].items_synchronized - self._data[row].items_failed - self._data[row].items_skipped
        if role == self.total_items:
            return self._data[row].items_total
        if role == self.items_failed:
            return self._data[row].items_failed
        if role == self.items_skipped:
            return self._data[row].items_skipped
        if role == self.LastUpdate:
            return self._data[row].last_update.strftime("%d/%m/%Y %H:%M")
        if role == self.SourceInfo:
            if self._data[row].type == SyncSourceTypes.coretools:
                return f"Host : {self._data[row].config_data['host']}:{self._data[row].config_data['port']} \n\n\
Database : {self._data[row].config_data['dbname']} \n\n\
Scope Mapping : auto"
            elif self._data[row].type == SyncSourceTypes.qcodes:
                return f"Database : {self._data[row].config_data['database_directory']} \n\n\
Set-up : {self._data[row].config_data['set_up']} \n\n\
Scope : {self.find_scope_name(self._data[row].default_scope)} \n\n"
            elif self._data[row].type == SyncSourceTypes.quantify:
                return f"Quantify Directory : {self._data[row].config_data['quantify_directory']} \n\n\
Set-up : {self._data[row].config_data['set_up']} \n\n\
Scope : {self.find_scope_name(self._data[row].default_scope)} \n\n"
            elif self._data[row].type == SyncSourceTypes.native:
                return f"Native source, no sync settings needed."
            else:
                source_info = ""
                try:
                    for key, value in self._data[row].config_data.items():
                        source_info += f"{key} : {value}\n\n"
                    if self._data[row].default_scope:
                        source_info += f"Scope : {self.find_scope_name(self._data[row].default_scope)}"
                except Exception as e:
                    print(f"Error while trying to get source info : {e}")
                return source_info
    def __get_data(self):
        with Session() as session:
            data_sources = []
            try:
                data_sources = dao_sync_sources.read_sources(session)
            except Exception as e:
                print(f'something went wrong :: {e}')
                
        return data_sources

    def roleNames(self):
        return {
            Qt.UserRole + 1: b'name',
            Qt.UserRole + 2: b'sourceType',
            Qt.UserRole + 3: b'status',
            Qt.UserRole + 4: b'item_remaining',
            Qt.UserRole + 5: b'total_items',
            Qt.UserRole + 6: b'SourceInfo',
            Qt.UserRole + 7: b'LastUpdate',
            Qt.UserRole + 8: b'items_failed',
            Qt.UserRole + 9: b'items_skipped',
        }
    
    @pyqtSlot(int)
    def remove(self, index):
        try:
            with Session() as session:
                remove_sync_source(self._data[index].name)
            self.beginRemoveRows(QModelIndex(), index, index)
            self._data = self.__get_data()
            self.endRemoveRows()
        except Exception as e:
            print(f"Failed to remove source {self._data[index].name} :: {e}")
        
    def update_data(self):
        current_len = len(self._data)
        new_data = self.__get_data()
        new_len = len(new_data)

        if new_len > current_len:
            self.beginInsertRows(QModelIndex(), current_len, new_len - 1)
            self._data = new_data
            self.endInsertRows()
        elif new_len < current_len:
            self.beginRemoveRows(QModelIndex(), new_len, current_len - 1)
            self._data = new_data
            self.endRemoveRows()
        else:
            self._data = new_data

        self.dataChanged.emit(
            self.index(0, 0),
            self.index(new_len - 1, 0),
            [self.name, self.sourceType, self.status, self.item_remaining, self.total_items, self.SourceInfo, self.LastUpdate, self.items_failed, self.items_skipped]
        )
    
    @pyqtSlot(str, str, str, str, result = str)
    def evaluateQCodesData(self, name, set_up, scope_uuid, path):
        errorstring = ""

        try:
            path = format_qml_path(path)
        except Exception as e:
            errorstring = f"An error occured while trying to parse the path.\n Error : {str(e)} \n"

        for data in self.__get_data():
            if data.name == name:
                errorstring = f"The name '{name}' already exists.\n"
            if data.type is SyncSourceTypes.qcodes:
                if data.config_data['database_directory'] == str(pathlib.Path(path)):
                    errorstring = f"Already added the database '{path}'.\n"

        if not path.name.endswith(".db"):
            errorstring += f"Please provide a valid SQL file."
        
        if scope_uuid == "":
            errorstring += "Please select a scope."
        
        if errorstring == "":
            with Session() as session:
                qcodesConfig = QCoDeSConfigData(database_directory=pathlib.Path(path),
                                                set_up=set_up)
                syncSource = sync_source(name=name,
                                        type=SyncSourceTypes.qcodes,
                                        status=SyncSourceStatus.pending,
                                        config_data=dataclasses.asdict(qcodesConfig), 
                                        default_scope=scope_uuid,
                                        auto_mapping=False)
                dao_sync_sources.add_new_source(syncSource, session)
        return errorstring

    @pyqtSlot(str, str, str, str, result = str)
    def evaluateQuantifyData(self, name, set_up, scope_uuid, path):
        errorstring = ""
        
        try:
            path = format_qml_path(path)
        except:
            errorstring = "Unable to parse the path, please provide a valid path."

        for data in self.__get_data():
            if data.name == name:
                errorstring = f"The name '{name}' already exists.\n"
            if data.type is SyncSourceTypes.quantify:
                if data.config_data['quantify_directory'] == path:
                    errorstring = f"Quantify directory already added in sync agent : {data.name}.\n"
        
        if scope_uuid == "":
            errorstring += "Please select a scope."

        if errorstring == "":
            with Session() as session:
                quantifyConfig = QuantifyConfigData(quantify_directory=path,
                                                set_up=set_up)
                syncSource = sync_source(name=name,
                                        type=SyncSourceTypes.quantify,
                                        status=SyncSourceStatus.pending,
                                        config_data=dataclasses.asdict(quantifyConfig), 
                                        default_scope=scope_uuid,
                                        auto_mapping=False)
                dao_sync_sources.add_new_source(syncSource, session)
        return errorstring
    
    @pyqtSlot(str, str, str, str, str, str, result = str)
    def evaluateCoreToolsData(self, name, database, user, password, port, host):
        errorstring = ""
        
        try:
            import core_tools
        except ImportError:
            errorstring = "Please install the core_tools package."
        
        if errorstring == "":
            if Version(core_tools.__version__) < Version("1.4.42"):
                errorstring = "Please update the core_tools package to version 1.4.42 or higher."
        
        if errorstring == "":
            for data in self.__get_data():
                if data.type is SyncSourceTypes.coretools:
                    if data.name == name:
                        errorstring = f"The name '{name}' already exists.\n"
                    if data.config_data['dbname'] == database and data.config_data['host'] == host:
                        errorstring = f"Already added the database '{database}' on the host '{host}'.\n"
        
        if errorstring == "":
            # check if it connects.
            cred = CoreToolsConfigData(dbname=database, user=user, password=password, port=int(port), host=host)
            try :
                import psycopg2
                conn = psycopg2.connect(**dataclasses.asdict(cred))
            except Exception as e:
                errorstring = f"{str(e)}"
                
        if errorstring == "":
            # check if the measurements table exists.
            try :
                cur = conn.cursor()
                stmt = "SELECT EXISTS ( SELECT FROM  pg_tables WHERE schemaname = 'public' AND  tablename  = 'global_measurement_overview');"
                cur.execute(stmt)
                res = cur.fetchone()[0]
                cur.close()
                conn.close()
                if res == False:
                    errorstring = f"Can connect to the database, but cannot find tables used by the core-tools software -.-. Please make sure core-tools is set-up on this database."
            except Exception as e:
                errorstring = f"An unexpected error occured.\n Error : {str(e)}"
        
        if errorstring == "":
            with Session() as session:
                PC = CoreToolsConfigData(dbname=database, user=user, password=password, port=port, host=host)
                syncSource = sync_source(name=name,
                                        type=SyncSourceTypes.coretools,
                                        status=SyncSourceStatus.pending,
                                        config_data=dataclasses.asdict(PC), 
                                        auto_mapping=True, default_scope=None)
                dao_sync_sources.add_new_source(syncSource, session)

        return errorstring
    
    @pyqtSlot(str, str, str, str, result = str)
    def evaluateFileBaseSync(self, name : str, scope_uuid : str, path : str, is_NFS : bool):
        errorstring = ""
        
        if path == "" or path == ".":
            errorstring += "Please provide a valid path."
        if errorstring == "":
            try : 
                path = format_qml_path(path)
            except Exception:
                errorstring = "An error occurred while trying to parse the path"
        
        if errorstring == "":
            if scope_uuid == "":
                errorstring += "Please select a scope."
            
        if errorstring == "":
            for data in self.__get_data():
                if data.name == name:
                    errorstring = f"The name '{name}' already exists.\n"
                if data.type is SyncSourceTypes.fileBase:
                    if data.config_data['root_directory'] == path:
                        errorstring = f"Already added the directory '{path}'.\n"
        
        if errorstring == "":
            if not pathlib.Path(path).exists():
                errorstring = f"Directory '{path}' does not exist."
        
        
        if errorstring == "":
            try:
                fileBaseConfig = FileBaseConfigData(root_directory=pathlib.Path(path),
                                                server_folder=is_NFS)
                scope = get_scope_by_uuid(uuid.UUID(scope_uuid))
                add_sync_source(name, FileBaseSync, fileBaseConfig, scope)
            except Exception as e:
                errorstring = f"An error occurred while trying to add the source.\n Error : {e}"
        
        return errorstring

    def find_scope_name(self, scope_uuid):
        if self.scopes is None:
            self.scopes = get_scopes()
        for scope in self.scopes:
            if scope.uuid == scope_uuid:
                return scope.name + " ( uuid : " + str(scope_uuid) + " )"

        return "No scope not found (you might have insufficient permissions)"
    
def format_qml_path(path : str) -> pathlib.Path:
    if sys.platform == 'win32':
        path = path.replace("file:///", "")
    else:
        path = QUrl(path).path()

    path = pathlib.Path(pathlib.Path(path))
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")
    print(f"Path : {path}")
    return path