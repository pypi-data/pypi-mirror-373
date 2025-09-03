import pytz
from datetime import datetime



def utc_now() -> datetime:
    return datetime.now(tz=pytz.utc)
