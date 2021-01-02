from datetime import date, datetime, timedelta
from typing import Optional


def parse_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0)


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %a %H:%M")


def format_range(start: datetime, end: Optional[datetime] = None) -> str:
    start_str = format_datetime(start)
    if end is None:
        return f"[{start_str}]"
    end_str = format_datetime(end)
    return f"[{start_str}]--[{end_str}]"


def format_duration(duration: timedelta) -> str:
    hours = int(duration.total_seconds()) // 3600
    minutes = (int(duration.total_seconds()) // 60) % 60
    return f"{hours}:{minutes:02}"


def date_to_datetime(date_: date) -> datetime:
    return datetime(year=date_.year, month=date_.month, day=date_.day)
