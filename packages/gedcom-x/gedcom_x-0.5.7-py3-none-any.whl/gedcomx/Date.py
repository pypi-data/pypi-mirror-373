from typing import Optional
from datetime import datetime, timezone
from dateutil import parser
import time




class DateFormat:
    def __init__(self) -> None:
        pass

class DateNormalization():
    pass        

class Date:
    identifier = 'http://gedcomx.org/v1/Date'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, original: Optional[str],normalized: Optional[DateNormalization] = None ,formal: Optional[str | DateFormat] = None) -> None:
        self.original = original
        self.formal = formal

        self.normalized: DateNormalization | None = normalized if normalized else None
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.original:
            type_as_dict['original'] = self.original
        if self.formal:
            type_as_dict['formal'] = self.formal
        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls,data):
        original = data.get('original',None)
        formal = data.get('formal',None)
        
        return Date(original=original,formal=formal)
        


def date_to_timestamp(date_str: str, assume_utc_if_naive: bool = True, print_definition: bool = True):
    """
    Convert a date string of various formats into a Unix timestamp.

    A "timestamp" refers to an instance of time, including values for year, 
    month, date, hour, minute, second, and timezone.
    """
    # Handle year ranges like "1894-1912" → pick first year
    if "-" in date_str and date_str.count("-") == 1 and all(part.isdigit() for part in date_str.split("-")):
        date_str = date_str.split("-")[0].strip()

    # Parse date
    dt = parser.parse(date_str)

    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc if assume_utc_if_naive else datetime.now().astimezone().tzinfo)

    # Normalize to UTC and compute timestamp
    dt_utc = dt.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    ts = (dt_utc - epoch).total_seconds()

    # Create ISO 8601 string with full date/time/timezone
    full_timestamp_str = dt_utc.replace(microsecond=0).isoformat()

    
    return ts, full_timestamp_str