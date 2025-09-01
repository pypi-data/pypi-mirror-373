from etiket_client.settings.user_settings import user_settings
from etiket_client.python_api.scopes import get_scopes

from PyQt5.QtCore import QAbstractListModel, Qt, pyqtSlot, pyqtProperty

class scope_manager(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_index = 0
        self._scopes = []

    @pyqtSlot(result=int)
    def currentIndex(self):
        self.__get_scopes()
        return self._selected_index
    
    @pyqtSlot(int)
    def setCurrentIndex(self, idx : int):
        self._selected_index = idx
        if idx >= 0:
            user_settings.current_scope = str(self._scopes[idx].uuid)
            user_settings.write()
    
    def rowCount(self, parent=None):
        return len(self._scopes)

    def data(self, index, role):
        self.__get_scopes()
        return self._scopes[index.row()].name

    def __get_scopes(self, reset = False):
        if (not self._scopes or
                user_settings.current_scope != str(self._scopes[self._selected_index].uuid) or
                reset == True):
            self._scopes = get_scopes()
            self._selected_index = self.__check_uuid_index(user_settings.current_scope)
                
    def __check_uuid_index(self, uuid):
        for i in range(len(self._scopes)):
            if str(self._scopes[i].uuid) == uuid:
                return i
        
        return -1
    
    # TODO move to separte sync class later...
    @pyqtSlot(int, result=str)
    def uuid_from_index(self, index):
        if index < 0:
            return ""
        scope = self._scopes[index]
        return str(scope.uuid)
    
    @pyqtSlot(result = int)
    def get_initial_index(self):
        return self._selected_index
    
    @pyqtSlot()
    def rebuild(self):
        self.reset_data(None)
    
    def roleNames(self):
        return {Qt.UserRole + 1: b'scope_name',}

    def reset_data(self, _):
        self.beginResetModel()
        self.__get_scopes(reset=True)
        self.endResetModel()