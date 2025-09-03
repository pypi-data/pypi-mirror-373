from datetime import datetime
from typing import Union, Optional


def get_datetime_from_data(input_datetime: Union[datetime, str]) -> Optional[datetime]:
    if isinstance(input_datetime, datetime):
        return input_datetime
    elif isinstance(input_datetime, str) and bool(input_datetime):
        try:
            return datetime.fromisoformat(input_datetime)
        except ValueError:
            return None
    return None
