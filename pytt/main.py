import time
from datetime import datetime
from enum import Enum
from typing import List

import typer

from pytt import db, plotting
from pytt.table import Table
from pytt.utils import format_duration, format_range

app = typer.Typer()


class Column(str, Enum):
    range = "range"
    duration = "duration"
    description = "description"


DEFAULT_COLUMNS = ["range", "duration", "description"]


@app.command("in", short_help="Start clock.")
def clock_in(
    description: str = typer.Option("", help="Description for an entry."),
    wait: bool = typer.Option(
        False, help="Wait for KeyboardInterrupt or exit right away."
    ),
):
    db.end_entry()
    db.create_entry(start=datetime.now(), description=description)

    if wait:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            db.end_entry()


@app.command("out", short_help="End clock.")
def clock_out():
    db.end_entry()


@app.command("log", short_help="Print log.")
def print_log(
    regex: str = typer.Option(None, help="Show entries that match regex."),
    column: List[Column] = typer.Option(DEFAULT_COLUMNS, help="Columns to print."),
    start: datetime = typer.Option(
        None, help="Starting date.", formats=["%Y-%m-%d", "%Y.%m.%d"]
    ),
    end: datetime = typer.Option(
        None, help="Ending date (exclusive).", formats=["%Y-%m-%d", "%Y.%m.%d"]
    ),
):
    entries = db.get_entries(regex=regex, start=start, end=end)

    table = Table(ncols=len(column))

    for entry in entries:
        columns = {
            Column.range: format_range(entry.start, entry.end),
            Column.duration: format_duration(entry.duration),
            Column.description: entry.description,
        }
        table.add_row([columns[col_name] for col_name in column])

    typer.echo("\n".join(table.formatted_rows))


@app.command("status", short_help="Show current clock.")
def print_status(
    column: List[Column] = typer.Option(DEFAULT_COLUMNS, help="Columns to print."),
):
    entry = db.get_current()

    if entry:
        columns = {
            Column.range: format_range(entry.start, entry.end),
            Column.duration: format_duration(entry.duration),
            Column.description: entry.description,
        }
        line = Table.format_row([columns[col_name] for col_name in column])
        typer.echo(line)
    else:
        typer.echo("No clock started")


def width_callback(value: int):
    if value <= 0:
        raise typer.BadParameter("must be positive")
    return value


@app.command("stats", short_help="Show daily stats.")
def print_stats(
    plot: bool = typer.Option(False, help="Print plot."),
    width: int = typer.Option(35, callback=width_callback, help="Plot width."),
    start: datetime = typer.Option(
        None, help="Starting date.", formats=["%Y-%m-%d", "%Y.%m.%d"]
    ),
    end: datetime = typer.Option(
        None, help="Ending date (exclusive).", formats=["%Y-%m-%d", "%Y.%m.%d"]
    ),
):

    stats = db.get_total_by_day(start=start, end=end)

    if plot:
        plotting.plot(stats, width)
        return

    table = Table(ncols=2)
    for date, duration in stats:
        row = [f"[{date}]", format_duration(duration)]
        table.add_row(row)

    formatted_rows = "\n".join(table.formatted_rows)
    if formatted_rows:
        typer.echo(formatted_rows)


def main() -> None:
    db.init_db()
    app()
    db.conn.close()


if __name__ == "__main__":
    main()
