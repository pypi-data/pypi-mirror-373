from etiket_client.local.models.dataset import DatasetRead as DatasetReadLocal, DatasetUpdate, DatasetCreate
from etiket_client.remote.endpoints.models.dataset import DatasetRead as DatasetReadRemote

from etiket_client.local.dao.dataset import dao_dataset
from etiket_client.local.database import Session

from etiket_client.python_api.dataset_model.files import file_manager
from etiket_client.python_api.dataset_model.utility import ds_list_extension, ds_property_mgr

from etiket_client.local.exceptions import DatasetAlreadyExistException

from typing import Optional

import datetime 
# TODO incorporate Schema definition
class dataset_model:
    uuid = ds_property_mgr(modifiable = False)
    alt_uid = ds_property_mgr(modifiable = False)
    collected = ds_property_mgr(modifiable = False)
    name = ds_property_mgr(modifiable = True)
    creator = ds_property_mgr(modifiable = False)
    description = ds_property_mgr(modifiable = True)
    notes = ds_property_mgr(modifiable = True)
    keywords = ds_property_mgr(modifiable = True)
    
    @property
    def tags(self) -> ds_list_extension:
        return self.keywords
    
    @tags.setter
    def tags(self, tags : list[str]):
        self.keywords = tags
    
    ranking = ds_property_mgr(modifiable = True)
    
    scope = ds_property_mgr(modifiable = False)
    attributes = ds_property_mgr(modifiable = True)
    
    def __init__(self, local_dataset : Optional[DatasetReadLocal],
                    remote_dataset : Optional[DatasetReadRemote], verbose = True):
        self._l_ds = local_dataset
        self._r_ds = remote_dataset
        
        self.files = file_manager(self, verbose=verbose)
    
    def __repr__(self) -> str:
        repr_string = f"Contents of dataset :: {self.name}"
        repr_string += "\n" + "="*len(repr_string) + "\n\n"
        repr_string += f"uuid :: {self.uuid}\n"
        if self.alt_uid:
            repr_string += f"Alternative identifier :: {self.alt_uid}\n"
        if self.description:
            repr_string += f"Description :: {self.description}\n"
        repr_string += f"Scope :: {self.scope.name}\n"
        repr_string += f"Ranking :: {self.ranking}\n"
        if self.attributes:
            repr_string += "Data Indentifiers :: \n"
            for k,v in self.attributes.items():
                repr_string += f"\t{k} : {v}\n"
        repr_string += f"Files :: \n{str(self.files)}"
        
        return repr_string
    
    @property
    def _dataset_content(self):
        if self._r_ds:
            if not self._l_ds:
                return self._r_ds
            else:
                if self._l_ds.modified < self._r_ds.modified:
                    return self._r_ds
        return self._l_ds
    
    def _create_local(self):
        if not self._l_ds:
            datasetCreate = DatasetCreate(**self._r_ds.model_dump(exclude=['files', 'scope']),
                                            scope_uuid=self._r_ds.scope.uuid)
            with Session() as session:
                self._l_ds = dao_dataset.create(datasetCreate, session)

    def _update_local(self, datasetUpdate : DatasetUpdate):
        try:
            if not self._l_ds:
                self._create_local()
        except DatasetAlreadyExistException:
            self._l_ds = dao_dataset.read(self.uuid, Session())
        
        if self._r_ds:
            if self._l_ds.modified < self._r_ds.modified :
                model_dump = self._r_ds.model_dump(exclude_none=True, exclude=['files', 'scope'])
                model_dump.update(datasetUpdate.model_dump(exclude_none=True))
                datasetUpdate = DatasetUpdate.model_validate(model_dump)

        with Session() as session:
            datasetUpdate.synchronized = False
            dao_dataset.update(self.uuid, datasetUpdate, session)
            for k,v in datasetUpdate.model_dump(exclude_none=True).items():
                setattr(self._l_ds, k, v)
            setattr(self._l_ds, 'modified', datetime.datetime.now())
