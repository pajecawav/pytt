from typing import Iterable, List, Optional


class Table:
    def __init__(self, ncols: int):
        self._rows: List[List[str]] = []
        self.ncols = ncols
        self.widths = [0] * self.ncols

    def add_row(self, row: List[str]) -> None:
        assert len(row) == self.ncols

        row = [str(col) for col in row]
        self._rows.append(row)

        for i, col in enumerate(row):
            self.widths[i] = max(self.widths[i], len(col))

    @property
    def formatted_rows(self) -> Iterable[str]:
        for row in self._rows:
            line = self.format_row(row, self.widths)
            yield line

    @staticmethod
    def format_row(row: List[str], widths: Optional[List[int]] = None) -> str:
        if widths is None:
            widths = [len(col) for col in row]

        line = sep = ""
        for col, width in zip(row, widths):
            line += f"{sep}{col:<{width}}"
            sep = " "

        return line
