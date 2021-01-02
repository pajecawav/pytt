import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from pytt.config import DB_PATH
from pytt.utils import date_to_datetime, parse_datetime

conn = sqlite3.connect(DB_PATH)


@dataclass
class Entry:
    id: int
    start: datetime
    end: Optional[datetime] = None
    description: str = ""

    def __init__(
        self,
        id: int,
        start: Union[datetime, str],
        end: Union[datetime, str] = None,
        description: str = "",
    ):
        self.id = id
        self.description = description

        if isinstance(start, str):
            self.start = parse_datetime(start)
        else:
            self.start = start

        if end is not None and isinstance(end, str):
            self.end = parse_datetime(end)
        else:
            self.end = end

    @property
    def duration(self) -> timedelta:
        end = self.end or datetime.now()
        return end - self.start


def regexp(expr: str, item: str) -> bool:
    return re.search(expr, item, re.IGNORECASE) is not None


def init_db() -> None:
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS entries
                (id INTEGER PRIMARY KEY,
                start DATETIME NOT NULL,
                end DATETIME,
                description TEXT)"""
    )
    conn.commit()


def create_entry(start: datetime, description: str) -> Entry:
    c = conn.cursor()
    c.execute(
        "INSERT INTO entries(start, description) VALUES (?, ?)",
        (start, description),
    )
    conn.commit()
    return Entry(id=c.lastrowid, start=start, description=description)


def end_entry() -> None:
    end = datetime.now()
    c = conn.cursor()
    c.execute("UPDATE entries SET end = ? WHERE end IS NULL", (end,))
    conn.commit()


def get_entries(
    *,
    regex: Optional[str] = None,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Entry]:

    c = conn.cursor()
    params: Tuple[Any, ...] = ()

    if regex:
        query = "SELECT * FROM entries WHERE description REGEXP ?"
        params += (regex,)
    else:
        query = "SELECT * FROM entries WHERE 1 = 1"

    if start:
        query += " AND start >= ?"
        params += (start,)
    if end:
        query += " AND end <= ?"
        params += (end,)

    entries = c.execute(query, params).fetchall()

    return [Entry(*entry) for entry in entries]


def get_current() -> Optional[Entry]:
    c = conn.cursor()
    entry = c.execute("SELECT * FROM entries WHERE end IS NULL").fetchone()
    return Entry(*entry) if entry else None


def get_total_by_day(
    start: Optional[date] = None, end: Optional[date] = None
) -> List[Tuple[date, timedelta]]:
    entries = get_entries(start=start, end=end)
    stats: Dict[date, timedelta] = defaultdict(timedelta)

    for entry in entries:
        start = entry.start
        end = entry.end or datetime.now()
        cur_day = entry.start.date()
        next_day = date_to_datetime(cur_day + timedelta(days=1))

        while end > next_day:
            stats[cur_day] += next_day - start
            start, cur_day = next_day, next_day.date()
            next_day = next_day + timedelta(days=1)

        stats[cur_day] += end - start

    return list(stats.items())


conn.create_function("REGEXP", 2, regexp)
