from dataclasses import field, dataclass
from etiket_client.python_api.schema import get_current_schema
from etiket_client.settings.folders import get_user_data_dir
from etiket_client.settings.user_settings import user_settings
from etiket_client.settings.saver import settings_saver
from typing import Optional

class config_file_descriptor:
    def __get__(self, obj, objtype=None) -> str:
        if user_settings.current_scope is not None:
            schema = get_current_schema().uuid
            return f"{get_user_data_dir()}schema_{schema}_settings.yaml"
        else:
            return f"{get_user_data_dir()}schema_dummy_settings.yaml"
@dataclass
class schema_settings(settings_saver):
    current_schema : Optional[str] = None
    attributes : dict = field(default_factory=lambda:{})
    
    _config_file = config_file_descriptor()