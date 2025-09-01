from etiket_client.local.dao.user import dao_user
from etiket_client.remote.authenticate import _is_logged_in, login_legacy, login_using_sso, logout, get_auth_methods
from etiket_client.remote.utility import check_internet_connection
from etiket_client.settings.user_settings import user_settings
from etiket_client.GUI.sync.models.helpers.pyqt_tcp_handler import TCP_auth_code_handler
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty, QTimer, QVariant, Qt, QAbstractListModel

from etiket_client.local.database import Session

import logging

logger = logging.getLogger(__name__)

class login_manager(QObject):
    loginChanged = pyqtSignal(name="loginChanged")
    institutionsChanged = pyqtSignal()
    _is_loggedIn = False
    _is_online = False
    
    def __init__(self, parent: 'QObject | None' = None):
        super().__init__(parent)
        
        self._is_online = check_internet_connection()
        
        if not self._is_online:
            raise Exception("Host is offline. Please check your internet connection.")
        if self._is_online:
            self.auth_methods = get_auth_methods()
            self._is_loggedIn = _is_logged_in()

            self.login_status_timer = QTimer()
            self.login_status_timer.setInterval(5*1000)
            self.login_status_timer.timeout.connect(self.__check_state)
            self.login_status_timer.start()        
    
    @pyqtProperty(bool, notify=loginChanged)
    def loggedIn(self):
        return self._is_loggedIn

    @pyqtProperty(QVariant, notify=institutionsChanged)
    def institutions(self):
        return list(self.auth_methods.keys())
    
    @pyqtSlot(result = str)
    def getCurrentUser(self):
        with Session() as session:
            user = dao_user.read(user_settings.user_sub, read_scopes=False, session=session)
        return user.firstname

    @pyqtSlot(str, str, str, result=bool)
    def login(self, username, password, institution):
        try:
            login_legacy(username, password, self.auth_methods[institution].server_url)
            self.change_state(True)
            return True
        except Exception as e:
            print("Login in failed. Please try again.")
            print(e)
            return False
    
    @pyqtSlot(int, str, result=bool)
    def login_sso(self, auth_provider_id : int, institution : str):
        try:
            login_using_sso(self.auth_methods[institution].openid_providers[auth_provider_id],
                            self.auth_methods[institution].server_url, 
                            TCP_auth_code_handler)
            self.change_state(True)
            return True
        except Exception as e:
            print("Login in failed. Please try again.")
            print(e)
            import traceback
            traceback.print_exc()
            return False
        
    def __check_state(self):
        try:
            is_logged_in = _is_logged_in()
            # Update the login state if it has changed
            if is_logged_in != self._is_loggedIn:
                self._is_loggedIn = is_logged_in
                self.loginChanged.emit()
        except Exception:
            pass
    
    def change_state(self, _is_loggedIn):
        if self._is_loggedIn == _is_loggedIn:
            return
        self._is_loggedIn = _is_loggedIn
        self.loginChanged.emit()
    
    @pyqtSlot()
    def logout(self):
        logout()
        self.change_state(False)

class auth_option:
    def __init__(self, institution, auth_provider_name, auth_provider_id, is_legacy_login):
        self.institution = institution
        self.auth_provider_id = auth_provider_id
        self.auth_provider_name = auth_provider_name
        self.is_legacy_login = is_legacy_login

class auth_option_list(QAbstractListModel):
    institution = Qt.UserRole + 1
    auth_provider_name = Qt.UserRole + 2
    auth_provider_id = Qt.UserRole + 3
    is_legacy_login = Qt.UserRole + 4
    
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self.institution = None
        self.auth_methods = get_auth_methods()
        
    @pyqtSlot(str)
    def set_institution_data(self, institution : str):
        self.institution = institution
        
        self.beginResetModel()
        data = []
        
        if institution:
            for i, open_id_provider in enumerate(self.auth_methods[institution].openid_providers):
                data.append(auth_option(self.institution, open_id_provider.name, i, False))
            
            if self.auth_methods[institution].allow_password_flow:
                data.append(auth_option(self.institution, "QHarbor login", -1, True))
        
        self._data = data
        self.endResetModel()
    
    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role):
        row = index.row()
        if role == auth_option_list.institution:
            return self._data[row].institution
        elif role == auth_option_list.auth_provider_name:
            return self._data[row].auth_provider_name
        elif role == auth_option_list.auth_provider_id:
            return self._data[row].auth_provider_id
        elif role == auth_option_list.is_legacy_login:
            return self._data[row].is_legacy_login
    
    def roleNames(self):
        return {
            Qt.UserRole + 1: b'institution',
            Qt.UserRole + 2: b'auth_provider_name',
            Qt.UserRole + 3: b'auth_provider_id',
            Qt.UserRole + 4: b'is_legacy_login',
        }