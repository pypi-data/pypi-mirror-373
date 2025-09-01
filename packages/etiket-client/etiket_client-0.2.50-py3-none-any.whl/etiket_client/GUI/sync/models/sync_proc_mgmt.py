from etiket_client.sync.proc import start_sync_agent, kill_sync_agent, is_running_sync_agent

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, QTimer, pyqtSignal

import time
class sync_proc_manager(QObject):
    syncProcChanged = pyqtSignal(name="syncProcChanged")
    _is_active = True
    
    
    def __init__(self, parent: 'QObject | None' = None):
        super().__init__(parent)
        self.__get_state()
        
        self.statusTimer = QTimer()
        self.statusTimer.setInterval(5*1000)
        self.statusTimer.timeout.connect(self.__get_state)
        self.statusTimer.start()

    @pyqtProperty(bool, notify=syncProcChanged)
    def sync_agent_state(self):
        return self._is_active
    
    @pyqtSlot()
    def kill_sync_proc(self):
        kill_sync_agent()
        self._is_active = False
        self.syncProcChanged.emit()
    
    @pyqtSlot()
    def start_sync_proc(self):
        start_sync_agent()
        self._is_active = True
        self.syncProcChanged.emit()
    
    def __get_state(self):
        state =  is_running_sync_agent()
        if state != self._is_active:
            self._is_active = state
            self.syncProcChanged.emit()
