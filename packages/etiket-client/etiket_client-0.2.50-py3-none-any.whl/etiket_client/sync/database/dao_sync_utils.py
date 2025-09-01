import uuid, sqlalchemy.exc

from sqlalchemy import update

from etiket_client.exceptions import UpdateSyncDatasetUUIDException
from etiket_client.sync.database.models_db import SyncItemsSQL
from etiket_client.local.database import Session

def updateDatasetUUID(oldDatasetUUID : uuid.UUID,  newDatasetUUID : uuid.UUID):
    try:
        with Session() as session:
            update_stmt = (
                update(SyncItemsSQL)
                .where(SyncItemsSQL.datasetUUID == oldDatasetUUID)
                .values(datasetUUID = newDatasetUUID)
            )

            session.execute(update_stmt)
            session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()
        raise UpdateSyncDatasetUUIDException("Failed to update dataset UUID in the database (unique constraint failed), this is most likely caused by another sync source that is already synchronizing this dataset.") from e