from etiket_client.local.dao.file import dao_file
from etiket_client.local.models.file import FileRead as FileReadLoc, FileCreate,\
    FileStatusLocal, FileSelect, FileType, FileUpdate
from etiket_client.local.database import Session

from etiket_client.remote.endpoints.file import file_read
from etiket_client.remote.endpoints.models.file import FileRead as FileReadRem, FileSelect as FileSelectRem, FileStatusRem
from etiket_client.remote.tools.file_download import file_download

from etiket_client.python_api.dataset_model.utility import ds_file_mgr
from etiket_client.settings.folders import create_file_dir, get_data_dir
from etiket_client.settings.user_settings import user_settings

from dataclasses import dataclass
from typing import List, Optional, Union

import tabulate, os, datetime, uuid, pathlib, datetime, shutil


@dataclass
class FileData:
    local: Optional[FileReadLoc] = None
    remote: Optional[FileReadRem] = None

class file_manager(dict):
    def __init__(self, dataset, verbose):
        self.dataset = dataset
        self.verbose = verbose
        
        file_contents = {}
        files = []
        if self.dataset._l_ds : files += self.dataset._l_ds.files
        if self.dataset._r_ds : files += self.dataset._r_ds.files
        
        for file in files:
            if file.filename not in file_contents.keys():
                file_contents[file.filename] = []
            file_contents[file.filename].append(file)   
        
        for key, data_items in file_contents.items():
            self[key] = file_object(key, dataset, data_items, verbose=self.verbose)
    
    def add_new_file(self, name : str, filename : str, file_path :  Union[str, pathlib.Path], file_type : FileType,
                    file_status : FileStatusLocal = FileStatusLocal.complete, file_generator : str ="unknown", version_id : Optional[int] = None):
        if filename in self.keys():
            raise ValueError(f"File with the name {filename} already exists. Please update the file instead.")

        validate_file_name(filename, file_path)
        
        file_uuid = uuid.uuid4()
        version_id = version_id or generate_version_id()
        expected_path = _clean_up_filepath(self.dataset, file_uuid,version_id, file_path)
        
        self.dataset._create_local()
        with Session() as session:
            fc = FileCreate(name = name, filename=os.path.basename(expected_path), uuid=file_uuid, 
                        creator=user_settings.user_sub, collected=datetime.datetime.now(),
                        file_generator=file_generator, status=file_status,
                        type=file_type, size=os.path.getsize(expected_path),
                        ds_uuid=self.dataset.uuid, version_id=version_id, local_path=expected_path)
            dao_file.create(fc, session)
            new_file_record = dao_file.read(FileSelect(uuid=fc.uuid), session)
            self[filename] = file_object(filename, self.dataset, new_file_record, verbose=self.verbose)
        return self[filename]

    def __repr__(self):
        if len(self) == 0:
            return "No files present in the current dataset."
        else:            
            headers = ["name", "filename", "type", "selected version number (version_id)", "Maximal version number", "Starred", "Hidden"]
            tabular_data = []
            for filename, content in self.items():
                tabular_data.append([content.name, filename, str(content.current.type),
                        f"{content.versions.index(content.current.version_id)} ({content.current.version_id})" , len(content) -1,
                        "Yes" if content.current.model_data.ranking > 0 else "No",
                        "Yes" if content.current.model_data.ranking < 0 else "No"])
            
            message = tabulate.tabulate(tabular_data, headers)
            return message

