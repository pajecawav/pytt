import math
from datetime import date, timedelta
from typing import List, Tuple

import typer

from pytt.utils import format_duration

TICK = "▇"


def plot(
    data: List[Tuple[date, timedelta]], width: int, tick_symbol: str = TICK
) -> None:
    max_value = max(entry[1] for entry in data)

    block_size = math.ceil(max_value.total_seconds() / width)
    for date_, duration in data:
        typer.echo(f"[{date_}] ", nl=False)
        typer.echo(tick_symbol * round(duration.total_seconds() / block_size), nl=False)
        typer.echo(f" {format_duration(duration)}")
