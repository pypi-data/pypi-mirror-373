from collections import OrderedDict

from rich.console import Console
from rich.table import Column, Table

from biolib.typing_utils import Any, List


class BioLibTable:
    def __init__(self, columns_to_row_map: OrderedDict, rows: List[Any], title):
        self.title = title
        self.rows = rows
        self.columns_to_row_map = columns_to_row_map
        self.table = self._create_table()

    def _create_table(self) -> Table:
        columns = [Column(header=header, **meta['params']) for header, meta in self.columns_to_row_map.items()]
        table = Table(*columns, title=self.title)
        for row in self.rows:
            row_values: List[str] = []
            for column in self.columns_to_row_map.values():
                keys = column['key'].split('.')
                value = row[keys[0]]
                for key in keys[1:]:
                    if not value or key not in value:
                        continue
                    value = value[key]
                row_values.append(str(value))
            table.add_row(*row_values)
        return table

    def print_table(self):
        console = Console()
        console.print(self.table)