class file_object:
    def __init__(self, filename, dataset, data_items : List['FileReadLoc | FileReadRem'], verbose):
        self.name = data_items[0].name
        self.filename = filename
        self.dataset = dataset
        self.verbose = verbose
        self.__build(data_items)

    def __build(self, data_items : List['FileReadLoc | FileReadRem']):
        file_version_data = {}
        for file_data in data_items:
            if file_data.version_id not in file_version_data.keys():
                file_version_data[file_data.version_id] = FileData()
            if isinstance(file_data, FileReadLoc):
                file_version_data[file_data.version_id].local = file_data
            else:
                file_version_data[file_data.version_id].remote = file_data
        
        self.__file_versions = {}
        for key, fileData in file_version_data.items():
            self.__file_versions[key] = file_version(self.dataset, fileData, self.verbose)
            
        self.__current_version_id = sorted(self.__file_versions.keys())[-1]
    
    def __rebuild(self):
        files = []
        with Session() as session:
            files += dao_file.read(FileSelect(uuid=self.current.uuid), session)
        try : 
            files += file_read(FileSelectRem(uuid=self.current.uuid))
        except Exception:
            pass
        
        self.__build(files)
    
    def __len__(self):
        return len(self.__file_versions)
    
    @property
    def current(self) -> 'file_version':
        return self.__file_versions[self.__current_version_id]
    
    @property
    def versions(self) -> List[int]:
        return sorted(self.__file_versions.keys())

    # TODO check if this work well!!
    def save_current_file(self):
        with Session() as session:
            fs = FileSelect(uuid=self.current.uuid, version_id = self.current.version_id)
            current_state = dao_file.read(fs, session)[0]
            if current_state.synchronized == False:
                fu = FileUpdate(size=os.path.getsize(self.current.path), status=FileStatusLocal.complete, synchronized=False)
                dao_file.update(fs, fu, session)
            else:
                version_id = generate_version_id()
                file_name = os.path.basename(self.current.path)
                file_dir = create_file_dir(self.dataset.scope.uuid, self.dataset.uuid, self.current.uuid, version_id)
                new_path = f"{file_dir}{file_name}"
                fc = FileCreate(**self.current.model_data.model_dump(exclude=['version_id', "synchronized", "local_path",'collected']), 
                                    ds_uuid=self.dataset.uuid, version_id=version_id,
                                    local_path=new_path, collected=datetime.datetime.now())
                dao_file.create(fc, session)
                os.rename(self.current.path, new_path)
                os.rmdir(os.path.dirname(self.current.path))
                dao_file.delete(fs, session) 
                self.__rebuild()
    
    def update_version_of_current_file(self, new_file_path, version_id : Optional[int] = None):
        with Session() as session:
            new_version_id = version_id or generate_version_id()
            file_path = _clean_up_filepath(self.dataset, self.current.uuid, new_version_id, new_file_path)
            
            fc = FileCreate(**self.current.model_data.model_dump(exclude=['version_id', "synchronized", "local_path", 'collected', 'status']), 
                            ds_uuid=self.dataset.uuid, version_id=new_version_id, status=FileStatusLocal.complete,
                            local_path=file_path, collected=datetime.datetime.now())
            dao_file.create(fc, session)
            self.__rebuild()
    
    def set_version_number(self, version_number : int):
        if version_number >= len(self) or version_number < -1:
            raise ValueError(f"The maximal version number is {len(self)-1}")
        self.__current_version_id = self.versions[version_number]
    
    def set_version_id(self, version_id : int):
        if version_id in self.__file_versions.keys():
            self.__current_version_id = self.__file_versions[version_id].version_id
        else:
            raise ValueError(f"The requested version {version_id} does not exist. (The following versions are available {str(self.__file_versions.keys())}).")
    
    def set_prev_version(self):
        current = self.versions.index(self.current.version_id)
        if current < 0:
            raise ValueError("The current version is the first version of the file.")
        self.set_version_number(current -1)
    
    def set_next_version(self):
        current = self.versions.index(self.current.version_id)
        self.set_version_number(current +1)
    
    def __repr__(self) -> str:
        output = "File object information\n=======================\n"
        output += f"Name : {self.filename}\nSelected File version : {self.current.version_id}\n"
        output += f"File versions ({len(self)}) : \n"
        for version in self.versions:
            if version == self.current.version_id:
                output += f"\t* {version} "
            else:
                output += f"\t  {version} "
            output +=  f"(created on {self.__file_versions[version].collected.strftime('%d/%m/%Y %H:%M:%S')})\n"
        return output
    
