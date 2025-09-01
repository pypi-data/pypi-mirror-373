import enum 

class SyncSourceStatus(str, enum.Enum):
    synchronized = "synchronized"
    synchronizing = "synchronizing"
    pending = "pending"
    error = "error"
    
class SyncSourceTypes(str, enum.Enum):
    native = "native"
    coretools = "Core-tools"
    qcodes = "qCoDeS"
    quantify = "quantify"
    fileBase = "fileBase"
    labber = "labber"
    custom = "custom"
    