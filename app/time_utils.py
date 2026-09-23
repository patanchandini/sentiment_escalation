from datetime import datetime, time, timedelta
from app import config

def is_business_hours(ts: datetime) -> bool:
    if ts.weekday() not in config.BUSINESS_DAYS:
        return False
    return config.BUSINESS_START <= ts.time() < config.BUSINESS_END

def next_business_day(ts: datetime) -> datetime:
    nxt = ts + timedelta(days=1)
    while nxt.weekday() not in config.BUSINESS_DAYS:
        nxt += timedelta(days=1)
    return nxt.replace(hour=config.BUSINESS_START.hour,
                       minute=0, second=0, microsecond=0)

def minutes_since(start: datetime, now: datetime) -> float:
    return (now - start).total_seconds() / 60.0