class file_version:
    name = ds_file_mgr()
    uuid = ds_file_mgr()
    version_id = ds_file_mgr()
    
    creator = ds_file_mgr()
    collected = ds_file_mgr()
    filename = ds_file_mgr()

    size = ds_file_mgr()
    type = ds_file_mgr()
    ranking = ds_file_mgr()
    status = ds_file_mgr()
    
    def __init__(self, dataset, fileData:FileData, verbose):
        self.dataset = dataset
        self.verbose = verbose
        self.local_version = fileData.local
        self.remote_version = fileData.remote
    
    @property
    def local(self) -> bool:
        if self.local_version:
            return True
        return False

    @property
    def model_data(self):
        if self.local:
            return self.local_version
        return self.remote_version
    
    def _mark_complete(self):
        if self.local:
            with Session() as session:
                fs = FileSelect(uuid = self.local_version.uuid, version_id=self.local_version.version_id)
                fu = FileUpdate(status=FileStatusLocal.complete, synchronized=False)
                dao_file.update(fs, fu, session)
        else:
            raise ValueError("This action can only be performed on a local file.")
        
    @property
    def path(self) -> str:
        if not self.local_version:
            local_path = file_download(self.dataset.scope.uuid, self.dataset.uuid, self.remote_version, self.verbose)

            self.dataset._create_local()
            fc = FileCreate(status=FileStatusLocal.complete, local_path=local_path,
                            synchronized=True, ds_uuid=self.dataset.uuid, 
                            **self.remote_version.model_dump(exclude=["status"]))
            
            with Session() as session:
                dao_file.create(fc, session)
                self.local_version = dao_file.read(FileSelect(**fc.model_dump()), session)[0]
        if self.local_version.status == FileStatusLocal.unavailable or not os.path.exists(self.local_version.local_path):
            local_path = file_download(self.dataset.scope.uuid, self.dataset.uuid, self.remote_version, self.verbose)

            fu = FileUpdate(status=FileStatusLocal.complete, local_path=local_path, synchronized=True)
            with Session() as session:
                dao_file.update(FileSelect(uuid=self.local_version.uuid, version_id=self.local_version.version_id), fu, session)
                self.local_version = dao_file.read(FileSelect(uuid=self.local_version.uuid, version_id=self.local_version.version_id), session)[0]

        return self.local_version.local_path

def validate_file_name(filename : str, file_path : Union[str, pathlib.Path]):
    # validate file_path and file_name
    if isinstance(file_path, str):
        file_path_obj = pathlib.Path(file_path)
    elif isinstance(file_path, pathlib.Path):
        file_path_obj = file_path
    else:
        raise ValueError(f"The file path {file_path} is not a valid path.")
    
    # Check if the provided file_path actually exists and is a file
    if not file_path_obj.exists():
        raise ValueError(f"The file path {file_path} does not exist.")
    if not file_path_obj.is_file():
        raise ValueError(f"The path {file_path} is not a file.")
    
    # Validate filename has a proper suffix
    if not pathlib.Path(filename).suffix:
        raise ValueError(f"The filename {filename} is not valid. Please provide a filename with a suffix.")
    
    if pathlib.Path(filename).suffix != file_path_obj.suffix:
        raise ValueError(f"The filename {filename} and the file path {file_path} have different suffixes. Please provide a filename with the same suffix as the file path.")
        
def generate_version_id(time = None):
    if time:
        return int(time.timestamp()*1000)
    return int(datetime.datetime.now().timestamp()*1000)

def _clean_up_filepath(dataset, file_uuid, version_id, current_path):
    expected_dir = create_file_dir(dataset.scope.uuid, dataset.uuid, file_uuid, version_id)
    expected_path = f"{expected_dir}{os.path.basename(current_path)}"
    
    if not os.path.exists(current_path):
        raise ValueError(f"The given path is invalid or the file might not exist.\nThe give path was : {current_path}")
    
    if pathlib.Path(get_data_dir()) not in pathlib.Path(current_path).parents:
        shutil.copyfile(current_path, expected_path)
    elif pathlib.Path(expected_path) not in pathlib.Path(current_path).parents:
        shutil.move(current_path, expected_path)
    
    # TODO is this wanted behavoir?
    # clear out folder that was created to put the file (if needed).
    current_path_dirname = os.path.dirname(os.path.abspath(current_path))
    if len(os.listdir(current_path_dirname)) == 0:
        os.rmdir(current_path_dirname)
    
    return expected_path