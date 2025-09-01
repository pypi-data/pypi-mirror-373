from etiket_client.local.model import FileDeleteQueue
from etiket_client.local.exceptions import FileNotAvailableException
from etiket_client.local.models.file import FileCreate, FileRead, FileUpdate, FileSelect
from etiket_client.local.model import Files

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from etiket_client.local.dao.base import dao_base
from etiket_client.local.dao.dataset import _get_ds_by_uuid, gen_search_helper

from typing import Optional, List
from uuid import UUID

import datetime, os, logging

logger = logging.getLogger(__name__)

class dao_file(dao_base):
    @staticmethod
    def create(fileCreate : FileCreate, session : Session):
        ds = _get_ds_by_uuid(fileCreate.ds_uuid, session)
        file = Files(**fileCreate.model_dump(by_alias=True, exclude=["ds_uuid"]),
                      scope_id=ds.scope.id, dataset_id=ds.id)
        ds.files.append(file)
        ds.search_helper = gen_search_helper(ds)
        ds.modified = datetime.datetime.now(tz=datetime.timezone.utc)
        session.commit()
        return file
        
    @staticmethod
    def read(fileSelect : FileSelect, session : Session):
        files = _get_File_raw(fileSelect.uuid, fileSelect.version_id, session)
        return [FileRead.model_validate(file) for file in files]
        
    @staticmethod
    def update(fileSelect : FileSelect, fileUpdate : FileUpdate, session : Session):
        if not fileSelect.version_id:
            raise ValueError("Please provide a version_id to update the file.")
        file = _get_File_raw(fileSelect.uuid, fileSelect.version_id, session)[0]
        dao_file._update(file, fileUpdate, session)

    @staticmethod
    def delete(fileSelect : FileSelect, session : Session):
        files = _get_File_raw(fileSelect.uuid, fileSelect.version_id, session)
        for file in files:
            if file.local_path is not None:
                # put the file in a delete queue, such that no program currently using the file is interrupted.
                dao_file_delete_queue.add_file(file.local_path, session)
            session.delete(file)
        session.commit()
    
    @staticmethod
    def get_file_by_name(datasetUUID : UUID, name : str, session : Session) -> 'List[Files]':
        ds = _get_ds_by_uuid(datasetUUID, session)
        files = []
        for file in ds.files:
            if file.name == name:
                files.append(file)
        return files
class dao_file_delete_queue(dao_base):
    @staticmethod
    def add_file(file_path : str, session : Session) -> None:
        delete_after = (datetime.datetime.now(tz=datetime.timezone.utc) +
                                    datetime.timedelta(days=5))
        fileToDelete = FileDeleteQueue(local_path=file_path, delete_after=delete_after)
        logger.info("Adding file %s to delete queue.", file_path)
        session.add(fileToDelete)
        session.commit()
    
    @staticmethod
    def clean_files(session : Session):
        stmt = select(FileDeleteQueue).where(FileDeleteQueue.delete_after < datetime.datetime.now(tz=datetime.timezone.utc))
        files = session.execute(stmt).scalars().all()
        for file in files:
            logger.info("Deleting file %s", file.local_path)
            try:
                os.remove(file.local_path)
                session.delete(file)
            except FileNotFoundError:
                logger.warning("File %s not found.", file.local_path)
                session.delete(file)
            except PermissionError:
                logger.warning("I do not have permission to delete the file %s (will try again tomorrow)", file.local_path)
                # set back the delete_after time to 1 day from now.
                delete_after = (datetime.datetime.now(tz=datetime.timezone.utc) +
                                    datetime.timedelta(days=1))
                stmt = update(FileDeleteQueue).where(FileDeleteQueue.local_path == file.local_path).values(delete_after=delete_after)
                session.execute(stmt)

        session.commit()
        
def _get_File_raw(file_uuid : UUID, version : Optional[int], session : Session) -> 'List[Files]':
    try:
        stmt = select(Files).where(Files.uuid == file_uuid)
        if version:
            stmt = stmt.where(Files.version_id == version)
        files = session.execute(stmt).scalars().all()
        if not files : raise Exception
        return files
    except:
        raise FileNotAvailableException

