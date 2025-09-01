from etiket_client.settings.folders import get_user_data_dir
from etiket_client.settings.saver import settings_saver

from typing import ClassVar

import dataclasses

@dataclasses.dataclass
class user_settings(settings_saver):
    user_sub : str = None
    
    SERVER_URL : str = None
    open_id_config : dict = None
    client_id : str = None
    token : dict = None
    api_token : str = None
    
    verbose : bool = True
    last_version_check : int = None
	
    current_scope : str = None
    default_attributes : dict = None

    sync_PID : int = None

    _config_file : ClassVar[str] =  f"{get_user_data_dir()}settings.yaml"
    
user_settings.load()