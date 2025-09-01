from etiket_client.remote.endpoints.file import file_read
from etiket_client.remote.endpoints.models.file import FileRead, FileSelect

from etiket_client.remote.endpoints.models.types import FileStatusRem
from etiket_client.settings.folders import create_file_dir

from datetime import datetime
from tqdm import tqdm

import requests, os, logging

logger = logging.getLogger(__name__)

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def file_download(scope_uuid, dataset_uuid, fileRead : FileRead, verbose):
    if fileRead.S3_validity is None:
        raise ValueError("File is not available on the server. The file does not seem to be uploaded yet.")
    
    if fileRead.S3_validity > datetime.now().timestamp() + 3600: # make sure the link is at least valid for 1h
        fileRead = file_read(FileSelect(uuid = fileRead.uuid, version_id=fileRead.version_id))[0]
    
    if fileRead.status != FileStatusRem.secured:
        raise ValueError(f"Cannot download the file, as file is not yet uploaded (status = {fileRead.status}).")
        
    logger.info('Starting downlaod for file with Dataset UUID :: {dataset_uuid}, File UUID :: {fileRead.uuid} and Version_id :: {fileRead.version_id})')
    file_dir = create_file_dir(scope_uuid, dataset_uuid, fileRead.uuid, fileRead.version_id)
    
    file_path = f"{file_dir}{fileRead.filename}"
    
    # TODO remove this when Dart and Python are combined.
    if os.path.isfile(file_path):
        if os.stat(file_path).st_size == fileRead.size:
            logger.warning(f'File already present on harddrive, returning file. ')
            return file_path
        else: 
            # file incomplete -- remove file and redownload.
            logger.warning(f'File already present on harddrive, but with wrong lenght -- removing file. ')
            os.remove(file_path)
            
    logger.info('Starting file download.')
    
    with requests.get(fileRead.S3_link, stream=True) as r:
        r.raise_for_status()
        tot_size = int(r.headers.get('content-length', 0))

        if verbose is True:
            with DownloadProgressBar(total=tot_size, unit='iB', unit_scale=True) as t:
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536): 
                        t.update(len(chunk))
                        f.write(chunk)
        else:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536): 
                    f.write(chunk)
    
    logger.info('File download complete.')
    
    return file_path