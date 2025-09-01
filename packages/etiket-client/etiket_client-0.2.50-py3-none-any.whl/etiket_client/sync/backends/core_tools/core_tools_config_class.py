import dataclasses

@dataclasses.dataclass
class CoreToolsConfigData:
    dbname : str
    user : str
    password : str
    host : str = "localhost"
    port : int = 5432