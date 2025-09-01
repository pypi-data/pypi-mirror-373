from etiket_client.local.models.dataset import DatasetUpdate

from typing import Any
class ds_property_mgr:
    def __init__(self, modifiable=False):
        self.modifiable = modifiable

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype = None):
        ds_data_obj = obj._dataset_content
        get_obj = getattr(ds_data_obj, self.name)
        
        def setter(value):
            self.__set__(obj, value)
        
        if isinstance(get_obj, list):
            return ds_list_extension(get_obj, setter)
        if isinstance(get_obj, dict):
            return ds_dict_extension(get_obj, setter)
        
        return getattr(ds_data_obj, self.name)

    def __set__(self, obj, value):
        if self.modifiable == True:
            du = DatasetUpdate(**{self.name : value})
            obj._update_local(du)
        else:
            raise f"{self.name} is immutable."

class ds_list_extension(list):
    def __init__(self, iterable : list, setter):
        super().__init__(iterable)
        self.setter = setter
        
    def __setitem__(self, index, item):
        super().__setitem__(index, item)
        self.setter(self) 

    def insert(self, index, item):
        super().insert(index, item)
        self.setter(self) 

    def append(self, item):
        super().append(item)
        self.setter(self) 

    def extend(self, other):
        super().extend(other)
        self.setter(self)
        
    def remove(self, item):
        super().remove(item)
        self.setter(self)

class ds_dict_extension(dict):
    def __init__(self, dict : dict, setter):
        super().__init__(dict)
        self.setter = setter
        
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.setter(self)
    
    def __delitem__(self, key: Any) -> None:
        super().__delitem__(key)
        self.setter(self)

class ds_file_mgr:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype = None):
        if obj.local_version:
            return getattr(obj.local_version, self.name)
        return getattr(obj.remote_version, self.name)

    def __set__(self, obj, value):
            raise f"{self.name} cannot be altered."
    