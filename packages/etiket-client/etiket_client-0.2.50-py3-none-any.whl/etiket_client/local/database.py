from etiket_client.settings.folders import get_sql_url

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from etiket_client.local.model import Base
from etiket_client.sync.database.models_db import SyncBase

import contextlib
from typing import Any, Generator
import os, etiket_client

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute('PRAGMA busy_timeout = 10000'); # Setting a suitable busy timeout of 10s can help mitigate issues where concurrent access to the database leads to lock contention.
    cursor.close()

engine = create_engine(get_sql_url(), echo=False)
Session = sessionmaker(engine)

# # TODO user resources lib!!
with engine.begin() as connection:
    from alembic.config import Config
    from alembic import command

    etiket_client_directory = os.path.dirname(os.path.dirname(etiket_client.__file__))
    alembic_cfg = Config(os.path.join(etiket_client_directory, 'alembic.ini'))
    alembic_cfg.attributes['connection'] = connection
    alembic_cfg.set_main_option("script_location",
                f"{os.path.dirname(etiket_client.__file__)}/local/alembic")
    command.upgrade(alembic_cfg, "head")
    
@contextlib.contextmanager
def get_db_session_context() -> Generator[Any, None, None]:
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()