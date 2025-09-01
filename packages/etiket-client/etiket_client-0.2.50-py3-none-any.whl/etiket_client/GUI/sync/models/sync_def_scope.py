from etiket_client.python_api.scopes import get_scopes

from PyQt5.QtCore import QAbstractListModel, Qt, pyqtSlot, pyqtProperty

# TODO get scopes once on a while in case they are updated on the server?
class sync_def_scope(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_index = -1
        self._scopes = []

    @pyqtSlot(result=int)
    def currentIndex(self):
        self.__get_scopes()
        return self._selected_index
    
    def rowCount(self, parent=None):
        return len(self._scopes)

    def data(self, index, role):
        self.__get_scopes()
        return self._scopes[index.row()].name

    def __get_scopes(self, reset = False):
        if (not self._scopes or reset == True):
            self._scopes = get_scopes()
            self._selected_index = -1
    
    # TODO move to separte sync class later...
    @pyqtSlot(int, result=str)
    def uuid_from_index(self, index):
        if index < 0:
            return ""
        scope = self._scopes[index]
        return str(scope.uuid)
    
    def roleNames(self):
        return {Qt.UserRole + 1: b'scope_name',}

    @pyqtSlot()
    def rebuild(self):
        self.reset_data(None)
    
    def reset_data(self, _):
        self.beginResetModel()
        self.__get_scopes(reset=True)
        self.endResetModel()