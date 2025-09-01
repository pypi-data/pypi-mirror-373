from etiket_client.remote.endpoints.models.types import FileStatusLocal, FileType
from etiket_client.settings.user_settings import user_settings
from etiket_client.local.exceptions import DatasetAlreadyExistException,\
    DatasetAltUIDAlreadyExistException, DatasetNotFoundException, MultipleDatasetFoundException

from etiket_client.local.model import Files, Scopes, Datasets, DatasetFTS, DatasetAttr, DsAttrLink
from etiket_client.local.models.dataset import  DatasetCreate, DatasetRead,\
    DatasetUpdate, DatasetSearch, DatasetSelection
    
from etiket_client.local.dao.base import dao_base
from etiket_client.local.dao.scope import _get_scope_raw, dao_scope, _get_user_scope_ids

from etiket_client.local.dao.dataset_utitlity import format_search_query_for_sqlite, process_search_words

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import column, select, func, delete, Date, and_, or_, desc
from sqlalchemy.sql.selectable import Select

from typing import List, Dict, Optional
from uuid import UUID

class dao_dataset(dao_base):
    @staticmethod
    def create(datasetCreate : DatasetCreate, session : Session):
        scope = _get_scope_raw(datasetCreate.scope_uuid, session)
        
        if not dao_dataset._unique(Datasets, Datasets.uuid == datasetCreate.uuid, session):
            raise DatasetAlreadyExistException(datasetCreate.uuid)
        if (datasetCreate.alt_uid is not None and 
            not dao_dataset._unique(Datasets, (Datasets.alt_uid == datasetCreate.alt_uid) & (Datasets.scope_id == scope.id), session)):
                raise DatasetAltUIDAlreadyExistException(datasetCreate.alt_uid)
        
        dataset_db = Datasets(**datasetCreate.model_dump( by_alias=True, exclude=["scope_uuid", "attributes"]),
                      search_helper="")
        dataset_db.search_helper = gen_search_helper(dataset_db)
        
        scope = _get_scope_raw(datasetCreate.scope_uuid, session)
        dataset_db.scope = scope
        
        attr = []
        for k,v in datasetCreate.attributes.items():
            attr += [_get_or_create_attr(k,v, scope, session)]
        
        for a in attr:
            dataset_db.attributes.append(a)
        
        session.add(dataset_db)
        session.commit()
        return DatasetRead.model_validate(dataset_db)
    
    @staticmethod
    def read(ds_uuid : UUID, session : Session) -> DatasetRead:
        dataset_db = _get_ds_by_uuid(ds_uuid, session)
        return DatasetRead.model_validate(dataset_db)
    
    
    @staticmethod
    def read_by_uuid_and_alt_uid(uuid_or_alt_uid : str, scope_uuid : Optional[UUID], session : Session) -> DatasetRead:
        condition = Datasets.alt_uid==str(uuid_or_alt_uid)
        try:
            if not isinstance(uuid_or_alt_uid, UUID):
                uuid_or_alt_uid = UUID(uuid_or_alt_uid)
            condition = condition | (Datasets.uuid == uuid_or_alt_uid)
        except:
            pass
    
        stmt = select(Datasets).where(condition)
        if scope_uuid:
            scope = _get_scope_raw(scope_uuid, session)
            stmt = stmt.where(Datasets.scope_id == scope.id)
        stmt = stmt.options(selectinload(Datasets.files), selectinload(Datasets.attributes))
        
        result = session.execute(stmt).scalars().all()
        if len(result) == 0:
            raise DatasetNotFoundException(uuid_or_alt_uid)
        if len(result) > 1:
            message = "Dataset found in multiple scopes, please specify the scope\n"
            for ds in result:
                message += f"\tScope :: {ds.scope.name} || with uuid == {ds.scope.uuid}\n"
            raise MultipleDatasetFoundException(message)
        
        return DatasetRead.model_validate(result[0])
    
    
    @staticmethod
    def update(ds_uuid : UUID, datasetUpdate : DatasetUpdate, session : Session):
        try: 
            dataset_db = _get_ds_by_uuid(ds_uuid, session)
            dao_dataset._update(dataset_db, datasetUpdate, session,
                                exclude=["attributes"])
            
            dataset_db.search_helper = gen_search_helper(dataset_db)
            
            if datasetUpdate.attributes is not None:
                # Clear current attributes
                attr_id = [attr.id for attr in dataset_db.attributes]
                dataset_db.attributes.clear()
                session.commit()

                # Remove unlinked attributes and assign new attributes
                dao_dataset.__remove_unlinked_attributes(attr_id, session)
                dao_dataset.__assign_attributes(dataset_db, datasetUpdate.attributes, session)
            
            session.commit()
            session.refresh(dataset_db)
            session.commit() 
        except Exception as e:
            session.rollback()
            raise e   
        
    @staticmethod
    def delete(ds_uuid : UUID, session : Session):
        ds = _get_ds_by_uuid(ds_uuid, session)
        attr_id = [attr.id for attr in ds.attributes]
        session.delete(ds)
        session.commit()
        dao_dataset.__remove_unlinked_attributes(attr_id, session)
    
    @staticmethod
    def search(datasetSearch: DatasetSearch, session : Session, offset: Optional[int] = None, limit : Optional[int] = 50):
        scope_ids = dao_dataset.__get_scope_ids(datasetSearch.scope_uuids, session)
        stmt = select(Datasets)
        stmt = stmt.options(selectinload(Datasets.files),
                            selectinload(Datasets.attributes) )

        stmt =dao_dataset.__search(stmt, scope_ids, datasetSearch)
        stmt = stmt.order_by(desc(Datasets.collected))
        stmt = stmt.offset(offset).limit(limit)

        result = session.execute(stmt).scalars()
        return [DatasetRead.model_validate(res) for res in result]
    
    @staticmethod
    def get_distinct_dates(datasetSearch : DatasetSearch, session : Session, offset : Optional[int] = None, limit : Optional[int] = None):
        scope_ids = dao_dataset.__get_scope_ids(datasetSearch.scope_uuids, session)
        
        stmt = select(func.DATE(Datasets.collected))
        stmt = dao_dataset.__search(stmt, scope_ids, datasetSearch)
        stmt = stmt.order_by(Datasets.collected.cast(Date).desc()).offset(offset).limit(limit)

        return session.execute(stmt.distinct()).scalars().all()

    @staticmethod
    def get_attributes(datasetSelection : DatasetSelection, session: Session):
        scope_ids = dao_dataset.__get_scope_ids(datasetSelection.scope_uuids, session)
        valid_ids = dao_dataset.__select_ds_id_from_attr_query(scope_ids, datasetSelection.attributes)
        stmt = select(DatasetAttr.key, DatasetAttr.value).join(DsAttrLink).where(DsAttrLink.dataset_id.in_(valid_ids)).group_by(DatasetAttr.id)
        result = session.execute(stmt).all()

        keys = set([res[0] for res in result])
        out = {key : [] for key in keys}
        
        for res in result:
            out[res[0]].append(res[1])
        
        return out

    @staticmethod
    def get_unsynced_datasets(session : Session):
        stmt = select(Files.dataset_id).where(and_(Files.synchronized == False, Files.status == FileStatusLocal.complete, Files.type != FileType.HDF5_CACHE))
        stmt = stmt.group_by(Files.dataset_id)
        ds_ids = session.execute(stmt).scalars().all()
        
        stmt = select(Datasets.uuid).where(or_(Datasets.synchronized == False, Datasets.id.in_(ds_ids)))
        stmt = stmt.order_by(Datasets.collected)
        return session.execute(stmt).scalars().all()
        
    @staticmethod
    def get_number_of_datasets(session : Session):
        stmt = select(func.count(Datasets.id))
        return session.execute(stmt).scalar_one()
    
    @staticmethod
    def get_scope_uuid_from_ds_uuid(dataset_uuid : UUID, session: Session):
        ds = _get_ds_by_uuid(dataset_uuid, session)
        return ds.scope.uuid
        
    @staticmethod
    def __assign_attributes(model, attributes, session):
        new_attr = []
        for k,v in attributes.items():
            new_attr.append(_get_or_create_attr(k,v, model.scope, session))
        
        for attr in new_attr:
            model.attributes.append(attr)
        
        session.commit()
        
    @staticmethod
    def __remove_unlinked_attributes(attr_id_list : List[int], session : Session):
        to_delete =[]
        for i in attr_id_list:
            stmt = select(func.count("*")).where(DsAttrLink.dataset_attr_id == i)
            if session.execute(stmt).scalar_one() == 0:
                to_delete.append(i)
        session.execute(delete(DatasetAttr).where(DatasetAttr.id.in_(to_delete)))
        session.commit()

    @staticmethod
    def __select_ds_id_from_attr_query(scope_ids: List[int], attr: Optional[Dict[str, List[str]]]):   
        stmt = select(DsAttrLink.dataset_id).join(DatasetAttr).where(DatasetAttr.scope_id.in_(scope_ids))
        if attr:
            where_query = None
            for k,v in attr.items():
                cond = ((DatasetAttr.key == k) & DatasetAttr.value.in_(v))
                if where_query is not None:
                    where_query = where_query | (DatasetAttr.scope_id.in_(scope_ids)) & cond
                else:
                    where_query = cond
            stmt = stmt.where(where_query)

            if len(attr) > 1:
                stmt = stmt.having(func.count('*') >= len(attr))
        
        stmt = stmt.group_by(DsAttrLink.dataset_id)

        return stmt

    @staticmethod
    def __search(stmt : Select, scope_ids : List[int], datasetSearch:DatasetSearch):
        stmt = stmt.where(Datasets.scope_id.in_(scope_ids))

        if datasetSearch.search_query:
            search_query = format_search_query_for_sqlite(datasetSearch.search_query)
            if search_query:
                stmt = stmt.where(column(DatasetFTS.__tablename__).match(search_query))
                stmt = stmt.join(DatasetFTS, DatasetFTS.rowid == Datasets.id)
        
        if datasetSearch.has_notes:
            stmt = stmt.where(Datasets.notes.is_not(None))
        if datasetSearch.start_date:
            stmt = stmt.where(Datasets.collected >= datasetSearch.start_date)
        if datasetSearch.end_date:
            stmt = stmt.where(Datasets.collected <= datasetSearch.end_date)
        if datasetSearch.ranking is not None:
            stmt = stmt.where(Datasets.ranking >= datasetSearch.ranking)
        
        if datasetSearch.attributes:
            valid_ids = dao_dataset.__select_ds_id_from_attr_query(scope_ids, datasetSearch.attributes)
            stmt = stmt.where(Datasets.id.in_(valid_ids))
        
        return stmt

    @staticmethod
    def __get_scope_ids(uuid_list, session):
        if uuid_list:
            scope_ids = [_get_scope_raw(uuid, session, True).id for uuid in uuid_list]
        else:
            scope_ids = [_get_scope_raw(scope.uuid, session, True).id for scope in dao_scope.read_all(username= user_settings.user_sub , session=session)]
        return scope_ids

