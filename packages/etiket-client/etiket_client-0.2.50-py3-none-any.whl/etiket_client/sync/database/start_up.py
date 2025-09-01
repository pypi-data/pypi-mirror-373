from etiket_client.exceptions import SyncSourceNotFoundException
from etiket_client.sync.database.models_pydantic import sync_source
from etiket_client.sync.database.dao_sync_sources import dao_sync_sources
from etiket_client.sync.database.types import SyncSourceTypes
from etiket_client.local.database import Session

def start_up():
    # create native sync source if it doesn't exist
    with Session() as session:
        ss = sync_source(name="native data", type=SyncSourceTypes.native,
                                config_data={}, auto_mapping=True,
                                default_scope=None)
        try:
            dao_sync_sources.read(ss.name, session)
        except SyncSourceNotFoundException:
            dao_sync_sources.add_new_source(ss, session)