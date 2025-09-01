
from datetime import datetime, timezone
from typing import Optional
from dateutil.parser import isoparse

def convert_time_from_utc_to_local(data_time : Optional[datetime]):
    if data_time is None:
        return None
    return isoparse(data_time).astimezone().replace(tzinfo=None)

def convert_time_from_local_to_utc(data_time : Optional[datetime]):
    if data_time is None:
        return None
    return data_time.astimezone(tz = timezone.utc).isoformat()