def gen_search_helper(model : Datasets):
    search_helper = f"{model.name}"
    if model.description: search_helper += f" {model.description}"
    if model.notes: search_helper += f" {model.notes}"

    for kw in model.keywords:
        search_helper += f" {kw}"
    
    file_names = []
    for file in model.files:
        file_names.append(file.filename)
        if not file.filename.startswith(file.name):
            file_names.append(file.name)
    search_helper += " " + " ".join(set(file_names))
    
    for attr in model.attributes:
        search_helper += f" {attr.key} {attr.value}"
    
    return process_search_words(search_helper)

def  _get_ds_by_uuid(uuid : 'UUID | str', session : Session) -> Datasets:    
    stmt = select(Datasets).where(Datasets.uuid == uuid)
    stmt.options(selectinload(Datasets.files), selectinload(Datasets.attributes))
        
    result = session.execute(stmt).scalar_one_or_none()
    if not result:
        raise DatasetNotFoundException(uuid)
    return result

def _get_or_create_attr(key, value, scope : Scopes, session:Session):
    stmt = select(DatasetAttr).where(DatasetAttr.scope_id == scope.id)
    stmt = stmt.where(DatasetAttr.key == key)
    stmt = stmt.where(DatasetAttr.value == value)
    
    result = session.execute(stmt).scalar_one_or_none()

    if result is None:
        return DatasetAttr(key=key, value=value, scope_id = scope.id)
    
    return result