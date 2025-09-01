import platform
import platformdirs as pd
import os, sys, hashlib


# TODO :: general question, should data and sql by linked to a folder on the system rather than a user folder?

def __get_base_dir():
    if platform.system() == 'Darwin':
        return os.path.expanduser("~/Library/Containers/com.qdrive.dataQruiser/Data/qdrive")
    if platform.system() == 'Linux':
        return os.path.expanduser("~/.dataQruiser/data/qdrive")
    return f"{pd.user_data_dir()}/qdrive"

def get_sql_url():
    path  = f"{__get_base_dir()}/sql/"
    if not os.path.exists(path):
        os.makedirs(path)
    return f"sqlite+pysqlite:///{path}etiket_db.sql"

def get_data_dir():
    path  = f"{__get_base_dir()}/data/"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def create_file_dir(scope_uuid, dataset_uuid, file_uuid, version_id):
    fpath = f'{get_data_dir()}{scope_uuid}/{dataset_uuid}/{file_uuid}/{version_id}/'            
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    return fpath

def get_user_data_dir():
    python_env_path = normalize_path(sys.prefix)
    python_env = hashlib.md5(python_env_path.encode('utf-8')).hexdigest()
    path  = f"{__get_base_dir()}/user_data/{python_env}/"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_log_dir():
    path  = f"{__get_base_dir()}/logs/"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def normalize_path(path_str : str) -> str:
    normalized_path = os.path.normcase(os.path.normpath(path_str))
    
    # Manually convert the drive letter to lowercase for Windows
    if os.name == 'nt' and len(normalized_path) > 1 and normalized_path[1] == ':':
        normalized_path = normalized_path[0].lower() + normalized_path[1:]
    
    return normalized_path