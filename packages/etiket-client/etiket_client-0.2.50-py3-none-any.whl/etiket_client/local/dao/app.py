import datetime

from typing import Optional

from etiket_client.local.model import QHarborAppRegister
from etiket_client.local.models.app import AppRegisterRead
from etiket_client.local.types import ProcTypes

from etiket_client.local.database import Session

from sqlalchemy import select

class dao_app_registerer:
    @staticmethod
    def register(version : str, proc_type : ProcTypes, location : str) -> None:
        with Session() as session:
            stmt = select(QHarborAppRegister).where(QHarborAppRegister.type == proc_type)
            stmt = stmt.where(QHarborAppRegister.location == location)
            res = session.execute(stmt).scalar_one_or_none()
            
            if res is None:
                session.add(QHarborAppRegister(type=proc_type, version=version, location=location))
                session.commit()
            else:
                res.version = version
                res.last_session = datetime.datetime.now(tz=datetime.timezone.utc)
                session.commit()
    
    @staticmethod
    def get_dataQruiser_version() -> Optional[AppRegisterRead]:
        with Session() as session:
            stmt = select(QHarborAppRegister).where(QHarborAppRegister.type == ProcTypes.dataQruiser)
            stmt = stmt.order_by(QHarborAppRegister.last_session.desc()).limit(1)
            res = session.execute(stmt).scalar_one_or_none()
            if res is None:
                return None
            return AppRegisterRead.model_dump(res)